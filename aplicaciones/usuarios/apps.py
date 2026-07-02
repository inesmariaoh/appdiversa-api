"""
Configuracion de la aplicacion de usuarios y autenticacion Django.
"""

from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    """Registra la aplicacion de gestion de usuarios del sistema."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "aplicaciones.usuarios"
    verbose_name = "Usuarios"
