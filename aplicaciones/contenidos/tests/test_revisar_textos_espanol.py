"""
Pruebas del servicio y comando de revision de textos en espanol.
"""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from aplicaciones.contenidos.models import ConfiguracionInterfaz
from aplicaciones.contenidos.revision_textos_espanol import (
    aplicar_correcciones_seguras,
    ejecutar_revision_textos,
)
from aplicaciones.notificaciones.models import PlantillaNotificacion


class RevisionTextosEspanolServicioTests(TestCase):
    """Pruebas unitarias de correcciones seguras de textos."""

    def test_aplica_correccion_conocida(self) -> None:
        resultado = aplicar_correcciones_seguras("Inicia sesion para continuar.")
        self.assertEqual(resultado, "Inicia sesión para continuar.")

    def test_no_modifica_palabra_exitoso(self) -> None:
        self.assertIsNone(
            aplicar_correcciones_seguras("Tu registro fue exitoso."),
        )

    def test_no_modifica_texto_ya_correcto(self) -> None:
        self.assertIsNone(
            aplicar_correcciones_seguras("Inicia sesión para continuar."),
        )

    def test_dry_run_detecta_cambios_sin_persistir(self) -> None:
        registro = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App sin tilde",
            descripcion_aplicativo="Informacion institucional sin tilde.",
            esta_activa=True,
        )

        reporte = ejecutar_revision_textos(aplicar=False)

        self.assertGreater(reporte.total_cambios, 0)
        registro.refresh_from_db()
        self.assertEqual(registro.descripcion_aplicativo, "Informacion institucional sin tilde.")

    def test_aplicar_persiste_correcciones_seguras(self) -> None:
        registro = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="AppDiversa",
            texto_pie_pagina="Proximamente mas encuestas.",
            esta_activa=True,
        )
        plantilla = PlantillaNotificacion.objects.create(
            codigo="prueba_textos",
            nombre="Restaurar contrasena",
            tipo="correo",
            asunto="Restaurar contrasena",
            contenido_html="<p>Inicia sesion</p>",
            contenido_texto="Inicia sesion",
            esta_activa=True,
        )

        reporte = ejecutar_revision_textos(aplicar=True)

        self.assertGreater(reporte.total_cambios, 0)
        registro.refresh_from_db()
        plantilla.refresh_from_db()
        self.assertEqual(registro.texto_pie_pagina, "Próximamente mas encuestas.")
        self.assertEqual(plantilla.nombre, "Restaurar contraseña")
        self.assertIn("Inicia sesión", plantilla.contenido_html)


class RevisionTextosEspanolComandoTests(TestCase):
    """Pruebas del management command revisar_textos_espanol."""

    def test_comando_dry_run_no_modifica_bd(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App",
            texto_autorizacion_datos="Autorizacion de datos personales.",
            esta_activa=True,
        )
        salida = StringIO()

        call_command("revisar_textos_espanol", "--dry-run", stdout=salida)

        registro = ConfiguracionInterfaz.objects.get()
        self.assertEqual(
            registro.texto_autorizacion_datos,
            "Autorizacion de datos personales.",
        )
        self.assertIn("Modo simulacion", salida.getvalue())

    def test_comando_aplicar_modifica_bd(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App",
            texto_autorizacion_datos="Autorizacion de datos personales.",
            esta_activa=True,
        )
        salida = StringIO()

        call_command("revisar_textos_espanol", "--aplicar", stdout=salida)

        registro = ConfiguracionInterfaz.objects.get()
        self.assertEqual(
            registro.texto_autorizacion_datos,
            "Autorización de datos personales.",
        )
        self.assertIn("Se aplicaron", salida.getvalue())
