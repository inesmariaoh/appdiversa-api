"""
Pruebas del mapeo de permisos Django hacia el panel administrativo.
"""

from django.test import TestCase

from aplicaciones.usuarios.constantes import GrupoSistema
from aplicaciones.usuarios.permisos_frontend import (
    PermisoFrontend,
    construir_permisos_frontend,
)
from aplicaciones.usuarios.tests.helpers import crear_usuario_prueba, inicializar_entorno_usuarios


class PermisosFrontendTests(TestCase):
    """Pruebas de permisos expuestos al frontend segun rol Django."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def test_administrador_general_tiene_todos_los_permisos_panel(self) -> None:
        usuario = crear_usuario_prueba("admin_panel", grupo=GrupoSistema.ADMINISTRADOR_GENERAL)
        permisos = construir_permisos_frontend(usuario)
        self.assertIn(PermisoFrontend.FORMULARIOS_VER, permisos)
        self.assertIn(PermisoFrontend.FORMULARIOS_EDITAR, permisos)
        self.assertIn(PermisoFrontend.FORMULARIOS_PUBLICAR, permisos)
        self.assertIn(PermisoFrontend.USUARIOS_VER, permisos)
        self.assertIn(PermisoFrontend.USUARIOS_EDITAR, permisos)

    def test_lector_solo_puede_ver_formularios(self) -> None:
        usuario = crear_usuario_prueba("lector_panel", grupo=GrupoSistema.LECTOR_FORMULARIOS)
        permisos = construir_permisos_frontend(usuario)
        self.assertEqual(permisos, [PermisoFrontend.FORMULARIOS_VER])

    def test_gestor_puede_ver_editar_y_publicar(self) -> None:
        usuario = crear_usuario_prueba("gestor_panel", grupo=GrupoSistema.GESTOR_FORMULARIOS)
        permisos = construir_permisos_frontend(usuario)
        self.assertIn(PermisoFrontend.FORMULARIOS_VER, permisos)
        self.assertIn(PermisoFrontend.FORMULARIOS_EDITAR, permisos)
        self.assertIn(PermisoFrontend.FORMULARIOS_PUBLICAR, permisos)

    def test_login_admin_expone_permisos_frontend(self) -> None:
        from rest_framework import status
        from rest_framework.test import APIClient

        from aplicaciones.usuarios.tests.helpers import CONTRASENA_PRUEBA, URL_LOGIN

        usuario = crear_usuario_prueba(
            "admin_login_panel",
            grupo=GrupoSistema.ADMINISTRADOR_GENERAL,
        )
        cliente = APIClient()
        respuesta = cliente.post(
            URL_LOGIN,
            {"username": usuario.username, "password": CONTRASENA_PRUEBA},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn(PermisoFrontend.FORMULARIOS_VER, respuesta.data["permisos"])
