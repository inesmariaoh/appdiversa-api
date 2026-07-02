"""
Pruebas de resolucion de correos desde configuracion de interfaz.
"""

from django.test import TestCase, override_settings

from aplicaciones.contenidos.models import ConfiguracionInterfaz
from aplicaciones.contenidos.servicios_correo import (
    obtener_email_remitente_notificaciones,
    obtener_email_soporte_configurado,
)


class ServiciosCorreoInterfazTests(TestCase):
    """Pruebas de correos de soporte y notificaciones administrables."""

    def setUp(self) -> None:
        ConfiguracionInterfaz.objects.filter(esta_activa=True).update(esta_activa=False)

    def test_obtener_email_soporte_desde_configuracion_activa(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App prueba",
            email_soporte="soporte@ejemplo.com",
            esta_activa=True,
        )
        self.assertEqual(
            obtener_email_soporte_configurado(),
            "soporte@ejemplo.com",
        )

    def test_obtener_email_soporte_vacio_sin_configuracion(self) -> None:
        self.assertEqual(obtener_email_soporte_configurado(), "")

    @override_settings(EMAIL_DEFAULT_FROM="noreply@entorno.test")
    def test_remitente_usa_configuracion_interfaz(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App prueba",
            email_remitente_notificaciones="notificaciones@ejemplo.com",
            esta_activa=True,
        )
        self.assertEqual(
            obtener_email_remitente_notificaciones(),
            "notificaciones@ejemplo.com",
        )

    @override_settings(EMAIL_DEFAULT_FROM="noreply@entorno.test")
    def test_remitente_usa_entorno_si_interfaz_vacia(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App prueba",
            email_remitente_notificaciones="",
            esta_activa=True,
        )
        self.assertEqual(
            obtener_email_remitente_notificaciones(),
            "noreply@entorno.test",
        )
