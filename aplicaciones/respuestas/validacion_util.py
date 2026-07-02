"""
Validacion de respuestas utiles para finalizacion de formularios.
"""

from decimal import Decimal
from datetime import date, datetime, time
from typing import Any

from aplicaciones.formularios.constantes_geograficas import CLAVES_UBICACION_GEOGRAFICA
from aplicaciones.formularios.models import Pregunta, TipoPregunta
from aplicaciones.respuestas.models import Respuesta

TIPOS_VALOR_TEXTO_UTIL = frozenset(
    {
        TipoPregunta.TEXTO_CORTO,
        TipoPregunta.TEXTO_LARGO,
        TipoPregunta.RADIO,
        TipoPregunta.SELECT,
        TipoPregunta.AUTOCOMPLETE,
        TipoPregunta.LIKERT,
    },
)

TIPOS_VALOR_JSON_UTIL = frozenset(
    {
        TipoPregunta.CHECKBOX,
        TipoPregunta.SELECT_MULTIPLE,
        TipoPregunta.MATRIZ,
    },
)

TIPOS_ARCHIVO_MULTIMEDIA = frozenset(
    {
        TipoPregunta.ARCHIVO,
        TipoPregunta.FIRMA,
        TipoPregunta.AUDIO,
        TipoPregunta.VIDEO,
    },
)


def _tiene_texto_util(respuesta: Respuesta) -> bool:
    return bool(respuesta.valor_texto.strip())


def _tiene_json_util(respuesta: Respuesta) -> bool:
    valor_json = respuesta.valor_json
    if valor_json is None:
        return False
    if isinstance(valor_json, list):
        return len(valor_json) > 0
    if isinstance(valor_json, dict):
        return len(valor_json) > 0
    return True


def _tiene_archivo_multimedia_util(respuesta: Respuesta) -> bool:
    if respuesta.archivo_ruta.strip():
        return True
    if _tiene_texto_util(respuesta):
        return True
    return _tiene_json_util(respuesta)


def _ubicacion_geografica_util(respuesta: Respuesta) -> bool:
    if not _tiene_json_util(respuesta):
        return False
    valor_json = respuesta.valor_json
    if not isinstance(valor_json, dict):
        return False
    return CLAVES_UBICACION_GEOGRAFICA.issubset(valor_json.keys())


def validar_respuesta_util(pregunta: Pregunta, respuesta: Respuesta) -> bool:
    """Evalua si una respuesta contiene un valor util segun el tipo de pregunta."""
    tipo_pregunta = pregunta.tipo_pregunta

    if tipo_pregunta == TipoPregunta.UBICACION_GEOGRAFICA:
        return _ubicacion_geografica_util(respuesta)

    if tipo_pregunta in TIPOS_VALOR_TEXTO_UTIL:
        return _tiene_texto_util(respuesta)

    if tipo_pregunta == TipoPregunta.NUMERO:
        return respuesta.valor_numero is not None

    if tipo_pregunta == TipoPregunta.FECHA:
        return respuesta.valor_fecha is not None

    if tipo_pregunta == TipoPregunta.HORA:
        return respuesta.valor_hora is not None

    if tipo_pregunta == TipoPregunta.FECHA_HORA:
        return respuesta.valor_fecha_hora is not None

    if tipo_pregunta in TIPOS_VALOR_JSON_UTIL:
        return _tiene_json_util(respuesta)

    if tipo_pregunta == TipoPregunta.GEOLOCALIZACION:
        return respuesta.latitud is not None and respuesta.longitud is not None

    if tipo_pregunta in TIPOS_ARCHIVO_MULTIMEDIA:
        return _tiene_archivo_multimedia_util(respuesta)

    if respuesta.valor_booleano is not None:
        return True

    return False


def _serializar_valor_exportable(valor: Any) -> Any:
    """Convierte valores de dominio a tipos serializables en JSON."""
    if valor is None:
        return None
    if isinstance(valor, (datetime, date, time)):
        return valor.isoformat()
    if isinstance(valor, Decimal):
        return float(valor)
    return valor


def _extraer_valor_resumen_numero(respuesta: Respuesta) -> Any:
    if respuesta.valor_numero is not None:
        return _serializar_valor_exportable(respuesta.valor_numero)
    return respuesta.valor_booleano


def _extraer_valor_resumen_geolocalizacion(respuesta: Respuesta) -> dict[str, Any]:
    return {
        "latitud": _serializar_valor_exportable(respuesta.latitud),
        "longitud": _serializar_valor_exportable(respuesta.longitud),
        "precision_metros": _serializar_valor_exportable(
            respuesta.precision_metros,
        ),
    }


def _extraer_valor_resumen_multimedia(respuesta: Respuesta) -> Any:
    if respuesta.archivo_ruta.strip():
        return respuesta.archivo_ruta
    if respuesta.valor_texto.strip():
        return respuesta.valor_texto
    return respuesta.valor_json


def extraer_valor_resumen(respuesta: Respuesta, tipo_pregunta: str) -> Any:
    """Extrae el valor de respuesta para el resumen segun el tipo de pregunta."""
    if tipo_pregunta in TIPOS_VALOR_TEXTO_UTIL:
        return respuesta.valor_texto

    if tipo_pregunta == TipoPregunta.NUMERO:
        return _extraer_valor_resumen_numero(respuesta)

    if tipo_pregunta == TipoPregunta.FECHA:
        return _serializar_valor_exportable(respuesta.valor_fecha)

    if tipo_pregunta == TipoPregunta.HORA:
        return _serializar_valor_exportable(respuesta.valor_hora)

    if tipo_pregunta == TipoPregunta.FECHA_HORA:
        return _serializar_valor_exportable(respuesta.valor_fecha_hora)

    if tipo_pregunta == TipoPregunta.UBICACION_GEOGRAFICA:
        return respuesta.valor_json

    if tipo_pregunta in TIPOS_VALOR_JSON_UTIL:
        return respuesta.valor_json

    if tipo_pregunta == TipoPregunta.GEOLOCALIZACION:
        return _extraer_valor_resumen_geolocalizacion(respuesta)

    if tipo_pregunta in TIPOS_ARCHIVO_MULTIMEDIA:
        return _extraer_valor_resumen_multimedia(respuesta)

    if respuesta.valor_booleano is not None:
        return respuesta.valor_booleano

    return respuesta.valor_texto or respuesta.valor_json
