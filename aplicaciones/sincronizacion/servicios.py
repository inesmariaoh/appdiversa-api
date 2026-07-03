"""
Servicios de negocio del motor de sincronizacion offline.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import crear_snapshot_modelo, registrar_auditoria
from aplicaciones.formularios.models import Pregunta
from aplicaciones.respuestas.catalogo_validacion import validar_y_normalizar_valor_catalogo
from aplicaciones.respuestas.excepciones import (
    PreguntaNoExisteError,
    SesionRespuestaNoExisteError,
    ValorInvalidoError,
    ValorNoPerteneceCatalogoError,
)
from aplicaciones.respuestas.mapeo_valores import asignar_valor_a_respuesta
from aplicaciones.respuestas.models import OrigenRespuesta, Respuesta
from aplicaciones.respuestas.selectores import (
    obtener_pregunta_por_codigo_en_version,
    obtener_respuesta,
    obtener_respuesta_por_uuid_local_incluyendo_eliminadas,
)
from aplicaciones.respuestas.validacion_util import extraer_valor_resumen
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima
from aplicaciones.sesiones_anonimas.selectores import obtener_sesion_por_uuid
from aplicaciones.sincronizacion.conflictos import resolver_last_write_wins
from aplicaciones.sincronizacion.constantes import (
    MensajesConflictoApi,
    MensajesSincronizacionApi,
)
from aplicaciones.sincronizacion.excepciones import (
    ChecksumInvalidoError,
    ConflictoNoEncontradoError,
    ResolucionConflictoInvalidaError,
)
from aplicaciones.sincronizacion.models import (
    ConflictoSincronizacion,
    EstadoSincronizacion,
    OperacionSincronizacion,
    ResolucionConflicto,
    TipoConflicto,
)
from aplicaciones.sincronizacion.validadores import validar_checksum_operacion


@dataclass(frozen=True)
class OperacionEntrada:
    """Operacion de sincronizacion recibida desde un dispositivo."""

    uuid_local: UUID
    codigo_pregunta: str
    valor: Any
    version_cliente: int
    fecha_cliente: datetime
    checksum: str = ""


@dataclass(frozen=True)
class ResultadoOperacionSync:
    """Resultado individual de una operacion de sincronizacion."""

    uuid_local: UUID
    estado: str
    mensaje: str | None = None
    respuesta_id: int | None = None


@dataclass(frozen=True)
class ResultadoBatchSync:
    """Resultado agregado de un lote de sincronizacion."""

    operaciones_procesadas: int
    operaciones_actualizadas: int
    duplicadas: int
    conflictos: list[dict[str, Any]]
    errores: list[dict[str, Any]]


def _parsear_fecha_cliente(fecha_cliente: datetime | str) -> datetime:
    """Convierte la fecha del cliente a datetime."""
    if isinstance(fecha_cliente, datetime):
        return fecha_cliente
    valor_normalizado = str(fecha_cliente).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(valor_normalizado)
    except ValueError as error:
        raise ValorInvalidoError() from error


def _extraer_valor_servidor(respuesta: Respuesta) -> Any:
    """Extrae el valor util de una respuesta para comparacion de conflictos."""
    return extraer_valor_resumen(respuesta, respuesta.pregunta.tipo_pregunta)


def _actualizar_actividad_sesion(sesion: SesionAnonima) -> None:
    """Actualiza el estado y marca la sesion como operada sin conexion."""
    sesion.estado = EstadoSesionAnonima.EN_PROCESO
    sesion.fecha_ultima_actividad = timezone.now()
    sesion.fecha_sincronizacion = timezone.now()
    sesion.es_offline = True
    sesion.save(
        update_fields=[
            "estado",
            "fecha_ultima_actividad",
            "fecha_sincronizacion",
            "es_offline",
            "fecha_modificacion",
        ],
    )


def registrar_operacion(
    uuid_sesion: UUID,
    operacion: OperacionEntrada,
    dispositivo: str,
    estado: str,
    origen: str,
    resultado: dict[str, Any] | None = None,
    ultimo_error: str = "",
) -> OperacionSincronizacion:
    """Registra una operacion de sincronizacion en el historial."""
    intentos_previos = OperacionSincronizacion.objects.filter(
        uuid_sesion=uuid_sesion,
        uuid_local=operacion.uuid_local,
    ).count()
    return OperacionSincronizacion.objects.create(
        uuid_local=operacion.uuid_local,
        uuid_sesion=uuid_sesion,
        dispositivo=dispositivo,
        version_cliente=operacion.version_cliente,
        estado=estado,
        fecha_cliente=operacion.fecha_cliente,
        checksum=operacion.checksum,
        origen=origen,
        numero_reintentos=intentos_previos,
        payload={
            "codigo_pregunta": operacion.codigo_pregunta,
            "valor": operacion.valor,
            "version_cliente": operacion.version_cliente,
        },
        resultado=resultado,
        ultimo_error=ultimo_error,
    )


def registrar_conflicto(
    uuid_local: UUID,
    respuesta: Respuesta | None,
    tipo_conflicto: str,
    valor_cliente: Any,
    valor_servidor: Any,
    resolucion: str = "",
) -> ConflictoSincronizacion:
    """Registra un conflicto de sincronizacion y su auditoria."""
    conflicto = ConflictoSincronizacion.objects.create(
        uuid_local=uuid_local,
        respuesta=respuesta,
        tipo_conflicto=tipo_conflicto,
        valor_cliente={"valor": valor_cliente},
        valor_servidor={"valor": valor_servidor},
        resolucion=resolucion,
    )
    registrar_auditoria(
        entidad=ConflictoSincronizacion.__name__,
        entidad_id=str(conflicto.pk),
        accion=AccionAuditoria.CONFLICTO,
        valor_nuevo={
            "uuid_local": str(uuid_local),
            "tipo_conflicto": tipo_conflicto,
            "resolucion": resolucion,
        },
        descripcion="Conflicto detectado en sincronizacion offline.",
    )
    return conflicto


_RESOLUCIONES_VALIDAS = frozenset(
    {
        ResolucionConflicto.CLIENTE,
        ResolucionConflicto.SERVIDOR,
        ResolucionConflicto.MANUAL,
    },
)


def _extraer_valor_conflicto(contenedor: Any) -> Any:
    """Extrae el valor util almacenado en un campo de conflicto."""
    if isinstance(contenedor, dict):
        return contenedor.get("valor")
    return contenedor


def _resolver_valor_a_aplicar(
    conflicto: ConflictoSincronizacion,
    resolucion: str,
    valor_manual: Any,
) -> Any:
    """Determina el valor a aplicar segun la resolucion elegida."""
    if resolucion == ResolucionConflicto.CLIENTE:
        return _extraer_valor_conflicto(conflicto.valor_cliente)
    if resolucion == ResolucionConflicto.MANUAL:
        if valor_manual is None:
            raise ResolucionConflictoInvalidaError(
                MensajesConflictoApi.VALOR_MANUAL_REQUERIDO,
            )
        return valor_manual
    return _extraer_valor_conflicto(conflicto.valor_servidor)


def _aplicar_valor_resolucion(respuesta: Respuesta, valor: Any) -> None:
    """Aplica el valor resuelto a la respuesta asociada al conflicto."""
    pregunta = respuesta.pregunta
    valor_normalizado = validar_y_normalizar_valor_catalogo(pregunta, valor)
    asignar_valor_a_respuesta(respuesta, pregunta.tipo_pregunta, valor_normalizado)
    respuesta.version_respuesta += 1
    respuesta.requiere_sincronizacion = False
    respuesta.esta_eliminado = False
    respuesta.save()
    registrar_auditoria(
        entidad=Respuesta.__name__,
        entidad_id=str(respuesta.pk),
        accion=AccionAuditoria.EDITAR,
        valor_nuevo=crear_snapshot_modelo(respuesta),
        descripcion="Respuesta actualizada por resolucion manual de conflicto.",
    )


@transaction.atomic
def resolver_conflicto(
    conflicto_uuid: UUID,
    resolucion: str,
    valor_manual: Any = None,
) -> ConflictoSincronizacion:
    """Resuelve manualmente un conflicto aplicando el valor elegido a la respuesta."""
    if resolucion not in _RESOLUCIONES_VALIDAS:
        raise ResolucionConflictoInvalidaError(MensajesConflictoApi.RESOLUCION_INVALIDA)

    conflicto = (
        ConflictoSincronizacion.objects.select_related("respuesta", "respuesta__pregunta")
        .filter(uuid=conflicto_uuid)
        .first()
    )
    if conflicto is None:
        raise ConflictoNoEncontradoError()

    aplica_valor = resolucion in (ResolucionConflicto.CLIENTE, ResolucionConflicto.MANUAL)
    if aplica_valor and conflicto.respuesta is None:
        raise ResolucionConflictoInvalidaError(
            MensajesConflictoApi.CONFLICTO_SIN_RESPUESTA,
        )

    if aplica_valor:
        valor = _resolver_valor_a_aplicar(conflicto, resolucion, valor_manual)
        _aplicar_valor_resolucion(conflicto.respuesta, valor)

    conflicto.resolucion = resolucion
    conflicto.save(update_fields=["resolucion"])
    registrar_auditoria(
        entidad=ConflictoSincronizacion.__name__,
        entidad_id=str(conflicto.pk),
        accion=AccionAuditoria.RESOLUCION_CONFLICTO,
        valor_nuevo={
            "uuid_local": str(conflicto.uuid_local),
            "resolucion": resolucion,
        },
        descripcion="Resolucion manual de conflicto de sincronizacion.",
    )
    return conflicto


def validar_idempotencia(
    respuesta: Respuesta | None,
    version_recibida: int,
) -> str:
    """
    Evalua idempotencia por version_cliente.
    Retorna: crear, actualizar, duplicada o conflicto.
    """
    if respuesta is None:
        return "crear"
    if respuesta.esta_eliminado:
        return "eliminada"
    if version_recibida > respuesta.version_cliente:
        return "actualizar"
    if version_recibida < respuesta.version_cliente:
        return "conflicto"
    return "duplicada"


def _aplicar_respuesta_sincronizada(
    respuesta: Respuesta,
    pregunta: Pregunta,
    operacion: OperacionEntrada,
    dispositivo: str,
    fue_creada: bool,
) -> Respuesta:
    """Aplica valores de una operacion sincronizada a la respuesta."""
    valor_normalizado = validar_y_normalizar_valor_catalogo(pregunta, operacion.valor)
    asignar_valor_a_respuesta(respuesta, pregunta.tipo_pregunta, valor_normalizado)
    respuesta.uuid_local = operacion.uuid_local
    respuesta.version_cliente = operacion.version_cliente
    respuesta.fecha_modificacion_cliente = operacion.fecha_cliente
    respuesta.dispositivo_origen = dispositivo
    respuesta.observacion = respuesta.observacion or ""
    respuesta.origen_respuesta = OrigenRespuesta.SINCRONIZACION
    respuesta.fecha_respuesta_cliente = operacion.fecha_cliente
    respuesta.requiere_sincronizacion = False
    respuesta.esta_eliminado = False
    if not fue_creada:
        respuesta.version_respuesta += 1
    respuesta.save()

    registrar_auditoria(
        entidad=Respuesta.__name__,
        entidad_id=str(respuesta.pk),
        accion=AccionAuditoria.CREAR if fue_creada else AccionAuditoria.EDITAR,
        valor_nuevo=crear_snapshot_modelo(respuesta),
        descripcion="Respuesta sincronizada desde dispositivo offline.",
    )
    return respuesta


def _obtener_o_crear_respuesta_objetivo(
    sesion: SesionAnonima,
    pregunta: Pregunta,
    uuid_local: UUID,
) -> tuple[Respuesta | None, bool, str | None]:
    """Ubica la respuesta objetivo por uuid_local o sesion-pregunta."""
    respuesta_local = obtener_respuesta_por_uuid_local_incluyendo_eliminadas(uuid_local)
    if respuesta_local is not None:
        if respuesta_local.esta_eliminado:
            return respuesta_local, False, MensajesSincronizacionApi.RESPUESTA_ELIMINADA
        return respuesta_local, False, None

    respuesta_sesion = obtener_respuesta(sesion, pregunta)
    if respuesta_sesion is None:
        return None, True, None

    if respuesta_sesion.uuid_local is None:
        return respuesta_sesion, False, None

    if respuesta_sesion.uuid_local != uuid_local:
        return respuesta_sesion, False, None

    return respuesta_sesion, False, None


def _resultado(
    operacion: OperacionEntrada,
    estado: str,
    mensaje: str | None = None,
    respuesta_id: int | None = None,
) -> ResultadoOperacionSync:
    """Construye un resultado de operacion reutilizando el uuid_local."""
    return ResultadoOperacionSync(
        uuid_local=operacion.uuid_local,
        estado=estado,
        mensaje=mensaje,
        respuesta_id=respuesta_id,
    )


def _verificar_precondiciones(
    sesion: SesionAnonima,
    operacion: OperacionEntrada,
) -> ResultadoOperacionSync | None:
    """Valida el estado de la sesion y el checksum antes de sincronizar."""
    if sesion.estado == EstadoSesionAnonima.FINALIZADA:
        return _resultado(
            operacion,
            EstadoSincronizacion.ERROR,
            MensajesSincronizacionApi.FORMULARIO_FINALIZADO,
        )
    checksum_invalido = operacion.checksum and not validar_checksum_operacion(
        operacion.codigo_pregunta,
        operacion.valor,
        operacion.version_cliente,
        operacion.checksum,
    )
    if checksum_invalido:
        return _resultado(
            operacion,
            EstadoSincronizacion.ERROR,
            MensajesSincronizacionApi.CHECKSUM_INVALIDO,
        )
    return None


def _verificar_conflicto_duplicado(
    pregunta: Pregunta,
    respuesta_objetivo: Respuesta | None,
    operacion: OperacionEntrada,
) -> ResultadoOperacionSync | None:
    """Detecta un duplicado con uuid_local distinto sobre la misma pregunta."""
    es_duplicado = (
        respuesta_objetivo is not None
        and respuesta_objetivo.uuid_local is not None
        and respuesta_objetivo.uuid_local != operacion.uuid_local
        and respuesta_objetivo.pregunta_id == pregunta.pk
    )
    if not es_duplicado:
        return None
    registrar_conflicto(
        operacion.uuid_local,
        respuesta_objetivo,
        TipoConflicto.DUPLICADO,
        operacion.valor,
        _extraer_valor_servidor(respuesta_objetivo),
        ResolucionConflicto.SERVIDOR,
    )
    return _resultado(
        operacion,
        EstadoSincronizacion.CONFLICTO,
        MensajesSincronizacionApi.CONFLICTO_VERSION,
        respuesta_objetivo.pk,
    )


def _registrar_conflicto_version(
    respuesta_objetivo: Respuesta,
    operacion: OperacionEntrada,
    tipo_conflicto: str,
    valor_servidor: Any,
) -> ResultadoOperacionSync | None:
    """Registra un conflicto de version y devuelve resultado si gana el servidor."""
    resolucion = resolver_last_write_wins(
        operacion.version_cliente,
        respuesta_objetivo.version_cliente,
        operacion.fecha_cliente,
        respuesta_objetivo.fecha_modificacion_cliente,
    )
    registrar_conflicto(
        operacion.uuid_local,
        respuesta_objetivo,
        tipo_conflicto,
        operacion.valor,
        valor_servidor,
        resolucion,
    )
    if resolucion == ResolucionConflicto.SERVIDOR:
        return _resultado(
            operacion,
            EstadoSincronizacion.CONFLICTO,
            MensajesSincronizacionApi.CONFLICTO_VERSION,
            respuesta_objetivo.pk,
        )
    return None


def _procesar_idempotencia(
    respuesta_objetivo: Respuesta | None,
    operacion: OperacionEntrada,
) -> ResultadoOperacionSync | None:
    """Aplica las reglas de idempotencia por version del cliente."""
    idempotencia = validar_idempotencia(respuesta_objetivo, operacion.version_cliente)

    if idempotencia == "eliminada":
        return _resultado(
            operacion,
            EstadoSincronizacion.ERROR,
            MensajesSincronizacionApi.RESPUESTA_ELIMINADA,
        )
    if idempotencia == "duplicada":
        return _resultado(
            operacion,
            EstadoSincronizacion.SINCRONIZADA,
            MensajesSincronizacionApi.OPERACION_DUPLICADA,
            respuesta_objetivo.pk if respuesta_objetivo else None,
        )
    if idempotencia != "conflicto":
        return None
    return _registrar_conflicto_version(
        respuesta_objetivo,
        operacion,
        TipoConflicto.VERSION,
        _extraer_valor_servidor(respuesta_objetivo),
    )


def _verificar_conflicto_modificacion(
    respuesta_objetivo: Respuesta,
    operacion: OperacionEntrada,
) -> ResultadoOperacionSync | None:
    """Detecta una modificacion concurrente con la misma version de cliente."""
    valor_servidor_previo = _extraer_valor_servidor(respuesta_objetivo)
    hay_modificacion = (
        respuesta_objetivo.version_cliente == operacion.version_cliente
        and valor_servidor_previo != operacion.valor
    )
    if not hay_modificacion:
        return None
    return _registrar_conflicto_version(
        respuesta_objetivo,
        operacion,
        TipoConflicto.MODIFICACION,
        valor_servidor_previo,
    )


def sincronizar_respuesta(
    sesion: SesionAnonima,
    dispositivo: str,
    operacion: OperacionEntrada,
) -> ResultadoOperacionSync:
    """Sincroniza una respuesta individual con validacion de idempotencia."""
    resultado_precondicion = _verificar_precondiciones(sesion, operacion)
    if resultado_precondicion is not None:
        return resultado_precondicion

    pregunta = obtener_pregunta_por_codigo_en_version(
        sesion.version_formulario,
        operacion.codigo_pregunta,
    )
    if pregunta is None:
        raise PreguntaNoExisteError()

    respuesta_objetivo, crear_nueva, error_eliminada = _obtener_o_crear_respuesta_objetivo(
        sesion,
        pregunta,
        operacion.uuid_local,
    )
    if error_eliminada is not None:
        return _resultado(
            operacion,
            EstadoSincronizacion.ERROR,
            error_eliminada,
            respuesta_objetivo.pk if respuesta_objetivo else None,
        )

    resultado_duplicado = _verificar_conflicto_duplicado(
        pregunta,
        respuesta_objetivo,
        operacion,
    )
    if resultado_duplicado is not None:
        return resultado_duplicado

    resultado_idempotencia = _procesar_idempotencia(respuesta_objetivo, operacion)
    if resultado_idempotencia is not None:
        return resultado_idempotencia

    fue_creada = crear_nueva or respuesta_objetivo is None
    if fue_creada:
        respuesta_objetivo = Respuesta(
            sesion=sesion,
            pregunta=pregunta,
            version_respuesta=1,
        )
    else:
        resultado_modificacion = _verificar_conflicto_modificacion(
            respuesta_objetivo,
            operacion,
        )
        if resultado_modificacion is not None:
            return resultado_modificacion

    respuesta_final = _aplicar_respuesta_sincronizada(
        respuesta_objetivo,
        pregunta,
        operacion,
        dispositivo,
        fue_creada,
    )
    _actualizar_actividad_sesion(sesion)

    return _resultado(
        operacion,
        EstadoSincronizacion.SINCRONIZADA,
        respuesta_id=respuesta_final.pk,
    )


def _construir_operacion_entrada(datos: dict[str, Any]) -> OperacionEntrada:
    """Construye una operacion de entrada desde un diccionario validado."""
    return OperacionEntrada(
        uuid_local=datos["uuid_local"],
        codigo_pregunta=datos["codigo_pregunta"],
        valor=datos["valor"],
        version_cliente=datos["version_cliente"],
        fecha_cliente=_parsear_fecha_cliente(datos["fecha_cliente"]),
        checksum=str(datos.get("checksum", "")),
    )


def _procesar_operacion_individual(
    sesion: SesionAnonima,
    dispositivo: str,
    datos_operacion: dict[str, Any],
    origen: str,
) -> ResultadoOperacionSync:
    """Procesa una operacion dentro de su propia transaccion."""
    operacion = _construir_operacion_entrada(datos_operacion)
    try:
        with transaction.atomic():
            resultado = sincronizar_respuesta(sesion, dispositivo, operacion)
            estado_operacion = (
                EstadoSincronizacion.CONFLICTO
                if resultado.estado == EstadoSincronizacion.CONFLICTO
                else EstadoSincronizacion.SINCRONIZADA
            )
            if resultado.mensaje == MensajesSincronizacionApi.OPERACION_DUPLICADA:
                estado_operacion = EstadoSincronizacion.SINCRONIZADA

            registrar_operacion(
                sesion.uuid_sesion,
                operacion,
                dispositivo,
                estado_operacion,
                origen,
                resultado={
                    "estado": resultado.estado,
                    "mensaje": resultado.mensaje,
                    "respuesta_id": resultado.respuesta_id,
                },
            )
            return resultado
    except ChecksumInvalidoError as error:
        registrar_operacion(
            sesion.uuid_sesion,
            operacion,
            dispositivo,
            EstadoSincronizacion.ERROR,
            origen,
            ultimo_error=error.mensaje,
        )
        return ResultadoOperacionSync(
            uuid_local=operacion.uuid_local,
            estado=EstadoSincronizacion.ERROR,
            mensaje=error.mensaje,
        )
    except (
        PreguntaNoExisteError,
        ValorInvalidoError,
        ValorNoPerteneceCatalogoError,
    ) as error:
        registrar_operacion(
            sesion.uuid_sesion,
            operacion,
            dispositivo,
            EstadoSincronizacion.ERROR,
            origen,
            ultimo_error=error.mensaje,
        )
        return ResultadoOperacionSync(
            uuid_local=operacion.uuid_local,
            estado=EstadoSincronizacion.ERROR,
            mensaje=error.mensaje,
        )


def _rechazar_batch_offline_no_permitido(
    sesion: SesionAnonima,
    dispositivo: str,
    origen: str,
    operaciones: list[dict[str, Any]],
) -> ResultadoBatchSync:
    """Rechaza el lote cuando el formulario no admite operacion sin conexion."""
    mensaje = MensajesSincronizacionApi.OFFLINE_NO_PERMITIDO
    errores: list[dict[str, Any]] = []
    for datos_operacion in operaciones:
        operacion = _construir_operacion_entrada(datos_operacion)
        registrar_operacion(
            sesion.uuid_sesion,
            operacion,
            dispositivo,
            EstadoSincronizacion.ERROR,
            origen,
            ultimo_error=mensaje,
        )
        errores.append({"uuid_local": str(operacion.uuid_local), "mensaje": mensaje})

    registrar_auditoria(
        entidad=SesionAnonima.__name__,
        entidad_id=str(sesion.pk),
        accion=AccionAuditoria.SINCRONIZAR,
        valor_nuevo={
            "uuid_sesion": str(sesion.uuid_sesion),
            "dispositivo": dispositivo,
            "rechazadas": len(errores),
            "motivo": mensaje,
        },
        descripcion="Lote de sincronizacion rechazado por formulario sin soporte offline.",
    )
    return ResultadoBatchSync(
        operaciones_procesadas=len(operaciones),
        operaciones_actualizadas=0,
        duplicadas=0,
        conflictos=[],
        errores=errores,
    )


def sincronizar_batch(
    uuid_sesion: UUID,
    dispositivo: str,
    version_app: str,
    operaciones: list[dict[str, Any]],
) -> ResultadoBatchSync:
    """Procesa un lote de operaciones de sincronizacion de forma independiente."""
    sesion = obtener_sesion_por_uuid(uuid_sesion)
    if sesion is None:
        raise SesionRespuestaNoExisteError()

    origen = f"sync:{version_app}"

    if not sesion.formulario.permite_offline:
        return _rechazar_batch_offline_no_permitido(
            sesion,
            dispositivo,
            origen,
            operaciones,
        )
    procesadas = 0
    actualizadas = 0
    duplicadas = 0
    conflictos: list[dict[str, Any]] = []
    errores: list[dict[str, Any]] = []

    for datos_operacion in operaciones:
        procesadas += 1
        resultado = _procesar_operacion_individual(
            sesion,
            dispositivo,
            datos_operacion,
            origen,
        )

        if resultado.estado == EstadoSincronizacion.ERROR:
            errores.append(
                {
                    "uuid_local": str(resultado.uuid_local),
                    "mensaje": resultado.mensaje,
                },
            )
            continue

        if resultado.mensaje == MensajesSincronizacionApi.OPERACION_DUPLICADA:
            duplicadas += 1
            continue

        if resultado.estado == EstadoSincronizacion.CONFLICTO:
            conflictos.append(
                {
                    "uuid_local": str(resultado.uuid_local),
                    "mensaje": resultado.mensaje,
                    "respuesta_id": resultado.respuesta_id,
                },
            )
            continue

        actualizadas += 1

    registrar_auditoria(
        entidad=SesionAnonima.__name__,
        entidad_id=str(sesion.pk),
        accion=AccionAuditoria.SINCRONIZAR,
        valor_nuevo={
            "uuid_sesion": str(uuid_sesion),
            "dispositivo": dispositivo,
            "version_app": version_app,
            "operaciones_procesadas": procesadas,
            "operaciones_actualizadas": actualizadas,
            "duplicadas": duplicadas,
            "conflictos": len(conflictos),
            "errores": len(errores),
        },
        descripcion="Lote de sincronizacion offline procesado.",
    )

    return ResultadoBatchSync(
        operaciones_procesadas=procesadas,
        operaciones_actualizadas=actualizadas,
        duplicadas=duplicadas,
        conflictos=conflictos,
        errores=errores,
    )
