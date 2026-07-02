"""
Servicios de normalizacion de respuestas para analitica.
"""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from aplicaciones.analitica.excepciones import FiltroAnaliticaInvalidoError
from aplicaciones.analitica.selectores import obtener_respuestas_para_analitica
from aplicaciones.formularios.models import Pregunta
from aplicaciones.respuestas.models import Respuesta


def _serializar_instante(valor: datetime | None) -> str | None:
    """Convierte un datetime a cadena ISO para exportacion analitica."""
    if valor is None:
        return None
    return valor.isoformat()


def _serializar_fecha(valor: date | None) -> str | None:
    """Convierte una fecha a cadena ISO para exportacion analitica."""
    if valor is None:
        return None
    return valor.isoformat()


def _serializar_hora(valor: time | None) -> str | None:
    """Convierte una hora a cadena ISO para exportacion analitica."""
    if valor is None:
        return None
    return valor.isoformat()


def _determinar_respuesta_valor(respuesta: Respuesta) -> Any:
    """Determina el valor principal de una respuesta segun su contenido."""
    if respuesta.valor_numero is not None:
        return float(respuesta.valor_numero)

    if respuesta.valor_texto.strip():
        return respuesta.valor_texto

    if respuesta.valor_booleano is not None:
        return respuesta.valor_booleano

    if respuesta.valor_fecha is not None:
        return _serializar_fecha(respuesta.valor_fecha)

    if respuesta.valor_hora is not None:
        return _serializar_hora(respuesta.valor_hora)

    if respuesta.valor_fecha_hora is not None:
        return _serializar_instante(respuesta.valor_fecha_hora)

    if respuesta.valor_json is not None:
        return respuesta.valor_json

    if respuesta.latitud is not None and respuesta.longitud is not None:
        return {
            "latitud": float(respuesta.latitud),
            "longitud": float(respuesta.longitud),
            "precision_metros": (
                float(respuesta.precision_metros)
                if respuesta.precision_metros is not None
                else None
            ),
        }

    if respuesta.archivo_ruta.strip():
        return respuesta.archivo_ruta

    return None


def _formatear_respuesta_numero(valor_numero: Decimal | None) -> str:
    """Formatea el valor numerico como cadena para consumo analitico."""
    if valor_numero is None:
        return ""
    return f"{valor_numero:.4f}"


def _obtener_datos_catalogo_pregunta(pregunta) -> dict[str, Any]:
    """Retorna metadata de catalogo asociada a una pregunta para analitica."""
    if not pregunta.usa_catalogo or pregunta.catalogo_asociado is None:
        return {
            "usa_catalogo": False,
            "catalogo_codigo": None,
            "catalogo_nombre": None,
        }

    catalogo = pregunta.catalogo_asociado
    return {
        "usa_catalogo": True,
        "catalogo_codigo": catalogo.codigo,
        "catalogo_nombre": catalogo.nombre,
    }


def normalizar_respuesta_analitica(respuesta: Respuesta) -> dict[str, Any]:
    """Transforma una respuesta individual en formato plano para BI."""
    sesion = respuesta.sesion
    formulario = sesion.formulario
    version = sesion.version_formulario
    pregunta = respuesta.pregunta
    seccion = pregunta.seccion
    datos_catalogo = _obtener_datos_catalogo_pregunta(pregunta)

    return {
        "uuid_sesion": str(sesion.uuid_sesion),
        "estado_sesion": sesion.estado,
        "fecha_inicio_sesion": _serializar_instante(sesion.fecha_inicio),
        "fecha_ultima_actividad": _serializar_instante(sesion.fecha_ultima_actividad),
        "formulario_uuid": str(formulario.uuid),
        "formulario_codigo": formulario.codigo,
        "formulario_nombre": formulario.nombre,
        "tipo_formulario": formulario.tipo_formulario,
        "numero_version": version.numero_version,
        "seccion_codigo": seccion.codigo,
        "seccion_titulo": seccion.titulo,
        "pregunta_codigo": pregunta.codigo,
        "pregunta_texto": pregunta.texto,
        "tipo_pregunta": pregunta.tipo_pregunta,
        "usa_catalogo": datos_catalogo["usa_catalogo"],
        "catalogo_codigo": datos_catalogo["catalogo_codigo"],
        "catalogo_nombre": datos_catalogo["catalogo_nombre"],
        "respuesta_valor": _determinar_respuesta_valor(respuesta),
        "respuesta_texto": respuesta.valor_texto,
        "respuesta_numero": _formatear_respuesta_numero(respuesta.valor_numero),
        "respuesta_json": respuesta.valor_json,
        "observacion": respuesta.observacion,
        "origen_respuesta": respuesta.origen_respuesta,
        "version_respuesta": respuesta.version_respuesta,
        "fecha_respuesta_cliente": _serializar_instante(
            respuesta.fecha_respuesta_cliente,
        ),
        "fecha_respuesta_servidor": _serializar_instante(
            respuesta.fecha_respuesta_servidor,
        ),
        "es_anonima": True,
        "es_offline": sesion.es_offline,
    }


def _parsear_fecha_filtro(valor: str | None) -> datetime | None:
    """Parsea una fecha opcional recibida como query param."""
    if valor is None or not valor.strip():
        return None
    valor_normalizado = valor.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(valor_normalizado)
    except ValueError as error:
        raise FiltroAnaliticaInvalidoError() from error


def listar_respuestas_analiticas(
    formulario_codigo: str | None = None,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    estado_sesion: str | None = None,
) -> list[dict[str, Any]]:
    """Retorna respuestas normalizadas en formato plano para analitica."""
    fecha_inicio_parseada = _parsear_fecha_filtro(fecha_inicio)
    fecha_fin_parseada = _parsear_fecha_filtro(fecha_fin)

    respuestas = obtener_respuestas_para_analitica(
        formulario_codigo=formulario_codigo,
        fecha_inicio=fecha_inicio_parseada,
        fecha_fin=fecha_fin_parseada,
        estado_sesion=estado_sesion,
    )

    return [
        normalizar_respuesta_analitica(respuesta)
        for respuesta in respuestas.iterator()
    ]
