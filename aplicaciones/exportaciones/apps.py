"""
Configuracion de la aplicacion de exportaciones transversal.
"""

from django.apps import AppConfig


class ExportacionesConfig(AppConfig):
    """Configuracion del modulo de exportaciones."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "aplicaciones.exportaciones"
    verbose_name = "Exportaciones"
