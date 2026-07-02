"""
Configuracion de la aplicacion de catalogos parametrizables.
"""

from django.apps import AppConfig


class CatalogosConfig(AppConfig):
    """Configuracion del modulo de catalogos empresariales."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "aplicaciones.catalogos"
    verbose_name = "Catálogos parametrizables"
