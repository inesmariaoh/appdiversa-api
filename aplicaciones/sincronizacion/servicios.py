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
from aplicaciones.sincronizacion.constantes import MensajesSincronizacionApi
from aplicaciones.sincronizacion.excepciones import ChecksumInvalidoError
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


def resolver_conflicto(
    conflicto_uuid: UUID,
    resolucion: str,
) -> ConflictoSincronizacion:
    """Resuelve manualmente un conflicto de sincronizacion registrado."""
    conflicto = ConflictoSincronizacion.objects.filter(uuid=conflicto_uuid).first()
    if conflicto is None:
        raise ValueError("Conflicto no encontrado.")

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


def sincronizar_respuesta(
    sesion: SesionAnonima,
    dispositivo: str,
    operacion: OperacionEntrada,
) -> ResultadoOperacionSync:
    """Sincroniza una respuesta individual con validacion de idempotencia."""
    if sesion.estado == EstadoSesionAnonima.FINALIZADA:
        return ResultadoOperacionSync(
            uuid_local=operacion.uuid_local,
            estado=EstadoSincronizacion.ERROR,
            mensaje=MensajesSincronizacionApi.FORMULARIO_FINALIZADO,
        )

    if operacion.checksum and not validar_checksum_operacion(
        operacion.codigo_pregunta,
        operacion.valor,
        operacion.version_cliente,
        operacion.checksum,
    ):
        return ResultadoOperacionSync(
            uuid_local=operacion.uuid_local,
            estado=EstadoSincronizacion.ERROR,
            mensaje=MensajesSincronizacionApi.CHECKSUM_INVALIDO,
        )

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
        return ResultadoOperacionSync(
            uuid_local=operacion.uuid_local,
            estado=EstadoSincronizacion.ERROR,
            mensaje=error_eliminada,
            respuesta_id=respuesta_objetivo.pk if respuesta_objetivo else None,
        )

    if (
        respuesta_objetivo is not None
        and respuesta_objetivo.uuid_local is not None
        and respuesta_objetivo.uuid_local != operacion.uuid_local
        and respuesta_objetivo.pregunta_id == pregunta.pk
    ):
        registrar_conflicto(
            operacion.uuid_local,
            respuesta_objetivo,
            TipoConflicto.DUPLICADO,
            operacion.valor,
            _extraer_valor_servidor(respuesta_objetivo),
            ResolucionConflicto.SERVIDOR,
        )
        return ResultadoOperacionSync(
            uuid_local=operacion.uuid_local,
            estado=EstadoSincronizacion.CONFLICTO,
            mensaje=MensajesSincronizacionApi.CONFLICTO_VERSION,
            respuesta_id=respuesta_objetivo.pk,
        )

    idempotencia = validar_idempotencia(respuesta_objetivo, operacion.version_cliente)

    if idempotencia == "eliminada":
        return ResultadoOperacionSync(
            uuid_local=operacion.uuid_local,
            estado=EstadoSincronizacion.ERROR,
            mensaje=MensajesSincronizacionApi.RESPUESTA_ELIMINADA,
        )

    if idempotencia == "duplicada":
        return ResultadoOperacionSync(
            uuid_local=operacion.uuid_local,
            estado=EstadoSincronizacion.SINCRONIZADA,
            mensaje=MensajesSincronizacionApi.OPERACION_DUPLICADA,
            respuesta_id=respuesta_objetivo.pk if respuesta_objetivo else None,
        )

    if idempotencia == "conflicto":
        valor_servidor = _extraer_valor_servidor(respuesta_objetivo)
        resolucion = resolver_last_write_wins(
            operacion.version_cliente,
            respuesta_objetivo.version_cliente,
            operacion.fecha_cliente,
            respuesta_objetivo.fecha_modificacion_cliente,
        )
        registrar_conflicto(
            operacion.uuid_local,
            respuesta_objetivo,
            TipoConflicto.VERSION,
            operacion.valor,
            valor_servidor,
            resolucion,
        )
        if resolucion == ResolucionConflicto.SERVIDOR:
            return ResultadoOperacionSync(
                uuid_local=operacion.uuid_local,
                estado=EstadoSincronizacion.CONFLICTO,
                mensaje=MensajesSincronizacionApi.CONFLICTO_VERSION,
                respuesta_id=respuesta_objetivo.pk,
            )

    fue_creada = crear_nueva or respuesta_objetivo is None
    if fue_creada:
        respuesta_objetivo = Respuesta(
            sesion=sesion,
            pregunta=pregunta,
            version_respuesta=1,
        )

    valor_servidor_previo = (
        _extraer_valor_servidor(respuesta_objetivo)
        if not fue_creada
        else None
    )
    if (
        not fue_creada
        and respuesta_objetivo.version_cliente == operacion.version_cliente
        and valor_servidor_previo != operacion.valor
    ):
        resolucion = resolver_last_write_wins(
            operacion.version_cliente,
            respuesta_objetivo.version_cliente,
            operacion.fecha_cliente,
            respuesta_objetivo.fecha_modificacion_cliente,
        )
        registrar_conflicto(
            operacion.uuid_local,
            respuesta_objetivo,
            TipoConflicto.MODIFICACION,
            operacion.valor,
            valor_servidor_previo,
            resolucion,
        )
        if resolucion == ResolucionConflicto.SERVIDOR:
            return ResultadoOperacionSync(
                uuid_local=operacion.uuid_local,
                estado=EstadoSincronizacion.CONFLICTO,
                mensaje=MensajesSincronizacionApi.CONFLICTO_VERSION,
                respuesta_id=respuesta_objetivo.pk,
            )

    respuesta_final = _aplicar_respuesta_sincronizada(
        respuesta_objetivo,
        pregunta,
        operacion,
        dispositivo,
        fue_creada,
    )
    _actualizar_actividad_sesion(sesion)

    return ResultadoOperacionSync(
        uuid_local=operacion.uuid_local,
        estado=EstadoSincronizacion.SINCRONIZADA,
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
