"""
Pruebas de eliminacion (baja logica) de la cuenta propia del usuario.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.usuarios.tests.helpers import (
    CONTRASENA_PRUEBA,
    autenticar_cliente,
    crear_usuario_prueba,
    inicializar_entorno_usuarios,
)

User = get_user_model()

URL_ELIMINAR_CUENTA = "/api/v1/auth/eliminar-cuenta/"


class EliminarCuentaTests(TestCase):
    """Pruebas del flujo de eliminacion de cuenta propia."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_eliminar_cuenta_desactiva_usuario(self) -> None:
        crear_usuario_prueba("eliminable", email="eliminable@example.com")
        autenticar_cliente(self.cliente, "eliminable")
        respuesta = self.cliente.post(
            URL_ELIMINAR_CUENTA,
            {"password": CONTRASENA_PRUEBA},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        usuario = User.objects.get(username="eliminable")
        self.assertFalse(usuario.is_active)

    def test_eliminar_cuenta_password_incorrecta(self) -> None:
        crear_usuario_prueba("password_malo", email="password_malo@example.com")
        autenticar_cliente(self.cliente, "password_malo")
        respuesta = self.cliente.post(
            URL_ELIMINAR_CUENTA,
            {"password": "OtraClave999!"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        usuario = User.objects.get(username="password_malo")
        self.assertTrue(usuario.is_active)

    def test_eliminar_cuenta_requiere_autenticacion(self) -> None:
        respuesta = self.cliente.post(
            URL_ELIMINAR_CUENTA,
            {"password": CONTRASENA_PRUEBA},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cuenta_eliminada_no_puede_iniciar_sesion(self) -> None:
        crear_usuario_prueba("sin_acceso", email="sin_acceso@example.com")
        autenticar_cliente(self.cliente, "sin_acceso")
        self.cliente.post(
            URL_ELIMINAR_CUENTA,
            {"password": CONTRASENA_PRUEBA},
            format="json",
        )
        cliente_nuevo = APIClient()
        respuesta = autenticar_cliente(cliente_nuevo, "sin_acceso")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
