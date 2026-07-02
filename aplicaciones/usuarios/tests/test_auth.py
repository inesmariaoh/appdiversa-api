"""
Pruebas de autenticacion Django del modulo de usuarios.
"""

from django.test import Client, TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.usuarios.constantes import MensajesAuth
from aplicaciones.usuarios.tests.helpers import (
    CONTRASENA_PRUEBA,
    URL_CAMBIAR_PASSWORD,
    URL_LOGIN,
    URL_LOGOUT,
    URL_ME,
    URL_PERFIL,
    autenticar_cliente,
    crear_usuario_prueba,
    inicializar_entorno_usuarios,
)


class AuthApiTests(TestCase):
    """Pruebas de endpoints de autenticacion."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.usuario = crear_usuario_prueba("usuario_auth", CONTRASENA_PRUEBA)

    def test_login_correcto_por_username(self) -> None:
        respuesta = self.cliente.post(
            URL_LOGIN,
            {"usuario": "usuario_auth", "password": CONTRASENA_PRUEBA},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["usuario"]["username"], "usuario_auth")
        self.assertIn("grupos", respuesta.data)
        self.assertIn("permisos", respuesta.data)
        self.assertIn("detalle", respuesta.data)

    def test_login_correcto_con_campo_username(self) -> None:
        respuesta = self.cliente.post(
            URL_LOGIN,
            {"username": "usuario_auth", "password": CONTRASENA_PRUEBA},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["usuario"]["username"], "usuario_auth")

    def test_login_correcto_por_email(self) -> None:
        respuesta = self.cliente.post(
            URL_LOGIN,
            {"usuario": "usuario_auth@example.com", "password": CONTRASENA_PRUEBA},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_login_incorrecto(self) -> None:
        respuesta = self.cliente.post(
            URL_LOGIN,
            {"usuario": "usuario_auth", "password": "incorrecta"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(respuesta.data["detalle"], MensajesAuth.CREDENCIALES_INVALIDAS)

    def test_login_sin_token_csrf_desde_spa(self) -> None:
        cliente_web = Client(enforce_csrf_checks=True)
        respuesta = cliente_web.post(
            URL_LOGIN,
            data='{"usuario": "usuario_auth", "password": "Contrasena123!"}',
            content_type="application/json",
            HTTP_ORIGIN="http://localhost:3000",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_login_credenciales_invalidas_mensaje_funcional(self) -> None:
        cliente_web = Client(enforce_csrf_checks=True)
        respuesta = cliente_web.post(
            URL_LOGIN,
            data='{"usuario": "usuario_auth", "password": "incorrecta"}',
            content_type="application/json",
            HTTP_ORIGIN="http://localhost:3000",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        cuerpo = respuesta.json()
        self.assertEqual(cuerpo["detalle"], MensajesAuth.CREDENCIALES_INVALIDAS)
        self.assertNotIn("CSRF", cuerpo["detalle"])

    def test_logout(self) -> None:
        autenticar_cliente(self.cliente, "usuario_auth", CONTRASENA_PRUEBA)
        respuesta = self.cliente.post(URL_LOGOUT)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_me_autenticado(self) -> None:
        autenticar_cliente(self.cliente, "usuario_auth", CONTRASENA_PRUEBA)
        respuesta = self.cliente.get(URL_ME)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["usuario"]["email"], "usuario_auth@example.com")
        self.assertIn("grupos", respuesta.data)

    def test_me_no_autenticado(self) -> None:
        respuesta = self.cliente.get(URL_ME)
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_perfil_get(self) -> None:
        autenticar_cliente(self.cliente, "usuario_auth", CONTRASENA_PRUEBA)
        respuesta = self.cliente.get(URL_PERFIL)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["username"], "usuario_auth")
        self.assertIn("fecha_ultimo_inicio_sesion", respuesta.data)
        self.assertEqual(respuesta.data["tipo_inicio_sesion_etiqueta"], "Correo electrónico")

    def test_perfil_patch(self) -> None:
        autenticar_cliente(self.cliente, "usuario_auth", CONTRASENA_PRUEBA)
        respuesta = self.cliente.patch(
            URL_PERFIL,
            {"first_name": "Nombre", "last_name": "Apellido"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["first_name"], "Nombre")
        self.assertEqual(respuesta.data["last_name"], "Apellido")

    def test_cambiar_password_correcto(self) -> None:
        autenticar_cliente(self.cliente, "usuario_auth", CONTRASENA_PRUEBA)
        respuesta = self.cliente.post(
            URL_CAMBIAR_PASSWORD,
            {
                "password_actual": CONTRASENA_PRUEBA,
                "password_nueva": "NuevaContrasena123!",
                "password_confirmacion": "NuevaContrasena123!",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_cambiar_password_incorrecto(self) -> None:
        autenticar_cliente(self.cliente, "usuario_auth", CONTRASENA_PRUEBA)
        respuesta = self.cliente.post(
            URL_CAMBIAR_PASSWORD,
            {
                "password_actual": "incorrecta",
                "password_nueva": "NuevaContrasena123!",
                "password_confirmacion": "NuevaContrasena123!",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
