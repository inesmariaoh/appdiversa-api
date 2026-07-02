"""
Pruebas de la API REST de consulta de registros de auditoria.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.models import RegistroAuditoria
from aplicaciones.usuarios.constantes import GrupoSistema
from aplicaciones.usuarios.tests.helpers import (
    CONTRASENA_PRUEBA,
    URL_LOGIN,
    crear_usuario_prueba,
    inicializar_entorno_usuarios,
)

URL_REGISTROS = "/api/v1/auditoria/registros/"


class ApiAuditoriaTests(TestCase):
    """Pruebas de listado y detalle de registros de auditoria."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()
        RegistroAuditoria.objects.create(
            entidad="Formulario",
            entidad_id="10",
            accion=AccionAuditoria.CREAR,
            descripcion="Creacion de formulario de prueba",
        )
        RegistroAuditoria.objects.create(
            entidad="Usuario",
            entidad_id="5",
            accion=AccionAuditoria.EDITAR,
            descripcion="Edicion de perfil",
        )

    def _autenticar(self, username: str, grupo: str) -> None:
        crear_usuario_prueba(username, grupo=grupo)
        self.cliente.post(
            URL_LOGIN,
            {"username": username, "password": CONTRASENA_PRUEBA},
            format="json",
        )

    def test_listado_requiere_autenticacion(self) -> None:
        respuesta = self.cliente.get(URL_REGISTROS)
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listado_denegado_a_rol_sin_permiso(self) -> None:
        self._autenticar("lector_auditoria", GrupoSistema.LECTOR_FORMULARIOS)
        respuesta = self.cliente.get(URL_REGISTROS)
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_administrador_lista_registros_paginados(self) -> None:
        self._autenticar("admin_auditoria", GrupoSistema.ADMINISTRADOR_GENERAL)
        respuesta = self.cliente.get(URL_REGISTROS)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("results", respuesta.data)
        self.assertGreaterEqual(respuesta.data["count"], 2)

    def test_filtro_por_entidad(self) -> None:
        self._autenticar("admin_filtro", GrupoSistema.ADMINISTRADOR_GENERAL)
        respuesta = self.cliente.get(URL_REGISTROS, {"entidad": "Formulario"})
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)
        self.assertEqual(respuesta.data["results"][0]["entidad"], "Formulario")

    def test_filtro_por_accion_invalida_retorna_error(self) -> None:
        self._autenticar("admin_accion", GrupoSistema.ADMINISTRADOR_GENERAL)
        respuesta = self.cliente.get(URL_REGISTROS, {"accion": "inexistente"})
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_detalle_registro_existente(self) -> None:
        self._autenticar("admin_detalle", GrupoSistema.ADMINISTRADOR_GENERAL)
        registro = RegistroAuditoria.objects.first()
        respuesta = self.cliente.get(f"{URL_REGISTROS}{registro.pk}/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["id"], registro.pk)

    def test_detalle_registro_inexistente(self) -> None:
        self._autenticar("admin_404", GrupoSistema.ADMINISTRADOR_GENERAL)
        respuesta = self.cliente.get(f"{URL_REGISTROS}999999/")
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
