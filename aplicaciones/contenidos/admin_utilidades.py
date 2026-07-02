"""
Utilidades de administracion Django para contenidos e interfaz.
"""

from typing import Any

from django.utils.html import format_html
from django.utils.safestring import SafeString

from aplicaciones.contenidos.models import LogoInterfaz
from aplicaciones.contenidos.servicios import resolver_url_logo_interfaz

ALTURA_VISTA_PREVIA_DETALLE = 120
ALTURA_VISTA_PREVIA_LISTA = 48


def construir_html_vista_previa_imagen(
    url_imagen: str | None,
    texto_alternativo: str = "",
    altura_maxima: int = ALTURA_VISTA_PREVIA_DETALLE,
) -> SafeString:
    """Genera el HTML de vista previa para una imagen en el admin."""
    if not url_imagen:
        return format_html('<span style="color:#888;">Sin imagen</span>')
    alt_escapado = texto_alternativo or "Vista previa"
    return format_html(
        (
            '<img src="{}" alt="{}" '
            'style="max-height:{}px; max-width:240px; object-fit:contain; '
            'border:1px solid #ddd; padding:4px; background:#fff;" />'
        ),
        url_imagen,
        alt_escapado,
        altura_maxima,
    )


def construir_vista_previa_logo(
    logo: LogoInterfaz | None,
    solicitud: Any = None,
    altura_maxima: int = ALTURA_VISTA_PREVIA_DETALLE,
) -> SafeString:
    """Construye la vista previa de un logo de interfaz para el admin."""
    if logo is None:
        return construir_html_vista_previa_imagen(None)
    url_imagen = resolver_url_logo_interfaz(logo, solicitud)
    return construir_html_vista_previa_imagen(
        url_imagen,
        logo.texto_alternativo,
        altura_maxima,
    )
