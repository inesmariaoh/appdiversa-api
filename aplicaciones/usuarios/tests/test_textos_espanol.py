"""
Pruebas de textos visibles en espanol del modulo de usuarios.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.contenidos.models import ConfiguracionInterfaz
from aplicaciones.usuarios.constantes import (
    MensajesAuth,
    MensajesContacto,
    MensajesCopiaRespuestas,
)
from aplicaciones.usuarios.tests.helpers import (
    CONTRASENA_PRUEBA,
    URL_CONTACTO,
    URL_RESTAURAR_PASSWORD,
    URL_SOLICITAR_RESTAURAR,
    inicializar_entorno_usuarios,
)

User = get_user_model()


class TextosEspanolUsuariosApiTests(TestCase):
    """Verifica mensajes funcionales principales en espanol correcto."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.usuario = User.objects.create_user(
            username="textos_user",
            email="textos@example.com",
            password=CONTRASENA_PRUEBA,
        )

    def test_mensajes_auth_tienen_tildes(self) -> None:
        self.assertIn("sesión", MensajesAuth.LOGIN_CORRECTO)
        self.assertIn("contraseña", MensajesAuth.CONTRASENA_CAMBIADA)
        self.assertIn("autenticación", MensajesAuth.NO_AUTENTICADO)

    def test_solicitud_restaurar_contrasena_mensaje_institucional(self) -> None:
        respuesta = self.cliente.post(
            URL_SOLICITAR_RESTAURAR,
            {"email": "textos@example.com"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            respuesta.data["detalle"],
            MensajesAuth.SOLICITUD_RESTAURAR_CONTRASENA,
        )
        self.assertIn("contraseña", respuesta.data["detalle"])

    def test_restaurar_contrasena_exitoso(self) -> None:
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

    def test_contacto_mensaje_enviado(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="AppDiversa",
            email_soporte="soporte@example.com",
            esta_activa=True,
        )
        respuesta = self.cliente.post(
            URL_CONTACTO,
            {
                "nombre": "Usuario",
                "correo": "usuario@example.com",
                "asunto": "Consulta",
                "mensaje": "Mensaje de prueba.",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["detalle"], MensajesContacto.ENVIADO)

    def test_mensaje_copia_respuestas_tiene_tildes(self) -> None:
        self.assertIn("correo", MensajesCopiaRespuestas.ENVIADA)
        self.assertIn("válido", MensajesCopiaRespuestas.CORREO_INVALIDO)
