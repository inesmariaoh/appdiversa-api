"""
Pruebas del comando crear_roles_base.
"""

from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.test import TestCase

from aplicaciones.usuarios.constantes import GrupoSistema, PermisoCodigo


class RolesBaseCommandTests(TestCase):
    """Pruebas de creacion de roles base del sistema."""

    def test_comando_crea_roles(self) -> None:
        call_command("crear_roles_base")
        for nombre in GrupoSistema.TODOS:
            self.assertTrue(Group.objects.filter(name=nombre).exists())

    def test_permisos_asignados(self) -> None:
        call_command("crear_roles_base")
        grupo_gestor = Group.objects.get(name=GrupoSistema.GESTOR_FORMULARIOS)
        permiso_publicar = Permission.objects.get(
            codename=PermisoCodigo.PUBLICAR_FORMULARIOS,
        )
        self.assertTrue(grupo_gestor.permissions.filter(pk=permiso_publicar.pk).exists())
