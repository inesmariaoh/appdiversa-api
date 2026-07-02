"""
Configuracion de la aplicacion de notificaciones transversal.
"""

from django.apps import AppConfig


class NotificacionesConfig(AppConfig):
    """Configuracion del modulo de notificaciones."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "aplicaciones.notificaciones"
    verbose_name = "Notificaciones"
