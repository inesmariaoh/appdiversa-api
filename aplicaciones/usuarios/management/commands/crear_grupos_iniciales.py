"""
Comando para crear grupos iniciales mediante delegacion a crear_roles_base.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Crea grupos iniciales de roles delegando en crear_roles_base."""

    help = "Crea grupos iniciales de roles (alias de crear_roles_base)."

    def handle(self, *args, **options) -> None:
        """Ejecuta crear_roles_base para mantener compatibilidad."""
        call_command("crear_roles_base")
