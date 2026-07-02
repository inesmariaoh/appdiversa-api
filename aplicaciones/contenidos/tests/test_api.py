"""
Pruebas de la API publica de configuracion de interfaz.
"""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.contenidos.constantes import ValoresPorDefectoInterfaz
from aplicaciones.contenidos.models import ConfiguracionInterfaz, LogoInterfaz

URL_CONFIGURACION = "/api/v1/interfaz/configuracion/"

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


class ConfiguracionInterfazApiTests(TestCase):
    """Pruebas del endpoint de configuracion de interfaz."""

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_retorna_valores_por_defecto_sin_configuracion_activa(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="Inactiva",
            esta_activa=False,
        )

        respuesta = self.cliente.get(URL_CONFIGURACION)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertEqual(
            datos["nombre_aplicativo"],
            ValoresPorDefectoInterfaz.NOMBRE_APLICATIVO,
        )
        self.assertEqual(
            datos["nombre_corto"],
            ValoresPorDefectoInterfaz.NOMBRE_CORTO,
        )
        self.assertIsNone(datos["logo_principal"])
        self.assertEqual(datos["logo_principal_alt"], "")
        self.assertEqual(datos["logos"], [])

    def test_endpoint_retorna_200_con_configuracion_activa(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="DiversApp",
            nombre_corto="AppDiversa",
            descripcion_aplicativo="Descripcion institucional",
            texto_pie_pagina="Pie de pagina",
            color_primario="#4B2E83",
            color_secundario="#F2F2F2",
            color_acento="#D0006F",
            esta_activa=True,
        )

        respuesta = self.cliente.get(URL_CONFIGURACION)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertEqual(datos["nombre_aplicativo"], "DiversApp")
        self.assertEqual(datos["color_primario"], "#4B2E83")

    @override_settings(MEDIA_URL="/media/")
    def test_endpoint_retorna_urls_de_logos_si_existen(self) -> None:
        configuracion = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="ConLogo",
            esta_activa=True,
        )
        logo = LogoInterfaz.objects.create(
            configuracion_interfaz=configuracion,
            codigo="logo_principal",
            nombre="Logo principal",
            texto_alternativo="Logo principal de la app",
        )
        logo.imagen.save(
            "logo.gif",
            crear_imagen_prueba(),
            save=True,
        )

        respuesta = self.cliente.get(URL_CONFIGURACION)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        url_logo = datos["logo_principal"]
        self.assertIsNotNone(url_logo)
        self.assertIn("/media/interfaz/logos/", url_logo)
        self.assertTrue(url_logo.endswith(".gif"))
        self.assertEqual(datos["logo_principal_alt"], "Logo principal de la app")
        self.assertEqual(len(datos["logos"]), 1)
        self.assertEqual(datos["logos"][0]["codigo"], "logo_principal")

    def test_retorna_nuevos_campos_parametrizados(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="DiversApp",
            texto_titulo_seccion_encuestas="Encuestas disponibles",
            texto_descripcion_seccion_encuestas="Seleccione una encuesta",
            email_soporte="soporte@ejemplo.com",
            texto_terminos_condiciones="Terminos legales",
            texto_autorizacion_datos="Autorizacion de datos",
            texto_verificacion_exitosa_titulo="Verificacion OK",
            texto_verificacion_exitosa_cuerpo="Cuerpo verificacion",
            texto_confirmacion_envio_titulo="Enviado",
            texto_confirmacion_envio_subtitulo="Gracias",
            meta_titulo_seo="AppDiversa SEO",
            meta_descripcion_seo="Descripcion SEO",
            accion_lengua_senas_habilitada=True,
            url_lengua_senas="https://ejemplo.com/senas",
            texto_lengua_senas="Lengua de senas",
            esta_activa=True,
        )

        respuesta = self.cliente.get(URL_CONFIGURACION)
        datos = respuesta.json()
        self.assertEqual(datos["texto_titulo_seccion_encuestas"], "Encuestas disponibles")
        self.assertEqual(datos["email_soporte"], "soporte@ejemplo.com")
        self.assertTrue(datos["accion_lengua_senas_habilitada"])
        self.assertEqual(datos["url_lengua_senas"], "https://ejemplo.com/senas")

    def test_campos_lengua_senas_por_defecto(self) -> None:
        respuesta = self.cliente.get(URL_CONFIGURACION)
        datos = respuesta.json()
        self.assertFalse(datos["accion_lengua_senas_habilitada"])
        self.assertEqual(datos["url_lengua_senas"], "")
        self.assertEqual(datos["texto_lengua_senas"], "")

    def test_configuracion_no_incluye_contenido_accesible_por_defecto(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="DiversApp",
            esta_activa=True,
        )
        respuesta = self.cliente.get(URL_CONFIGURACION)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertNotIn("contenido_accesible", respuesta.json())

    def test_configuracion_incluye_contenido_accesible_con_parametro(self) -> None:
        from aplicaciones.internacionalizacion.models import Idioma, TraduccionContenido
        from aplicaciones.internacionalizacion.servicios import resolver_uuid_entidad

        Idioma.objects.create(
            codigo_iso="es",
            nombre="Espanol",
            nombre_nativo="Espanol",
            es_predeterminado=True,
        )
        Idioma.objects.create(
            codigo_iso="en",
            nombre="Ingles",
            nombre_nativo="English",
        )
        configuracion = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="DiversApp",
            texto_pie_pagina="Pie",
            esta_activa=True,
        )
        uuid_entidad = resolver_uuid_entidad(configuracion, "ConfiguracionInterfaz")
        TraduccionContenido.objects.create(
            idioma=Idioma.objects.get(codigo_iso="en"),
            entidad="ConfiguracionInterfaz",
            entidad_uuid=uuid_entidad,
            campo="nombre_aplicativo",
            valor_traducido="DiversApp EN",
            lectura_facil="Aplicacion diversa",
            esta_activa=True,
        )

        respuesta = self.cliente.get(
            URL_CONFIGURACION,
            {"idioma": "en", "incluir_accesibilidad": "true"},
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertIn("contenido_accesible", datos)
        self.assertEqual(
            datos["contenido_accesible"]["nombre_aplicativo"]["lectura_facil"],
            "Aplicacion diversa",
        )
        self.assertIn("texto_pie_pagina", datos["contenido_accesible"])
