"""
Servicios de negocio para respuestas anonimas.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import crear_snapshot_modelo, registrar_auditoria
from aplicaciones.formularios.models import Pregunta
from aplicaciones.respuestas.catalogo_validacion import validar_y_normalizar_valor_catalogo
from aplicaciones.respuestas.constantes import (
    MENSAJES_MOTIVO_PENDIENTE,
    MensajesRespuestaApi,
    MotivoPreguntaPendiente,
)
from aplicaciones.respuestas.excepciones import (
    FormularioYaFinalizadoError,
    OrigenRespuestaInvalidoError,
    PreguntaNoExisteError,
    SesionRespuestaNoExisteError,
    ValorInvalidoError,
)
from aplicaciones.respuestas.mapeo_valores import asignar_valor_a_respuesta
from aplicaciones.respuestas.models import OrigenRespuesta, Respuesta
from aplicaciones.respuestas.selectores import (
    evaluar_filtros_sesion,
    obtener_pregunta_por_codigo_en_version,
    obtener_preguntas_flujo_visual_sesion,
    obtener_preguntas_obligatorias_efectivas_sesion,
    obtener_respuesta,
    obtener_respuestas_por_pregunta_sesion,
    obtener_respuestas_sesion,
    obtener_resumen_respuestas_sesion,
    obtener_todas_preguntas_activas_sesion,
    evaluar_resultado_reglas_sesion,
)
from aplicaciones.respuestas.validadores_ubicacion_geografica import (
    es_pregunta_ubicacion_geografica,
    validar_y_normalizar_ubicacion_geografica,
)
from aplicaciones.formularios.reglas.visibilidad import pregunta_visible_efectiva
from aplicaciones.respuestas.formateo_valor_resumen import formatear_valor_resumen_legible
from aplicaciones.respuestas.validacion_texto_otro import falta_texto_otro_obligatorio
from aplicaciones.respuestas.validacion_util import (
    extraer_valor_resumen,
    validar_respuesta_util,
)
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima
from aplicaciones.sesiones_anonimas.selectores import obtener_sesion_por_uuid


@dataclass(frozen=True)
class ResultadoGuardarRespuesta:
    """Resultado de guardado o actualizacion de respuesta."""

    respuesta: Respuesta
    fue_creada: bool


def _validar_origen_respuesta(origen_respuesta: str) -> str:
    """Valida que el origen de respuesta sea un valor permitido."""
    valores_permitidos = {item.value for item in OrigenRespuesta}
    if origen_respuesta not in valores_permitidos:
        raise OrigenRespuestaInvalidoError()
    return origen_respuesta


def _parsear_fecha_respuesta_cliente(
    fecha_respuesta_cliente: datetime | str | None,
) -> datetime | None:
    """Convierte la fecha del cliente a datetime si se proporciona."""
    if fecha_respuesta_cliente is None:
        return None
    if isinstance(fecha_respuesta_cliente, datetime):
        return fecha_respuesta_cliente
    valor_normalizado = str(fecha_respuesta_cliente).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(valor_normalizado)
    except ValueError as error:
        raise ValorInvalidoError() from error


def _determinar_requiere_sincronizacion(origen_respuesta: str) -> bool:
    """Indica si la respuesta requiere sincronizacion futura."""
    return origen_respuesta in {
        OrigenRespuesta.OFFLINE,
        OrigenRespuesta.SINCRONIZACION,
    }


def _actualizar_actividad_sesion(sesion: SesionAnonima) -> None:
    """Actualiza el estado y la ultima actividad de la sesion."""
    sesion.estado = EstadoSesionAnonima.EN_PROCESO
    sesion.fecha_ultima_actividad = timezone.now()
    sesion.save(update_fields=["estado", "fecha_ultima_actividad", "fecha_modificacion"])


def guardar_o_actualizar_respuesta(
    uuid_sesion: UUID,
    codigo_pregunta: str,
    valor: object,
    observacion: str = "",
    origen_respuesta: str = OrigenRespuesta.WEB,
    fecha_respuesta_cliente: datetime | str | None = None,
) -> ResultadoGuardarRespuesta:
    """Guarda o actualiza una respuesta anonima asociada a una sesion."""
    sesion = obtener_sesion_por_uuid(uuid_sesion)
    if sesion is None:
        raise SesionRespuestaNoExisteError()

    origen_validado = _validar_origen_respuesta(origen_respuesta)
    pregunta = obtener_pregunta_por_codigo_en_version(
        sesion.version_formulario,
        codigo_pregunta,
    )
    if pregunta is None:
        raise PreguntaNoExisteError()

    fecha_cliente = _parsear_fecha_respuesta_cliente(fecha_respuesta_cliente)
    requiere_sincronizacion = _determinar_requiere_sincronizacion(origen_validado)

    with transaction.atomic():
        respuesta_existente = obtener_respuesta(sesion, pregunta)
        fue_creada = respuesta_existente is None
        valor_anterior = None
        if respuesta_existente is not None:
            valor_anterior = crear_snapshot_modelo(respuesta_existente)

        if fue_creada:
            respuesta = Respuesta(
                sesion=sesion,
                pregunta=pregunta,
                version_respuesta=1,
            )
        else:
            respuesta = respuesta_existente
            respuesta.version_respuesta += 1

        valor_normalizado = (
            validar_y_normalizar_ubicacion_geografica(pregunta, valor)
            if es_pregunta_ubicacion_geografica(pregunta)
            else validar_y_normalizar_valor_catalogo(pregunta, valor)
        )
        asignar_valor_a_respuesta(respuesta, pregunta.tipo_pregunta, valor_normalizado)
        respuesta.observacion = observacion
        respuesta.origen_respuesta = origen_validado
        respuesta.fecha_respuesta_cliente = fecha_cliente
        respuesta.requiere_sincronizacion = requiere_sincronizacion
        respuesta.esta_eliminado = False
        respuesta.save()

        registrar_auditoria(
            entidad=Respuesta.__name__,
            entidad_id=str(respuesta.pk),
            accion=AccionAuditoria.CREAR if fue_creada else AccionAuditoria.EDITAR,
            valor_anterior=valor_anterior,
            valor_nuevo=crear_snapshot_modelo(respuesta),
        )

        _actualizar_actividad_sesion(sesion)

    limpiar_respuestas_preguntas_ocultas(sesion)

    return ResultadoGuardarRespuesta(respuesta=respuesta, fue_creada=fue_creada)


def listar_respuestas_sesion(uuid_sesion: UUID) -> SesionAnonima:
    """Retorna la sesion con sus respuestas para consulta publica."""
    sesion = obtener_sesion_por_uuid(uuid_sesion)
    if sesion is None:
        raise SesionRespuestaNoExisteError()
    return sesion


def obtener_respuestas_de_sesion(sesion: SesionAnonima) -> list[Respuesta]:
    """Retorna la lista de respuestas activas de una sesion."""
    return list(obtener_respuestas_sesion(sesion))


def _construir_pregunta_pendiente(pregunta: Pregunta, motivo: str) -> dict[str, object]:
    """Construye el detalle de una pregunta pendiente con su motivo especifico."""
    return {
        "codigo": pregunta.codigo,
        "texto": pregunta.texto,
        "seccion_codigo": pregunta.seccion.codigo,
        "seccion_titulo": pregunta.seccion.titulo,
        "orden": pregunta.orden,
        "motivo": motivo,
        "mensaje": MENSAJES_MOTIVO_PENDIENTE[motivo],
    }


def _preguntas_pendientes_por_obligatoriedad(
    preguntas_obligatorias: list[Pregunta],
    respuestas_por_pregunta: dict[int, Respuesta],
) -> list[tuple[Pregunta, str]]:
    """Selecciona preguntas obligatorias sin respuesta util."""
    pendientes: list[tuple[Pregunta, str]] = []
    for pregunta in preguntas_obligatorias:
        respuesta = respuestas_por_pregunta.get(pregunta.pk)
        if respuesta is None or not validar_respuesta_util(pregunta, respuesta):
            pendientes.append(
                (pregunta, MotivoPreguntaPendiente.OBLIGATORIA_SIN_RESPUESTA),
            )
    return pendientes


def _preguntas_pendientes_por_texto_otro(
    sesion: SesionAnonima,
    resultado_reglas: object,
    respuestas_por_pregunta: dict[int, Respuesta],
) -> list[tuple[Pregunta, str]]:
    """Selecciona preguntas visibles con opcion otro seleccionada sin texto obligatorio."""
    ids_visibles = [
        pregunta.pk
        for pregunta in obtener_preguntas_flujo_visual_sesion(sesion, resultado_reglas)
    ]
    preguntas_con_otro = (
        Pregunta.objects.filter(
            pk__in=ids_visibles,
            permite_otro=True,
            texto_otro_obligatorio=True,
        )
        .select_related("seccion")
        .prefetch_related("opciones")
    )

    pendientes: list[tuple[Pregunta, str]] = []
    for pregunta in preguntas_con_otro:
        respuesta = respuestas_por_pregunta.get(pregunta.pk)
        if respuesta is not None and falta_texto_otro_obligatorio(pregunta, respuesta):
            pendientes.append(
                (pregunta, MotivoPreguntaPendiente.TEXTO_OTRO_REQUERIDO),
            )
    return pendientes


def _consolidar_preguntas_pendientes(
    pendientes: list[tuple[Pregunta, str]],
) -> list[dict[str, object]]:
    """Construye el detalle de pendientes evitando duplicados por pregunta."""
    identificadores_vistos: set[int] = set()
    resultado: list[dict[str, object]] = []
    for pregunta, motivo in pendientes:
        if pregunta.pk in identificadores_vistos:
            continue
        identificadores_vistos.add(pregunta.pk)
        resultado.append(_construir_pregunta_pendiente(pregunta, motivo))
    return resultado


def _evaluar_preguntas_pendientes(sesion: SesionAnonima) -> list[dict[str, object]]:
    """Identifica preguntas obligatorias o con texto otro obligatorio sin completar."""
    resultado_reglas = evaluar_resultado_reglas_sesion(sesion)
    respuestas_por_pregunta = obtener_respuestas_por_pregunta_sesion(sesion)
    preguntas_obligatorias = obtener_preguntas_obligatorias_efectivas_sesion(
        sesion,
        resultado_reglas,
    )

    pendientes = _preguntas_pendientes_por_obligatoriedad(
        preguntas_obligatorias,
        respuestas_por_pregunta,
    )
    pendientes += _preguntas_pendientes_por_texto_otro(
        sesion,
        resultado_reglas,
        respuestas_por_pregunta,
    )
    return _consolidar_preguntas_pendientes(pendientes)


def limpiar_respuestas_preguntas_ocultas(sesion: SesionAnonima) -> list[str]:
    """Elimina logicamente respuestas de preguntas ocultas cuando corresponde."""
    resultado_reglas = evaluar_resultado_reglas_sesion(sesion)
    preguntas = obtener_todas_preguntas_activas_sesion(sesion)
    codigos_limpiados: list[str] = []

    for pregunta in preguntas:
        if pregunta_visible_efectiva(pregunta, resultado_reglas):
            continue
        if not pregunta.limpiar_respuesta_al_ocultar:
            continue

        respuesta = obtener_respuesta(sesion, pregunta)
        if respuesta is None or respuesta.esta_eliminado:
            continue
        if not validar_respuesta_util(pregunta, respuesta):
            continue

        valor_anterior = crear_snapshot_modelo(respuesta)
        respuesta.esta_eliminado = True
        respuesta.save(update_fields=["esta_eliminado", "fecha_modificacion"])
        registrar_auditoria(
            entidad=Respuesta.__name__,
            entidad_id=str(respuesta.pk),
            accion=AccionAuditoria.ELIMINAR,
            valor_anterior=valor_anterior,
            valor_nuevo=crear_snapshot_modelo(respuesta),
            descripcion="Limpieza de respuesta por pregunta oculta en reglas.",
        )
        codigos_limpiados.append(pregunta.codigo)

    return codigos_limpiados


def _construir_resultado_validacion(
    preguntas_pendientes: list[dict[str, object]],
) -> dict[str, object]:
    """Construye el resultado de validacion de finalizacion."""
    total_pendientes = len(preguntas_pendientes)
    return {
        "es_valido": total_pendientes == 0,
        "cumple_filtros": True,
        "total_pendientes": total_pendientes,
        "preguntas_pendientes": preguntas_pendientes,
    }


def _construir_resultado_filtros_no_cumplidos(
    resultado_filtros: dict[str, object],
) -> dict[str, object]:
    """Construye el resultado cuando no se cumplen filtros preliminares."""
    filtros = resultado_filtros.get("filtros", [])
    if not isinstance(filtros, list):
        filtros = []
    incumplidos = [
        item
        for item in filtros
        if not item.get("cumple") and item.get("bloquea_continuacion", True)
    ]
    return {
        "es_valido": False,
        "cumple_filtros": False,
        "total_pendientes": len(incumplidos),
        "filtros_incumplidos": incumplidos,
        "preguntas_pendientes": [],
        "mensaje": MensajesRespuestaApi.FILTROS_NO_CUMPLIDOS,
    }


def _validar_filtros_sesion(sesion: SesionAnonima) -> dict[str, object] | None:
    """Retorna resultado de error si la sesion no cumple filtros preliminares."""
    resultado_filtros = evaluar_filtros_sesion(sesion)
    if resultado_filtros["cumple_filtros"]:
        return None
    return _construir_resultado_filtros_no_cumplidos(resultado_filtros)


def _registrar_auditoria_sesion(
    sesion: SesionAnonima,
    accion: str,
    descripcion: str,
    datos_adicionales: dict[str, object] | None = None,
) -> None:
    """Registra auditoria de operaciones sobre una sesion anonima."""
    valor_nuevo: dict[str, object] = {
        "uuid_sesion": str(sesion.uuid_sesion),
        "estado": sesion.estado,
    }
    if datos_adicionales is not None:
        valor_nuevo.update(datos_adicionales)

    registrar_auditoria(
        entidad=SesionAnonima.__name__,
        entidad_id=str(sesion.pk),
        accion=accion,
        valor_nuevo=valor_nuevo,
        descripcion=descripcion,
    )


def validar_formulario_sesion(uuid_sesion: UUID) -> dict[str, object]:
    """Valida si la sesion cumple todas las preguntas obligatorias."""
    sesion = obtener_sesion_por_uuid(uuid_sesion)
    if sesion is None:
        raise SesionRespuestaNoExisteError()

    resultado_filtros = _validar_filtros_sesion(sesion)
    if resultado_filtros is not None:
        _registrar_auditoria_sesion(
            sesion,
            AccionAuditoria.CONSULTAR,
            MensajesRespuestaApi.FILTROS_NO_CUMPLIDOS,
            {"cumple_filtros": False},
        )
        return resultado_filtros

    resultado = _construir_resultado_validacion(_evaluar_preguntas_pendientes(sesion))
    _registrar_auditoria_sesion(
        sesion,
        AccionAuditoria.CONSULTAR,
        "Validacion de finalizacion de formulario.",
        {
            "es_valido": resultado["es_valido"],
            "total_pendientes": resultado["total_pendientes"],
        },
    )
    return resultado


def _obtener_sesion_para_finalizacion(uuid_sesion: UUID) -> SesionAnonima:
    """Obtiene una sesion apta para finalizacion o lanza excepcion funcional."""
    sesion = obtener_sesion_por_uuid(uuid_sesion)
    if sesion is None:
        raise SesionRespuestaNoExisteError()
    if sesion.estado == EstadoSesionAnonima.FINALIZADA:
        raise FormularioYaFinalizadoError()
    return sesion


def _construir_item_resumen(respuesta: Respuesta) -> dict[str, object]:
    """Construye un item del resumen de respuestas de la sesion."""
    pregunta = respuesta.pregunta
    seccion = pregunta.seccion
    valor = extraer_valor_resumen(respuesta, pregunta.tipo_pregunta)
    return {
        "seccion_codigo": seccion.codigo,
        "seccion_titulo": seccion.titulo,
        "pregunta_codigo": pregunta.codigo,
        "pregunta_texto": pregunta.texto,
        "tipo_pregunta": pregunta.tipo_pregunta,
        "valor": valor,
        "valor_legible": formatear_valor_resumen_legible(
            pregunta,
            pregunta.tipo_pregunta,
            valor,
            respuesta.observacion,
        ),
        "observacion": respuesta.observacion,
    }


def resumen_respuestas_sesion(uuid_sesion: UUID) -> dict[str, object]:
    """Retorna el resumen de respuestas activas de una sesion."""
    sesion = obtener_sesion_por_uuid(uuid_sesion)
    if sesion is None:
        raise SesionRespuestaNoExisteError()

    respuestas = obtener_resumen_respuestas_sesion(sesion)
    items_resumen = [_construir_item_resumen(respuesta) for respuesta in respuestas]

    return {
        "uuid_sesion": sesion.uuid_sesion,
        "estado": sesion.estado,
        "formulario": {
            "uuid": sesion.formulario.uuid,
            "codigo": sesion.formulario.codigo,
            "nombre": sesion.formulario.nombre,
        },
        "version": {
            "numero_version": sesion.version_formulario.numero_version,
        },
        "respuestas": items_resumen,
    }


def finalizar_formulario_sesion(
    uuid_sesion: UUID,
    correo_notificacion: str | None = None,
) -> dict[str, object]:
    """Finaliza el diligenciamiento si no hay preguntas obligatorias pendientes."""
    sesion = _obtener_sesion_para_finalizacion(uuid_sesion)

    resultado_filtros = _validar_filtros_sesion(sesion)
    if resultado_filtros is not None:
        _registrar_auditoria_sesion(
            sesion,
            AccionAuditoria.FINALIZAR_FORMULARIO,
            MensajesRespuestaApi.FILTROS_NO_CUMPLIDOS,
            {"cumple_filtros": False},
        )
        return resultado_filtros

    preguntas_pendientes = _evaluar_preguntas_pendientes(sesion)

    if preguntas_pendientes:
        resultado_pendientes = _construir_resultado_validacion(preguntas_pendientes)
        _registrar_auditoria_sesion(
            sesion,
            AccionAuditoria.FINALIZAR_FORMULARIO,
            MensajesRespuestaApi.PREGUNTAS_OBLIGATORIAS_PENDIENTES,
            {
                "es_valido": False,
                "total_pendientes": resultado_pendientes["total_pendientes"],
            },
        )
        return resultado_pendientes

    sesion.estado = EstadoSesionAnonima.FINALIZADA
    sesion.fecha_ultima_actividad = timezone.now()
    sesion.save(
        update_fields=[
            "estado",
            "fecha_ultima_actividad",
            "fecha_modificacion",
        ],
    )

    resumen = resumen_respuestas_sesion(uuid_sesion)
    if correo_notificacion:
        from aplicaciones.notificaciones.servicios_correo import (
            enviar_notificacion_formulario_finalizado,
        )

        enviar_notificacion_formulario_finalizado(
            uuid_sesion,
            correo_notificacion.strip(),
            resumen,
        )
    _registrar_auditoria_sesion(
        sesion,
        AccionAuditoria.FINALIZAR_FORMULARIO,
        MensajesRespuestaApi.FORMULARIO_FINALIZADO_OK,
        {"total_respuestas": len(resumen["respuestas"])},
    )

    return {
        "estado": EstadoSesionAnonima.FINALIZADA,
        "mensaje": MensajesRespuestaApi.FORMULARIO_FINALIZADO_OK,
        "resumen": resumen,
    }
