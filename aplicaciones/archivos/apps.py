"""
Configuracion de la aplicacion de repositorio documental.
"""

from django.apps import AppConfig


class ArchivosConfig(AppConfig):
    """Configuracion del modulo de archivos transversal."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "aplicaciones.archivos"
    verbose_name = "Repositorio documental"
