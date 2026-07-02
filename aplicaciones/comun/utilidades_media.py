"""
Utilidades para construir URLs absolutas de archivos media.
"""

from typing import Any


def normalizar_url_relativa(url_relativa: str) -> str:
    """Normaliza una URL relativa para que sea valida con build_absolute_uri."""
    if url_relativa.startswith(("http://", "https://", "//")):
        return url_relativa
    if not url_relativa.startswith("/"):
        return f"/{url_relativa}"
    return url_relativa


def construir_url_absoluta_desde_solicitud(
    url_relativa: str,
    solicitud: Any,
) -> str:
    """Construye una URL absoluta desde una solicitud HTTP y una ruta relativa."""
    if solicitud is None:
        return url_relativa
    return solicitud.build_absolute_uri(normalizar_url_relativa(url_relativa))
