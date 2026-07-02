"""
Pruebas de registro de usuarios.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.usuarios.constantes import GrupoSistema
from aplicaciones.usuarios.tests.helpers import (
    CONTRASENA_PRUEBA,
    URL_REGISTRO,
    inicializar_entorno_usuarios,
)

User = get_user_model()


class RegistroApiTests(TestCase):
    """Pruebas del endpoint de registro publico."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_registro_correcto(self) -> None:
        respuesta = self.cliente.post(
            URL_REGISTRO,
            {
                "username": "nuevo_encuestado",
                "email": "nuevo@example.com",
                "password": CONTRASENA_PRUEBA,
                "password_confirmacion": CONTRASENA_PRUEBA,
                "first_name": "Nuevo",
                "last_name": "Usuario",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        usuario = User.objects.get(username="nuevo_encuestado")
        self.assertTrue(
            usuario.groups.filter(name=GrupoSistema.ENCUESTADO).exists(),
        )

    def test_username_duplicado(self) -> None:
        User.objects.create_user(username="duplicado", password=CONTRASENA_PRUEBA)
        respuesta = self.cliente.post(
            URL_REGISTRO,
            {
                "username": "duplicado",
                "email": "otro@example.com",
                "password": CONTRASENA_PRUEBA,
                "password_confirmacion": CONTRASENA_PRUEBA,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_duplicado(self) -> None:
        User.objects.create_user(
            username="user1",
            email="repetido@example.com",
            password=CONTRASENA_PRUEBA,
        )
        respuesta = self.cliente.post(
            URL_REGISTRO,
            {
                "username": "user2",
                "email": "repetido@example.com",
                "password": CONTRASENA_PRUEBA,
                "password_confirmacion": CONTRASENA_PRUEBA,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_debil(self) -> None:
        respuesta = self.cliente.post(
            URL_REGISTRO,
            {
                "username": "debil",
                "email": "debil@example.com",
                "password": "123",
                "password_confirmacion": "123",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_passwords_diferentes(self) -> None:
        respuesta = self.cliente.post(
            URL_REGISTRO,
            {
                "username": "distintas",
                "email": "distintas@example.com",
                "password": CONTRASENA_PRUEBA,
                "password_confirmacion": "OtraContrasena123!",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
