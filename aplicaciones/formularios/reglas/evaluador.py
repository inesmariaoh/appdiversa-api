"""
Evaluacion de operadores y acciones del motor de reglas.
"""

from typing import Any

from aplicaciones.formularios.models import AccionRegla, OperadorRegla, ReglaPregunta
from aplicaciones.formularios.reglas.normalizadores import (
    convertir_a_decimal,
    normalizar_valor_esperado,
)
from aplicaciones.formularios.reglas.resultado import ResultadoReglas


def _valores_iguales(valor_respuesta: Any, valor_esperado: Any) -> bool:
    """Compara dos valores con tolerancia numerica."""
    if valor_respuesta is None and valor_esperado is None:
        return True
    if valor_respuesta is None or valor_esperado is None:
        return False

    decimal_respuesta = convertir_a_decimal(valor_respuesta)
    decimal_esperado = convertir_a_decimal(valor_esperado)
    if decimal_respuesta is not None and decimal_esperado is not None:
        return decimal_respuesta == decimal_esperado

    return str(valor_respuesta) == str(valor_esperado)


def _contiene_valor(valor_respuesta: Any, valor_esperado: Any) -> bool:
    """Evalua contencion para listas o cadenas de texto."""
    if valor_respuesta is None or valor_esperado is None:
        return False

    if isinstance(valor_respuesta, list):
        if isinstance(valor_esperado, list):
            return any(item in valor_respuesta for item in valor_esperado)
        return valor_esperado in valor_respuesta

    if isinstance(valor_esperado, list):
        return valor_respuesta in valor_esperado

    return str(valor_esperado) in str(valor_respuesta)


def _comparar_magnitud(
    valor_respuesta: Any,
    valor_esperado: Any,
    operador: str,
) -> bool:
    """Compara magnitudes numericas para operadores gt y lt."""
    decimal_respuesta = convertir_a_decimal(valor_respuesta)
    decimal_esperado = convertir_a_decimal(valor_esperado)
    if decimal_respuesta is None or decimal_esperado is None:
        return False
    if operador == OperadorRegla.GT:
        return decimal_respuesta > decimal_esperado
    return decimal_respuesta < decimal_esperado


def _evaluar_in(valor_respuesta: Any, valor_esperado: Any) -> bool:
    """Indica si el valor de respuesta esta dentro del conjunto esperado."""
    if valor_respuesta is None or valor_esperado is None:
        return False
    if isinstance(valor_esperado, list):
        return valor_respuesta in valor_esperado
    return _valores_iguales(valor_respuesta, valor_esperado)


def evaluar_operador(
    valor_respuesta: Any,
    operador: str,
    valor_esperado: Any,
) -> bool:
    """Evalua un operador de regla sin exponer errores tecnicos."""
    if operador == OperadorRegla.EQUALS:
        return _valores_iguales(valor_respuesta, valor_esperado)

    if operador == OperadorRegla.NOT_EQUALS:
        return not _valores_iguales(valor_respuesta, valor_esperado)

    if operador == OperadorRegla.CONTAINS:
        return _contiene_valor(valor_respuesta, valor_esperado)

    if operador == OperadorRegla.GT:
        return _comparar_magnitud(valor_respuesta, valor_esperado, OperadorRegla.GT)

    if operador == OperadorRegla.LT:
        return _comparar_magnitud(valor_respuesta, valor_esperado, OperadorRegla.LT)

    if operador == OperadorRegla.IN:
        return _evaluar_in(valor_respuesta, valor_esperado)

    return False


def aplicar_accion_regla(regla: ReglaPregunta, resultado: ResultadoReglas) -> None:
    """Aplica la accion de una regla al resultado agregado."""
    codigo_pregunta_destino = (
        regla.pregunta_destino.codigo if regla.pregunta_destino_id else None
    )
    codigo_seccion_destino = (
        regla.seccion_destino.codigo if regla.seccion_destino_id else None
    )

    if regla.accion == AccionRegla.MOSTRAR:
        resultado.agregar_codigo_pregunta(
            resultado.preguntas_visibles,
            codigo_pregunta_destino,
        )
    elif regla.accion == AccionRegla.OCULTAR:
        resultado.agregar_codigo_pregunta(
            resultado.preguntas_ocultas,
            codigo_pregunta_destino,
        )
    elif regla.accion == AccionRegla.HABILITAR:
        resultado.agregar_codigo_pregunta(
            resultado.preguntas_habilitadas,
            codigo_pregunta_destino,
        )
    elif regla.accion == AccionRegla.DESHABILITAR:
        resultado.agregar_codigo_pregunta(
            resultado.preguntas_deshabilitadas,
            codigo_pregunta_destino,
        )
    elif regla.accion == AccionRegla.HACER_OBLIGATORIA:
        resultado.agregar_codigo_pregunta(
            resultado.preguntas_obligatorias,
            codigo_pregunta_destino,
        )
    elif regla.accion == AccionRegla.HACER_OPCIONAL:
        resultado.agregar_codigo_pregunta(
            resultado.preguntas_opcionales,
            codigo_pregunta_destino,
        )
    elif regla.accion == AccionRegla.SALTAR_A_PREGUNTA and codigo_pregunta_destino:
        resultado.saltar_a_pregunta = codigo_pregunta_destino
    elif regla.accion == AccionRegla.SALTAR_A_SECCION and codigo_seccion_destino:
        resultado.saltar_a_seccion = codigo_seccion_destino
    elif regla.accion == AccionRegla.FINALIZAR_FORMULARIO:
        resultado.finalizar_formulario = True
    elif regla.accion == AccionRegla.NO_APLICA_FORMULARIO:
        resultado.no_aplica_formulario = True

    if regla.mensaje:
        resultado.agregar_mensaje(regla.mensaje)


def evaluar_reglas(
    reglas: list[ReglaPregunta],
    respuestas_por_codigo: dict[str, Any],
) -> ResultadoReglas:
    """Evalua una coleccion de reglas contra el mapa de respuestas."""
    resultado = ResultadoReglas()

    for regla in reglas:
        codigo_origen = regla.pregunta_origen.codigo
        valor_respuesta = respuestas_por_codigo.get(codigo_origen)
        valor_esperado_normalizado = normalizar_valor_esperado(regla.valor_esperado)
        if evaluar_operador(
            valor_respuesta,
            regla.operador,
            valor_esperado_normalizado,
        ):
            aplicar_accion_regla(regla, resultado)

    return resultado
