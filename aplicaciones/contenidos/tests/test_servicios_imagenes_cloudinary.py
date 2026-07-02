"""Pruebas de sincronizacion de imagenes Cloudinary."""

from django.test import TestCase

from aplicaciones.archivos.models import ArchivoRepositorio
from aplicaciones.contenidos.constantes import CodigosLogoInterfaz
from aplicaciones.contenidos.models import ConfiguracionInterfaz, LogoInterfaz
from aplicaciones.contenidos.servicios_imagenes_cloudinary import (
    RECURSOS_IMAGENES_CLOUDINARY,
    sincronizar_recursos_imagenes_cloudinary,
)
from aplicaciones.formularios.models import Formulario


class ServiciosImagenesCloudinaryTest(TestCase):
    """Valida la parametrizacion de recursos visuales externos."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.configuracion = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App prueba",
            esta_activa=True,
        )
        cls.formulario = Formulario.objects.create(
            uuid="11111111-1111-1111-1111-111111111111",
            codigo="PRU-001",
            nombre="Encuesta prueba",
            tipo_formulario="encuesta",
            imagen_portada="formularios/portadas/image_ecu_disponible.png",
        )
        LogoInterfaz.objects.create(
            configuracion_interfaz=cls.configuracion,
            codigo=CodigosLogoInterfaz.INSTITUCIONAL,
            nombre="Logo institucional",
            imagen="interfaz/logos/logos_dane_sen.png",
            orden=3,
        )
        LogoInterfaz.objects.create(
            configuracion_interfaz=cls.configuracion,
            codigo=CodigosLogoInterfaz.PRINCIPAL,
            nombre="Logo principal",
            imagen="interfaz/logos/Propuesta_2.jpg",
            orden=1,
        )

    def test_sincronizar_crea_archivos_y_vincula_relaciones(self) -> None:
        sincronizar_recursos_imagenes_cloudinary()

        archivo_portada = ArchivoRepositorio.objects.get(
            metadatos__codigo_recurso="image_ecu_disponible",
        )
        self.assertEqual(
            archivo_portada.url_publica,
            RECURSOS_IMAGENES_CLOUDINARY["image_ecu_disponible"].url,
        )

        self.formulario.refresh_from_db()
        self.assertEqual(
            self.formulario.imagen_portada_repositorio_id,
            archivo_portada.pk,
        )

        logo_institucional = LogoInterfaz.objects.get(
            codigo=CodigosLogoInterfaz.INSTITUCIONAL,
        )
        self.assertEqual(
            logo_institucional.archivo_repositorio.url_publica,
            RECURSOS_IMAGENES_CLOUDINARY["logos_dane_sen"].url,
        )

        self.configuracion.refresh_from_db()
        self.assertIsNotNone(self.configuracion.logo_principal_repositorio_id)
