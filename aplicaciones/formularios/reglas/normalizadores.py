"""
Normalizacion de valores para el motor de reglas.
"""

from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from typing import Any

from aplicaciones.formularios.reglas.constantes import (
    CLAVE_MAX_ESPERADO,
    CLAVE_MIN_ESPERADO,
    CLAVE_VALOR_ESPERADO,
    CLAVE_VALORES_ESPERADOS,
)
from aplicaciones.respuestas.models import Respuesta


def _serializar_valor_temporal(valor: date | datetime | time) -> str:
    """Convierte valores temporales a representacion ISO."""
    return valor.isoformat()


def normalizar_valor_respuesta(respuesta: Respuesta | None) -> Any:
    """Retorna el valor util de una respuesta segun los campos almacenados."""
    if respuesta is None:
        return None

    if respuesta.valor_numero is not None:
        return respuesta.valor_numero

    if respuesta.valor_booleano is not None:
        return respuesta.valor_booleano

    if respuesta.valor_fecha_hora is not None:
        return _serializar_valor_temporal(respuesta.valor_fecha_hora)

    if respuesta.valor_fecha is not None:
        return _serializar_valor_temporal(respuesta.valor_fecha)

    if respuesta.valor_hora is not None:
        return _serializar_valor_temporal(respuesta.valor_hora)

    if respuesta.latitud is not None and respuesta.longitud is not None:
        geolocalizacion: dict[str, Any] = {
            "latitud": respuesta.latitud,
            "longitud": respuesta.longitud,
        }
        if respuesta.precision_metros is not None:
            geolocalizacion["precision_metros"] = respuesta.precision_metros
        if respuesta.valor_json:
            geolocalizacion.update(respuesta.valor_json)
        return geolocalizacion

    if respuesta.valor_json is not None:
        return respuesta.valor_json

    if respuesta.archivo_ruta.strip():
        return respuesta.archivo_ruta

    if respuesta.valor_texto.strip():
        return respuesta.valor_texto

    return None


def normalizar_valor_esperado(valor_esperado: Any) -> Any:
    """Normaliza el valor esperado de una regla desde JSON parametrizado."""
    if not isinstance(valor_esperado, dict):
        return valor_esperado

    if CLAVE_VALOR_ESPERADO in valor_esperado:
        return valor_esperado[CLAVE_VALOR_ESPERADO]

    if CLAVE_VALORES_ESPERADOS in valor_esperado:
        return valor_esperado[CLAVE_VALORES_ESPERADOS]

    if CLAVE_MIN_ESPERADO in valor_esperado:
        return valor_esperado[CLAVE_MIN_ESPERADO]

    if CLAVE_MAX_ESPERADO in valor_esperado:
        return valor_esperado[CLAVE_MAX_ESPERADO]

    return valor_esperado


def convertir_a_decimal(valor: Any) -> Decimal | None:
    """Convierte un valor a Decimal si es posible."""
    if valor is None:
        return None
    try:
        return Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return None
