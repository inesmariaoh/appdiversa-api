"""
Pruebas del formulario de contacto publico.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.contenidos.models import ConfiguracionInterfaz
from aplicaciones.usuarios.constantes import MensajesContacto
from aplicaciones.usuarios.tests.helpers import URL_CONTACTO, inicializar_entorno_usuarios


class ContactoApiTests(TestCase):
    """Pruebas del endpoint de contacto publico."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_contacto_correcto(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="AppDiversa",
            email_soporte="soporte@example.com",
            esta_activa=True,
        )
        respuesta = self.cliente.post(
            URL_CONTACTO,
            {
                "nombre": "Usuario prueba",
                "correo": "usuario@example.com",
                "asunto": "Consulta",
                "mensaje": "Mensaje de prueba.",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["detalle"], MensajesContacto.ENVIADO)

    def test_contacto_sin_email_soporte_retorna_400(self) -> None:
        respuesta = self.cliente.post(
            URL_CONTACTO,
            {
                "nombre": "Usuario",
                "correo": "usuario@example.com",
                "asunto": "Consulta",
                "mensaje": "Mensaje.",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(respuesta.data["detalle"], MensajesContacto.SIN_EMAIL_SOPORTE)

    def test_email_invalido_retorna_400(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="AppDiversa",
            email_soporte="soporte@example.com",
            esta_activa=True,
        )
        respuesta = self.cliente.post(
            URL_CONTACTO,
            {
                "nombre": "Usuario",
                "correo": "correo-invalido",
                "asunto": "Consulta",
                "mensaje": "Mensaje.",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
