"""
Servicios del motor avanzado de reglas.
"""

from uuid import UUID

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import registrar_auditoria
from aplicaciones.formularios.reglas.evaluador import evaluar_reglas
from aplicaciones.formularios.reglas.normalizadores import normalizar_valor_respuesta
from aplicaciones.formularios.reglas.resultado import ResultadoReglas
from aplicaciones.formularios.models import ReglaPregunta
from aplicaciones.formularios.selectores import (
    obtener_reglas_activas_por_pregunta_origen,
    obtener_reglas_activas_version,
)
from aplicaciones.respuestas.excepciones import (
    PreguntaNoExisteError,
    SesionRespuestaNoExisteError,
)
from aplicaciones.respuestas.selectores import (
    obtener_pregunta_por_codigo_en_version,
    obtener_respuestas_sesion,
)
from aplicaciones.sesiones_anonimas.models import SesionAnonima
from aplicaciones.sesiones_anonimas.selectores import obtener_sesion_por_uuid


def _construir_mapa_respuestas_por_codigo(sesion: SesionAnonima) -> dict[str, object]:
    """Construye un mapa de valores de respuesta indexado por codigo de pregunta."""
    respuestas = obtener_respuestas_sesion(sesion)
    mapa: dict[str, object] = {}
    for respuesta in respuestas:
        mapa[respuesta.pregunta.codigo] = normalizar_valor_respuesta(respuesta)
    return mapa


def _registrar_auditoria_evaluacion_reglas(
    sesion: SesionAnonima,
    codigo_pregunta: str | None,
    resultado: ResultadoReglas,
) -> None:
    """Registra auditoria de consulta del motor de reglas."""
    valor_nuevo: dict[str, object] = {
        "uuid_sesion": str(sesion.uuid_sesion),
        "codigo_pregunta": codigo_pregunta,
        "total_visibles": len(resultado.preguntas_visibles),
        "total_ocultas": len(resultado.preguntas_ocultas),
        "finalizar_formulario": resultado.finalizar_formulario,
        "no_aplica_formulario": resultado.no_aplica_formulario,
    }
    registrar_auditoria(
        entidad=SesionAnonima.__name__,
        entidad_id=str(sesion.pk),
        accion=AccionAuditoria.CONSULTAR,
        valor_nuevo=valor_nuevo,
        descripcion="Evaluacion de reglas condicionales del formulario.",
    )


def _evaluar_y_serializar(
    sesion: SesionAnonima,
    reglas: list[ReglaPregunta],
    codigo_pregunta: str | None = None,
) -> dict[str, object]:
    """Evalua reglas y retorna el resultado serializado con auditoria."""
    mapa_respuestas = _construir_mapa_respuestas_por_codigo(sesion)
    resultado = evaluar_reglas(reglas, mapa_respuestas)
    _registrar_auditoria_evaluacion_reglas(sesion, codigo_pregunta, resultado)
    return resultado.to_dict()


def evaluar_reglas_sesion(uuid_sesion: str | UUID) -> dict[str, object]:
    """Evalua todas las reglas activas de la sesion y retorna el resultado."""
    sesion = obtener_sesion_por_uuid(UUID(str(uuid_sesion)))
    if sesion is None:
        raise SesionRespuestaNoExisteError()

    reglas = list(obtener_reglas_activas_version(sesion.version_formulario))
    return _evaluar_y_serializar(sesion, reglas)


def evaluar_reglas_para_respuesta(
    uuid_sesion: str | UUID,
    codigo_pregunta: str,
) -> dict[str, object]:
    """Evalua reglas asociadas a la pregunta origen indicada."""
    sesion = obtener_sesion_por_uuid(UUID(str(uuid_sesion)))
    if sesion is None:
        raise SesionRespuestaNoExisteError()

    pregunta = obtener_pregunta_por_codigo_en_version(
        sesion.version_formulario,
        codigo_pregunta,
    )
    if pregunta is None:
        raise PreguntaNoExisteError()

    reglas = list(
        obtener_reglas_activas_por_pregunta_origen(
            sesion.version_formulario,
            codigo_pregunta,
        ),
    )
    return _evaluar_y_serializar(sesion, reglas, codigo_pregunta)
