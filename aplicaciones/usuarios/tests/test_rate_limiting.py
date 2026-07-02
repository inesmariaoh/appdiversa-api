"""
Pruebas de limitacion de tasa en endpoints publicos sensibles.
"""

from unittest import mock

from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from aplicaciones.comun.throttling import ScopeThrottle
from aplicaciones.usuarios.tests.helpers import URL_LOGIN

LIMITE_LOGIN_PRUEBA = "2/min"


class RateLimitingLoginTests(TestCase):
    """Verifica que el login aplica limitacion de tasa por ambito."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        cache.clear()

    def tearDown(self) -> None:
        cache.clear()

    def test_login_excede_limite_retorna_429(self) -> None:
        credenciales = {"usuario": "inexistente", "password": "incorrecta"}
        tasas = {ScopeThrottle.LOGIN: LIMITE_LOGIN_PRUEBA}
        with mock.patch.dict(ScopedRateThrottle.THROTTLE_RATES, tasas):
            primera = self.cliente.post(URL_LOGIN, credenciales, format="json")
            segunda = self.cliente.post(URL_LOGIN, credenciales, format="json")
            tercera = self.cliente.post(URL_LOGIN, credenciales, format="json")

        self.assertNotEqual(primera.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertNotEqual(segunda.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(tercera.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_login_sin_limite_configurado_no_bloquea(self) -> None:
        credenciales = {"usuario": "inexistente", "password": "incorrecta"}
        for _ in range(5):
            respuesta = self.cliente.post(URL_LOGIN, credenciales, format="json")
            self.assertNotEqual(
                respuesta.status_code,
                status.HTTP_429_TOO_MANY_REQUESTS,
            )
