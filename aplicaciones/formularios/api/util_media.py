"""
Utilidades de URLs de medios para la API de formularios.
"""

from typing import Any

from django.db.models import Model

from aplicaciones.comun.utilidades_media import construir_url_absoluta_desde_solicitud


def construir_url_imagen_campo(
    instancia: Model,
    campo: str,
    solicitud: Any,
    campo_repositorio: str | None = None,
) -> str | None:
    """Construye la URL de imagen desde repositorio o campo legacy si existe."""
    if campo_repositorio:
        archivo_repositorio = getattr(instancia, campo_repositorio, None)
        if archivo_repositorio is not None:
            from aplicaciones.archivos.servicios import construir_url

            return construir_url(archivo_repositorio, solicitud)

    archivo_imagen = getattr(instancia, campo)
    if not archivo_imagen:
        return None
    return construir_url_absoluta_desde_solicitud(archivo_imagen.url, solicitud)
