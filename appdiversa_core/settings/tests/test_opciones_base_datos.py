"""Pruebas de opciones de conexion MySQL."""

from django.test import SimpleTestCase
import environ

from appdiversa_core.settings.opciones_base_datos import construir_opciones_mysql


class OpcionesBaseDatosTest(SimpleTestCase):
    """Valida la parametrizacion SSL de MySQL."""

    def test_sin_ssl_devuelve_solo_charset(self) -> None:
        env = environ.Env()
        env.ENVIRON = {"DB_SSL_MODE": ""}

        opciones = construir_opciones_mysql(env)

        self.assertEqual(opciones, {"charset": "utf8mb4"})

    def test_ssl_required_agrega_modo(self) -> None:
        env = environ.Env()
        env.ENVIRON = {"DB_SSL_MODE": "REQUIRED"}

        opciones = construir_opciones_mysql(env)

        self.assertEqual(opciones["ssl_mode"], "REQUIRED")
        self.assertNotIn("ssl", opciones)

    def test_ssl_verify_ca_agrega_certificado(self) -> None:
        env = environ.Env()
        env.ENVIRON = {
            "DB_SSL_MODE": "VERIFY_CA",
            "DB_SSL_CA": "/etc/ssl/certs/ca.pem",
        }

        opciones = construir_opciones_mysql(env)

        self.assertEqual(opciones["ssl_mode"], "VERIFY_CA")
        self.assertEqual(opciones["ssl"], {"ca": "/etc/ssl/certs/ca.pem"})
