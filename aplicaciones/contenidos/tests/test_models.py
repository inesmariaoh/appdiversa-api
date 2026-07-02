"""
Pruebas de los modelos de configuracion de interfaz.
"""

from django.test import TestCase

from aplicaciones.contenidos.models import ConfiguracionInterfaz
from aplicaciones.contenidos.selectores import obtener_configuracion_interfaz_activa
from aplicaciones.contenidos.servicios import activar_configuracion_interfaz


class ConfiguracionInterfazModelTests(TestCase):
    """Pruebas del modelo ConfiguracionInterfaz."""

    def test_crear_configuracion_interfaz(self) -> None:
        configuracion = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="DiversApp",
            nombre_corto="AppDiversa",
            color_primario="#4B2E83",
        )

        self.assertEqual(configuracion.nombre_aplicativo, "DiversApp")
        self.assertTrue(configuracion.esta_activa)

    def test_obtener_configuracion_interfaz_activa(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="Activa",
            esta_activa=True,
        )
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="Inactiva",
            esta_activa=False,
        )

        configuracion_activa = obtener_configuracion_interfaz_activa()

        self.assertIsNotNone(configuracion_activa)
        self.assertEqual(configuracion_activa.nombre_aplicativo, "Activa")

    def test_activar_configuracion_desactiva_anteriores(self) -> None:
        configuracion_anterior = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="Anterior",
            esta_activa=True,
        )
        configuracion_nueva = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="Nueva",
            esta_activa=False,
        )

        activar_configuracion_interfaz(configuracion_nueva)

        configuracion_anterior.refresh_from_db()
        configuracion_nueva.refresh_from_db()
        self.assertFalse(configuracion_anterior.esta_activa)
        self.assertTrue(configuracion_nueva.esta_activa)

    def test_configuracion_permite_nuevos_textos(self) -> None:
        configuracion = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App parametrizada",
            texto_titulo_seccion_encuestas="Titulo encuestas",
            texto_descripcion_seccion_encuestas="Descripcion encuestas",
            email_soporte="contacto@ejemplo.com",
            texto_terminos_condiciones="Terminos",
            meta_titulo_seo="Meta titulo",
            accion_lengua_senas_habilitada=False,
        )
        self.assertEqual(configuracion.texto_titulo_seccion_encuestas, "Titulo encuestas")
        self.assertFalse(configuracion.accion_lengua_senas_habilitada)
