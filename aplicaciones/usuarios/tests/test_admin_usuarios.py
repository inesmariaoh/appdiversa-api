"""
Pruebas de gestion administrativa de usuarios.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.notificaciones.constantes import CodigoPlantillaCorreo, EstadoNotificacion
from aplicaciones.notificaciones.models import Notificacion
from aplicaciones.usuarios.constantes import GrupoSistema
from aplicaciones.usuarios.tests.helpers import (
    GRUPO_ADMIN,
    GRUPO_GESTOR,
    URL_USUARIOS,
    autenticar_cliente,
    crear_usuario_prueba,
    inicializar_entorno_usuarios,
)


class UsuariosAdminApiTests(TestCase):
    """Pruebas de endpoints administrativos de usuarios."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.admin = crear_usuario_prueba("admin_usuarios", grupo=GRUPO_ADMIN)
        self.gestor = crear_usuario_prueba("gestor_usuarios", grupo=GRUPO_GESTOR)

    def test_admin_crea_usuario(self) -> None:
        autenticar_cliente(self.cliente, "admin_usuarios")
        respuesta = self.cliente.post(
            URL_USUARIOS,
            {
                "username": "nuevo_usuario",
                "email": "nuevo@example.com",
                "contrasena": "Contrasena123!",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

    def test_crear_usuario_envia_notificacion_si_email_existe(self) -> None:
        autenticar_cliente(self.cliente, "admin_usuarios")
        respuesta = self.cliente.post(
            URL_USUARIOS,
            {
                "username": "usuario_correo",
                "email": "correo_nuevo@example.com",
                "contrasena": "Contrasena123!",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        notificacion = Notificacion.objects.filter(
            destinatario="correo_nuevo@example.com",
            plantilla__codigo=CodigoPlantillaCorreo.USUARIO_CREADO,
        ).first()
        self.assertIsNotNone(notificacion)
        self.assertEqual(notificacion.estado, EstadoNotificacion.ENVIADA)

    def test_no_admin_no_puede_crear(self) -> None:
        autenticar_cliente(self.cliente, "gestor_usuarios")
        respuesta = self.cliente.post(
            URL_USUARIOS,
            {
                "username": "bloqueado",
                "contrasena": "Contrasena123!",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_asignar_grupos(self) -> None:
        autenticar_cliente(self.cliente, "admin_usuarios")
        nuevo = crear_usuario_prueba("usuario_grupos")
        respuesta = self.cliente.post(
            f"{URL_USUARIOS}{nuevo.pk}/asignar-grupos/",
            {"grupos": [GrupoSistema.LECTOR_FORMULARIOS]},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn(GrupoSistema.LECTOR_FORMULARIOS, respuesta.data["grupos"])

    def test_desactivar_usuario(self) -> None:
        autenticar_cliente(self.cliente, "admin_usuarios")
        objetivo = crear_usuario_prueba("usuario_desactivar")
        respuesta = self.cliente.post(f"{URL_USUARIOS}{objetivo.pk}/desactivar/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertFalse(respuesta.data["is_active"])
