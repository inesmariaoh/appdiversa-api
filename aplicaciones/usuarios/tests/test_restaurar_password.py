"""
Pruebas de restauracion de contrasena.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.usuarios.constantes import MensajesAuth
from aplicaciones.usuarios.tests.helpers import (
    CONTRASENA_PRUEBA,
    URL_RESTAURAR_PASSWORD,
    URL_SOLICITAR_RESTAURAR,
    inicializar_entorno_usuarios,
)

User = get_user_model()


class RestaurarPasswordApiTests(TestCase):
    """Pruebas de endpoints de restauracion de contrasena."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.usuario = User.objects.create_user(
            username="restaurar_user",
            email="restaurar@example.com",
            password=CONTRASENA_PRUEBA,
        )

    def test_solicitud_correo_existente(self) -> None:
        respuesta = self.cliente.post(
            URL_SOLICITAR_RESTAURAR,
            {"email": "restaurar@example.com"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            respuesta.data["detalle"],
            MensajesAuth.SOLICITUD_RESTAURAR_CONTRASENA,
        )

    def test_solicitud_correo_inexistente_responde_generico(self) -> None:
        respuesta = self.cliente.post(
            URL_SOLICITAR_RESTAURAR,
            {"email": "noexiste@example.com"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            respuesta.data["detalle"],
            MensajesAuth.SOLICITUD_RESTAURAR_CONTRASENA,
        )

    def test_token_valido_cambia_contrasena(self) -> None:
        generador = PasswordResetTokenGenerator()
        uid = urlsafe_base64_encode(force_bytes(self.usuario.pk))
        token = generador.make_token(self.usuario)
        respuesta = self.cliente.post(
            URL_RESTAURAR_PASSWORD,
            {
                "uid": uid,
                "token": token,
                "password_nueva": "NuevaContrasena123!",
                "password_confirmacion": "NuevaContrasena123!",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["detalle"], MensajesAuth.CONTRASENA_RESTAURADA)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password("NuevaContrasena123!"))

    def test_token_invalido_retorna_400(self) -> None:
        uid = urlsafe_base64_encode(force_bytes(self.usuario.pk))
        respuesta = self.cliente.post(
            URL_RESTAURAR_PASSWORD,
            {
                "uid": uid,
                "token": "token-invalido",
                "password_nueva": "NuevaContrasena123!",
                "password_confirmacion": "NuevaContrasena123!",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_passwords_diferentes_retorna_400(self) -> None:
        generador = PasswordResetTokenGenerator()
        uid = urlsafe_base64_encode(force_bytes(self.usuario.pk))
        token = generador.make_token(self.usuario)
        respuesta = self.cliente.post(
            URL_RESTAURAR_PASSWORD,
            {
                "uid": uid,
                "token": token,
                "password_nueva": "NuevaContrasena123!",
                "password_confirmacion": "OtraContrasena123!",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
