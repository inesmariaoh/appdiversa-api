"""
Pruebas del modelo LogoInterfaz y administracion de logos.
"""

from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from aplicaciones.contenidos.admin import LogoInterfazAdmin
from aplicaciones.contenidos.models import ConfiguracionInterfaz, LogoInterfaz
from aplicaciones.contenidos.servicios import resolver_url_logo_interfaz

IMAGEN_GIF_MINIMA = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00"
    b"\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00"
    b"\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02"
    b"\x44\x01\x00\x3b"
)


def crear_imagen_prueba(nombre: str = "logo.gif") -> SimpleUploadedFile:
    """Crea un archivo de imagen minimo para pruebas."""
    return SimpleUploadedFile(
        nombre,
        IMAGEN_GIF_MINIMA,
        content_type="image/gif",
    )


class LogoInterfazModelTests(TestCase):
    """Pruebas del modelo LogoInterfaz."""

    def setUp(self) -> None:
        self.configuracion = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App prueba",
            esta_activa=True,
        )

    def test_crear_logo_interfaz(self) -> None:
        logo = LogoInterfaz.objects.create(
            configuracion_interfaz=self.configuracion,
            codigo="logo_principal",
            nombre="Logo principal",
            texto_alternativo="Logo de la aplicacion",
        )

        self.assertEqual(logo.codigo, "logo_principal")
        self.assertEqual(logo.texto_alternativo, "Logo de la aplicacion")
        self.assertTrue(logo.esta_activo)

    def test_codigo_unico_por_configuracion_activa(self) -> None:
        LogoInterfaz.objects.create(
            configuracion_interfaz=self.configuracion,
            codigo="logo_principal",
            nombre="Logo principal",
        )

        with self.assertRaises(Exception):
            LogoInterfaz.objects.create(
                configuracion_interfaz=self.configuracion,
                codigo="logo_principal",
                nombre="Logo duplicado",
            )

    def test_soft_delete_logo(self) -> None:
        logo = LogoInterfaz.objects.create(
            configuracion_interfaz=self.configuracion,
            codigo="logo_secundario",
            nombre="Logo secundario",
        )

        logo.eliminar_logicamente()

        logo.refresh_from_db()
        self.assertTrue(logo.esta_eliminado)
        self.assertIsNone(LogoInterfaz.objects.filter(pk=logo.pk).first())

    def test_resolver_url_logo_interfaz_desde_imagen(self) -> None:
        logo = LogoInterfaz.objects.create(
            configuracion_interfaz=self.configuracion,
            codigo="logo_principal",
            nombre="Logo principal",
        )
        logo.imagen.save("logo.gif", crear_imagen_prueba(), save=True)

        url = resolver_url_logo_interfaz(logo)

        self.assertIsNotNone(url)
        self.assertIn("interfaz/logos/", url)


class LogoInterfazAdminTests(TestCase):
    """Pruebas basicas del admin de logos."""

    def test_admin_muestra_vista_previa_en_listado(self) -> None:
        configuracion = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App admin",
        )
        logo = LogoInterfaz.objects.create(
            configuracion_interfaz=configuracion,
            codigo="logo_principal",
            nombre="Logo principal",
            texto_alternativo="Alt logo",
        )
        logo.imagen.save("logo.gif", crear_imagen_prueba(), save=True)

        admin_site = AdminSite()
        admin_logos = LogoInterfazAdmin(LogoInterfaz, admin_site)
        html = admin_logos.vista_previa_lista(logo)

        self.assertIn("<img", str(html))
        self.assertIn("Alt logo", str(html))


class ResolverLogosInterfazTests(TestCase):
    """Pruebas de resolucion de logos para la API publica."""

    @override_settings(MEDIA_URL="/media/")
    def test_usa_logo_parametrizado_de_otra_configuracion_activa(self) -> None:
        from aplicaciones.contenidos.servicios import resolver_url_imagen_configuracion

        config_inactiva = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="Config inactiva",
            esta_activa=False,
        )
        config_activa = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="Config activa",
            esta_activa=True,
        )
        config_activa.logo_institucional.save(
            "logo_institucional.png",
            crear_imagen_prueba("legacy.png"),
            save=True,
        )

        logo = LogoInterfaz.objects.create(
            configuracion_interfaz=config_inactiva,
            codigo="logo_institucional",
            nombre="Logo institucional",
            texto_alternativo="DANE y SEN",
        )
        logo.imagen.save(
            "logos_dane_sen.png",
            crear_imagen_prueba("logos_dane_sen.png"),
            save=True,
        )

        url = resolver_url_imagen_configuracion(config_activa, "logo_institucional")

        self.assertIsNotNone(url)
        self.assertIn("logos_dane_sen", url)
        self.assertNotIn("legacy", url)

    @override_settings(MEDIA_URL="/media/")
    def test_prioriza_logo_de_configuracion_activa_sobre_otras(self) -> None:
        from aplicaciones.contenidos.servicios import resolver_url_imagen_configuracion

        config_activa = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="Config activa",
            esta_activa=True,
        )
        config_otra = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="Config otra",
            esta_activa=False,
        )

        logo_activa = LogoInterfaz.objects.create(
            configuracion_interfaz=config_activa,
            codigo="logo_principal",
            nombre="Logo activa",
        )
        logo_activa.imagen.save(
            "logo_activa.gif",
            crear_imagen_prueba("logo_activa.gif"),
            save=True,
        )

        logo_otra = LogoInterfaz.objects.create(
            configuracion_interfaz=config_otra,
            codigo="logo_principal",
            nombre="Logo otra",
        )
        logo_otra.imagen.save(
            "logo_otra.gif",
            crear_imagen_prueba("logo_otra.gif"),
            save=True,
        )

        url = resolver_url_imagen_configuracion(config_activa, "logo_principal")

        self.assertIsNotNone(url)
        self.assertIn("logo_activa", url)
        self.assertNotIn("logo_otra", url)
