"""
Renderizado de plantillas de notificaciones.
"""

import re
from typing import Any

PATRON_VARIABLE = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


def renderizar_plantilla(contenido: str, variables: dict[str, Any]) -> str:
    """Reemplaza variables tipo {{nombre}} en el contenido de una plantilla."""

    def reemplazar_coincidencia(coincidencia: re.Match[str]) -> str:
        nombre_variable = coincidencia.group(1)
        valor = variables.get(nombre_variable, "")
        return str(valor) if valor is not None else ""

    if not contenido:
        return ""
    return PATRON_VARIABLE.sub(reemplazar_coincidencia, contenido)
