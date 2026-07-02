"""
Pruebas de la aplicacion comun.
"""

from django.test import Client, SimpleTestCase


class VerificarSaludTests(SimpleTestCase):
    """Pruebas del endpoint de verificacion de salud del servicio."""

    def test_verificar_salud_retorna_estado_ok(self) -> None:
        cliente = Client()
        respuesta = cliente.get("/api/v1/salud/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), {"estado": "ok"})
