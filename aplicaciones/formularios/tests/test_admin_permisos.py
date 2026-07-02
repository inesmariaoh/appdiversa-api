"""
Pruebas de matriz de permisos de la API administrativa de formularios.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.formularios.tests.helpers_admin import (
    URL_ADMIN_FORMULARIOS,
    crear_formulario_admin_prueba,
    crear_pregunta_prueba,
    crear_seccion_prueba,
    preparar_entorno_admin,
)
from aplicaciones.usuarios.tests.helpers import (
    GRUPO_ADMIN,
    GRUPO_EDITOR,
    GRUPO_GESTOR,
    GRUPO_LECTOR,
    URL_USUARIOS,
    autenticar_cliente,
    crear_usuario_prueba,
)


class PermisosFormulariosAdminTests(TestCase):
    """Valida restricciones por rol en endpoints administrativos de formularios."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        preparar_entorno_admin()

    def setUp(self) -> None:
        self.cliente = APIClient()
        crear_usuario_prueba("admin_form", grupo=GRUPO_ADMIN)
        crear_usuario_prueba("gestor_perm", grupo=GRUPO_GESTOR)
        crear_usuario_prueba("editor_perm", grupo=GRUPO_EDITOR)
        crear_usuario_prueba("lector_perm", grupo=GRUPO_LECTOR)
        self.formulario = crear_formulario_admin_prueba("perm_form")
        self.version = self.formulario.versiones.first()

    def test_editor_no_crea_version(self) -> None:
        autenticar_cliente(self.cliente, "editor_perm")
        respuesta = self.cliente.post(
            f"{URL_ADMIN_FORMULARIOS}{self.formulario.pk}/versiones/",
            {"descripcion_cambio": "Intento editor"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_gestor_crea_version(self) -> None:
        autenticar_cliente(self.cliente, "gestor_perm")
        respuesta = self.cliente.post(
            f"{URL_ADMIN_FORMULARIOS}{self.formulario.pk}/versiones/",
            {"descripcion_cambio": "Nueva version gestor"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data["numero_version"], 2)

    def test_lector_no_edita_seccion(self) -> None:
        seccion = crear_seccion_prueba(self.version)
        autenticar_cliente(self.cliente, "lector_perm")
        respuesta = self.cliente.patch(
            f"/api/v1/admin/secciones/{seccion.pk}/",
            {"titulo": "Cambio bloqueado"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_editor_edita_pregunta_borrador(self) -> None:
        seccion = crear_seccion_prueba(self.version, "sec_edit")
        pregunta = crear_pregunta_prueba(seccion, "p_edit")
        autenticar_cliente(self.cliente, "editor_perm")
        respuesta = self.cliente.patch(
            f"/api/v1/admin/preguntas/{pregunta.pk}/",
            {"texto": "Texto actualizado"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["texto"], "Texto actualizado")


class PermisosUsuariosAdminTests(TestCase):
    """Valida que solo administrador_general gestiona usuarios, grupos y permisos."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        preparar_entorno_admin()

    def setUp(self) -> None:
        self.cliente = APIClient()
        crear_usuario_prueba("admin_users", grupo=GRUPO_ADMIN)
        crear_usuario_prueba("gestor_users", grupo=GRUPO_GESTOR)

    def test_admin_lista_grupos(self) -> None:
        autenticar_cliente(self.cliente, "admin_users")
        respuesta = self.cliente.get("/api/v1/admin/grupos/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(respuesta.data), 5)

    def test_admin_lista_permisos(self) -> None:
        autenticar_cliente(self.cliente, "admin_users")
        respuesta = self.cliente.get("/api/v1/admin/permisos/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(respuesta.data), 1)

    def test_gestor_no_lista_grupos(self) -> None:
        autenticar_cliente(self.cliente, "gestor_users")
        respuesta = self.cliente.get("/api/v1/admin/grupos/")
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_gestor_no_lista_usuarios(self) -> None:
        autenticar_cliente(self.cliente, "gestor_users")
        respuesta = self.cliente.get(URL_USUARIOS)
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
