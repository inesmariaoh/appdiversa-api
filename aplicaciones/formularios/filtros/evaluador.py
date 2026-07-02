"""
Evaluacion parametrizable de preguntas filtro/preliminares.
"""

from datetime import date
from typing import Any

from aplicaciones.formularios.constantes_filtro import (
    CLAVE_VALOR_FILTRO,
    CLAVE_VALORES_FILTRO,
)
from aplicaciones.formularios.models import Pregunta, TipoPregunta, TipoValidacionFiltro
from aplicaciones.formularios.reglas.normalizadores import convertir_a_decimal


def calcular_edad(
    fecha_nacimiento: date,
    fecha_referencia: date | None = None,
) -> int:
    """Calcula la edad en años completos respecto a una fecha de referencia."""
    referencia = fecha_referencia or date.today()
    edad = referencia.year - fecha_nacimiento.year
    cumple_pasado = (referencia.month, referencia.day) < (
        fecha_nacimiento.month,
        fecha_nacimiento.day,
    )
    if cumple_pasado:
        edad -= 1
    return edad


def _extraer_fecha_desde_valor(valor: Any) -> date | None:
    """Interpreta una fecha de nacimiento desde distintos formatos de respuesta."""
    if valor is None:
        return None

    if isinstance(valor, date):
        return valor

    if isinstance(valor, dict):
        anio = valor.get("anio")
        mes = valor.get("mes")
        dia = valor.get("dia")
        if anio and mes and dia:
            try:
                return date(int(anio), int(mes), int(dia))
            except (TypeError, ValueError):
                return None
        return None

    if isinstance(valor, str) and valor.strip():
        try:
            return date.fromisoformat(valor.split("T")[0])
        except ValueError:
            return None

    return None


def _normalizar_valor_filtro_esperado(valor_esperado: Any) -> Any:
    """Normaliza el valor esperado de un filtro desde JSON parametrizado."""
    if not isinstance(valor_esperado, dict):
        return valor_esperado
    if CLAVE_VALOR_FILTRO in valor_esperado:
        return valor_esperado[CLAVE_VALOR_FILTRO]
    if CLAVE_VALORES_FILTRO in valor_esperado:
        return valor_esperado[CLAVE_VALORES_FILTRO]
    return valor_esperado


def _resolver_tipo_validacion_filtro(pregunta: Pregunta) -> str:
    """Resuelve el tipo de validacion de filtro configurado o inferido."""
    if pregunta.tipo_validacion_filtro:
        return pregunta.tipo_validacion_filtro

    if pregunta.tipo_pregunta in {TipoPregunta.FECHA, TipoPregunta.FECHA_HORA}:
        if pregunta.valor_minimo is not None or pregunta.valor_maximo is not None:
            return TipoValidacionFiltro.RANGO_EDAD

    if pregunta.tipo_pregunta in {
        TipoPregunta.RADIO,
        TipoPregunta.SELECT,
        TipoPregunta.CHECKBOX,
        TipoPregunta.SELECT_MULTIPLE,
    }:
        return TipoValidacionFiltro.OPCION_EXACTA

    if pregunta.tipo_pregunta == TipoPregunta.NUMERO:
        return TipoValidacionFiltro.RANGO_NUMERICO

    return ""


def _evaluar_rango_edad(
    pregunta: Pregunta,
    valor: Any,
    fecha_referencia: date | None = None,
) -> bool:
    fecha_nacimiento = _extraer_fecha_desde_valor(valor)
    if fecha_nacimiento is None:
        return False

    edad = calcular_edad(fecha_nacimiento, fecha_referencia)
    edad_minima = int(pregunta.valor_minimo) if pregunta.valor_minimo is not None else None
    edad_maxima = int(pregunta.valor_maximo) if pregunta.valor_maximo is not None else None

    if edad_minima is not None and edad < edad_minima:
        return False
    if edad_maxima is not None and edad > edad_maxima:
        return False
    return True


def _evaluar_opcion_exacta(pregunta: Pregunta, valor: Any) -> bool:
    esperado = _normalizar_valor_filtro_esperado(pregunta.valor_filtro_esperado)
    if esperado is None:
        return valor is not None and str(valor).strip() != ""
    return str(valor) == str(esperado)


def _evaluar_lista_opciones(pregunta: Pregunta, valor: Any) -> bool:
    esperados = _normalizar_valor_filtro_esperado(pregunta.valor_filtro_esperado)
    if not isinstance(esperados, list):
        return _evaluar_opcion_exacta(pregunta, valor)

    if isinstance(valor, list):
        return any(item in esperados for item in valor)
    return valor in esperados


def _evaluar_rango_numerico(pregunta: Pregunta, valor: Any) -> bool:
    numero = convertir_a_decimal(valor)
    if numero is None:
        return False

    minimo = convertir_a_decimal(pregunta.valor_minimo)
    maximo = convertir_a_decimal(pregunta.valor_maximo)
    if minimo is not None and numero < minimo:
        return False
    if maximo is not None and numero > maximo:
        return False
    return True


def _evaluar_booleano(pregunta: Pregunta, valor: Any) -> bool:
    esperado = _normalizar_valor_filtro_esperado(pregunta.valor_filtro_esperado)
    if isinstance(valor, bool):
        return valor is esperado
    if isinstance(esperado, bool):
        return str(valor).lower() in {"true", "1", "si", "sí"} if esperado else str(
            valor,
        ).lower() in {"false", "0", "no"}
    return _evaluar_opcion_exacta(pregunta, valor)


def evaluar_pregunta_filtro(
    pregunta: Pregunta,
    valor: Any,
    fecha_referencia: date | None = None,
) -> tuple[bool, str | None]:
    """Evalua si una respuesta cumple la condicion de filtro de la pregunta."""
    if not pregunta.es_pregunta_filtro:
        return True, None

    tipo_validacion = _resolver_tipo_validacion_filtro(pregunta)
    if not tipo_validacion:
        return True, None

    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return False, pregunta.mensaje_error or None

    cumple = False
    if tipo_validacion == TipoValidacionFiltro.RANGO_EDAD:
        cumple = _evaluar_rango_edad(pregunta, valor, fecha_referencia)
    elif tipo_validacion == TipoValidacionFiltro.OPCION_EXACTA:
        cumple = _evaluar_opcion_exacta(pregunta, valor)
    elif tipo_validacion == TipoValidacionFiltro.LISTA_OPCIONES:
        cumple = _evaluar_lista_opciones(pregunta, valor)
    elif tipo_validacion == TipoValidacionFiltro.RANGO_NUMERICO:
        cumple = _evaluar_rango_numerico(pregunta, valor)
    elif tipo_validacion == TipoValidacionFiltro.BOOLEANO:
        cumple = _evaluar_booleano(pregunta, valor)

    if cumple:
        return True, None

    mensaje = pregunta.mensaje_no_cumple.strip() or pregunta.mensaje_error.strip()
    return False, mensaje or None


def construir_metadata_validacion_filtro(pregunta: Pregunta) -> dict[str, Any] | None:
    """Construye metadata de validacion de filtro para consumo del frontend."""
    if not pregunta.es_pregunta_filtro:
        return None

    tipo_validacion = _resolver_tipo_validacion_filtro(pregunta)
    if not tipo_validacion:
        return None

    return {
        "tipo_validacion": tipo_validacion,
        "valor_minimo": (
            str(pregunta.valor_minimo) if pregunta.valor_minimo is not None else None
        ),
        "valor_maximo": (
            str(pregunta.valor_maximo) if pregunta.valor_maximo is not None else None
        ),
        "valor_esperado": pregunta.valor_filtro_esperado,
        "bloquea_continuacion": pregunta.bloquea_continuacion_si_no_cumple,
        "mensaje_no_cumple": (
            pregunta.mensaje_no_cumple.strip()
            or pregunta.mensaje_error.strip()
            or None
        ),
    }
