"""
Formateo legible de valores de respuesta para resumen y notificaciones.
"""

from decimal import Decimal
from typing import Any

from aplicaciones.formularios.models import Pregunta, TipoPregunta

SEPARADOR_OPCIONES = ", "
SEPARADOR_MATRIZ = "; "
SEPARADOR_UBICACION = ", "


def _texto_opcion(pregunta: Pregunta, codigo: str) -> str:
    """Resuelve la etiqueta visible de una opcion por su codigo."""
    for opcion in pregunta.opciones.all():
        if opcion.codigo == codigo:
            return opcion.etiqueta
    return codigo


def _texto_fila_matriz(pregunta: Pregunta, codigo: str) -> str:
    """Resuelve la etiqueta visible de una fila de matriz por su codigo."""
    for fila in pregunta.filas_matriz.all():
        if fila.codigo == codigo:
            return fila.etiqueta
    return codigo


def _texto_columna_matriz(pregunta: Pregunta, codigo: str) -> str:
    """Resuelve la etiqueta visible de una columna de matriz por su codigo."""
    for columna in pregunta.columnas_matriz.all():
        if columna.codigo == codigo:
            return columna.etiqueta
    return codigo


def _formatear_lista_codigos(pregunta: Pregunta, codigos: list[Any]) -> str:
    """Convierte una lista de codigos de opcion en etiquetas legibles."""
    etiquetas = [_texto_opcion(pregunta, str(codigo)) for codigo in codigos]
    return SEPARADOR_OPCIONES.join(etiquetas)


def _formatear_matriz(pregunta: Pregunta, valor: dict[Any, Any]) -> str:
    """Convierte un mapa fila-columna de matriz en texto legible."""
    partes: list[str] = []
    for codigo_fila, codigo_columna in valor.items():
        fila = _texto_fila_matriz(pregunta, str(codigo_fila))
        columna = _texto_columna_matriz(pregunta, str(codigo_columna))
        partes.append(f"{fila}: {columna}")
    return SEPARADOR_MATRIZ.join(partes)


def _formatear_ubicacion_geografica(valor: dict[Any, Any]) -> str:
    """Convierte un diccionario de ubicacion geografica en texto legible."""
    partes: list[str] = []
    for clave, contenido in valor.items():
        if isinstance(contenido, dict):
            etiqueta = str(contenido.get("etiqueta") or contenido.get("codigo") or clave)
        else:
            etiqueta = str(contenido)
        partes.append(f"{clave}: {etiqueta}")
    return SEPARADOR_UBICACION.join(partes)


def _formatear_geolocalizacion(valor: dict[Any, Any]) -> str:
    """Convierte coordenadas de geolocalizacion en texto legible."""
    latitud = valor.get("latitud")
    longitud = valor.get("longitud")
    if latitud is None or longitud is None:
        return ""
    precision = valor.get("precision_metros")
    if precision is not None:
        return f"Latitud {latitud}, longitud {longitud} (±{precision} m)"
    return f"Latitud {latitud}, longitud {longitud}"


def _formatear_valor_primitivo(valor: Any) -> str:
    """Convierte un valor primitivo a cadena legible."""
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    if isinstance(valor, Decimal):
        return str(valor.normalize())
    return str(valor)


def _anexar_observacion_al_resumen(texto: str, observacion: str) -> str:
    """Anexa la observacion complementaria al texto legible del resumen."""
    texto_limpio = texto.strip()
    observacion_limpia = observacion.strip()
    if not observacion_limpia:
        return texto_limpio
    if not texto_limpio:
        return observacion_limpia
    return f"{texto_limpio}: {observacion_limpia}"


def formatear_valor_resumen_legible(
    pregunta: Pregunta,
    tipo_pregunta: str,
    valor: Any,
    observacion: str = "",
) -> str:
    """Genera una representacion legible del valor de respuesta para resumen."""
    if valor is None and not observacion.strip():
        return ""

    texto = ""

    if tipo_pregunta in {TipoPregunta.CHECKBOX, TipoPregunta.SELECT_MULTIPLE}:
        if isinstance(valor, list):
            texto = _formatear_lista_codigos(pregunta, valor)
        else:
            texto = _formatear_valor_primitivo(valor)
    elif tipo_pregunta == TipoPregunta.MATRIZ and isinstance(valor, dict):
        texto = _formatear_matriz(pregunta, valor)
    elif tipo_pregunta == TipoPregunta.UBICACION_GEOGRAFICA and isinstance(valor, dict):
        texto = _formatear_ubicacion_geografica(valor)
    elif tipo_pregunta == TipoPregunta.GEOLOCALIZACION and isinstance(valor, dict):
        texto = _formatear_geolocalizacion(valor)
    elif tipo_pregunta in {
        TipoPregunta.RADIO,
        TipoPregunta.SELECT,
        TipoPregunta.AUTOCOMPLETE,
        TipoPregunta.LIKERT,
    } and isinstance(valor, str):
        texto = _texto_opcion(pregunta, valor)
    elif isinstance(valor, (dict, list)):
        texto = _formatear_valor_primitivo(valor)
    else:
        texto = _formatear_valor_primitivo(valor)

    return _anexar_observacion_al_resumen(texto, observacion)
