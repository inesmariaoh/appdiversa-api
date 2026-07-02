"""
Pruebas del comando crear_usuarios_demo.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase

from aplicaciones.usuarios.constantes import GrupoSistema
from aplicaciones.usuarios.management.commands.crear_usuarios_demo import (
    CONTRASENA_DEMO_PREDETERMINADA,
    USUARIOS_DEMO,
)

User = get_user_model()


class CrearUsuariosDemoCommandTests(TestCase):
    """Pruebas de creacion de usuarios demo del sistema."""

    def test_comando_crea_usuarios_con_grupos(self) -> None:
        call_command("crear_usuarios_demo")
        for definicion in USUARIOS_DEMO:
            usuario = User.objects.get(username=definicion.username)
            self.assertTrue(usuario.check_password(CONTRASENA_DEMO_PREDETERMINADA))
            self.assertTrue(
                usuario.groups.filter(name=definicion.grupo).exists(),
            )

    def test_comando_es_idempotente(self) -> None:
        call_command("crear_usuarios_demo")
        call_command("crear_usuarios_demo")
        self.assertEqual(User.objects.count(), len(USUARIOS_DEMO))

    def test_admin_tiene_is_staff(self) -> None:
        call_command("crear_usuarios_demo")
        admin = User.objects.get(username="admin_appdiversa")
        self.assertTrue(admin.is_staff)
        gestor = User.objects.get(username="gestor_formularios")
        self.assertFalse(gestor.is_staff)

    def test_crear_grupos_iniciales_alias(self) -> None:
        call_command("crear_grupos_iniciales")
        for nombre in GrupoSistema.TODOS:
            self.assertTrue(Group.objects.filter(name=nombre).exists())
