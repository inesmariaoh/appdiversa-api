"""
Pruebas de verificacion de correo electronico de usuarios.
"""

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.usuarios.models import VerificacionCorreo
from aplicaciones.usuarios.tests.helpers import (
    CONTRASENA_PRUEBA,
    URL_REGISTRO_CORREO,
    crear_usuario_prueba,
    inicializar_entorno_usuarios,
)

URL_VERIFICAR = "/api/v1/auth/verificar-correo/"
URL_REENVIAR = "/api/v1/auth/reenviar-verificacion/"


def _construir_credenciales_verificacion(usuario) -> tuple[str, str]:
    """Construye el uid y token validos para un usuario."""
    generador = PasswordResetTokenGenerator()
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = generador.make_token(usuario)
    return uid, token


class VerificacionCorreoTests(TestCase):
    """Pruebas del flujo de verificacion de correo."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_registro_crea_verificacion_pendiente(self) -> None:
        respuesta = self.cliente.post(
            URL_REGISTRO_CORREO,
            {"correo": "nuevo@example.com", "contrasena": CONTRASENA_PRUEBA},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        verificacion = VerificacionCorreo.objects.get(usuario__email="nuevo@example.com")
        self.assertFalse(verificacion.verificado)

    def test_verificar_con_token_valido(self) -> None:
        usuario = crear_usuario_prueba("verificable", email="verificable@example.com")
        uid, token = _construir_credenciales_verificacion(usuario)
        respuesta = self.cliente.post(
            URL_VERIFICAR,
            {"uid": uid, "token": token},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        verificacion = VerificacionCorreo.objects.get(usuario=usuario)
        self.assertTrue(verificacion.verificado)

    def test_verificar_con_token_invalido(self) -> None:
        usuario = crear_usuario_prueba("token_malo", email="token_malo@example.com")
        uid, _ = _construir_credenciales_verificacion(usuario)
        respuesta = self.cliente.post(
            URL_VERIFICAR,
            {"uid": uid, "token": "token-invalido"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reenviar_a_correo_inexistente_no_revela(self) -> None:
        respuesta = self.cliente.post(
            URL_REENVIAR,
            {"email": "inexistente@example.com"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_reenviar_a_usuario_pendiente(self) -> None:
        crear_usuario_prueba("pendiente", email="pendiente@example.com")
        respuesta = self.cliente.post(
            URL_REENVIAR,
            {"email": "pendiente@example.com"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
