"""
Configuracion de la aplicacion de internacionalizacion.
"""

from django.apps import AppConfig


class InternacionalizacionConfig(AppConfig):
    """Configuracion del modulo de internacionalizacion."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "aplicaciones.internacionalizacion"
    verbose_name = "Internacionalización"
