"""
Pruebas de parametrizacion de textos del flujo de formularios.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.archivos.constantes import (
    EstadoArchivo,
    OrigenArchivo,
    TipoArchivo,
)
from aplicaciones.archivos.models import ArchivoRepositorio
from aplicaciones.contenidos.constantes import ValoresPorDefectoFlujoFormulario
from aplicaciones.contenidos.models import ConfiguracionFlujoFormulario, ConfiguracionInterfaz
from aplicaciones.contenidos.servicios_flujo_formulario import (
    activar_configuracion_flujo_formulario,
    construir_bloque_flujo_formulario_publico,
)
from aplicaciones.internacionalizacion.models import Idioma, TraduccionContenido

URL_CONFIGURACION = "/api/v1/interfaz/configuracion/"
URL_IMAGEN_EXITO = "https://res.cloudinary.com/demo/image/upload/exito.png"


def crear_archivo_imagen_exito() -> ArchivoRepositorio:
    """Crea un archivo de repositorio publico apto para la pantalla de exito."""
    return ArchivoRepositorio.objects.create(
        nombre_original="img_enc_enviada_exito.png",
        nombre_fisico="exito.png",
        extension="png",
        mime_type="image/png",
        tamano_bytes=0,
        checksum_sha256="",
        tipo_archivo=TipoArchivo.IMAGEN,
        ruta_relativa="externo/cloudinary/img_enc_enviada_exito.png",
        url_publica=URL_IMAGEN_EXITO,
        es_publico=True,
        origen=OrigenArchivo.CONFIGURACION,
        estado=EstadoArchivo.ACTIVO,
    )


class ConfiguracionFlujoFormularioModelTests(TestCase):
    """Pruebas del modelo ConfiguracionFlujoFormulario."""

    def test_solo_una_configuracion_activa_en_clean(self) -> None:
        ConfiguracionFlujoFormulario.objects.create(esta_activa=True)
        segunda = ConfiguracionFlujoFormulario(esta_activa=True)
        with self.assertRaises(ValidationError):
            segunda.full_clean()

    def test_activar_desactiva_las_demas(self) -> None:
        primera = ConfiguracionFlujoFormulario.objects.create(esta_activa=True)
        segunda = ConfiguracionFlujoFormulario.objects.create(esta_activa=False)
        activar_configuracion_flujo_formulario(segunda)
        primera.refresh_from_db()
        segunda.refresh_from_db()
        self.assertFalse(primera.esta_activa)
        self.assertTrue(segunda.esta_activa)


class ConfiguracionFlujoFormularioServicioTests(TestCase):
    """Pruebas de servicios de textos del flujo de formularios."""

    def test_valores_por_defecto_sin_configuracion(self) -> None:
        bloque = construir_bloque_flujo_formulario_publico()
        self.assertEqual(
            bloque["modal_salir"]["titulo"],
            ValoresPorDefectoFlujoFormulario.MODAL_SALIR_TITULO,
        )
        self.assertIsNone(bloque["terminos"]["contenido"])

    def test_configuracion_activa_devuelve_textos(self) -> None:
        ConfiguracionFlujoFormulario.objects.create(
            esta_activa=True,
            modal_salir_titulo="Titulo personalizado",
            terminos_p1="Parrafo personalizado",
        )
        bloque = construir_bloque_flujo_formulario_publico()
        self.assertEqual(bloque["modal_salir"]["titulo"], "Titulo personalizado")
        self.assertEqual(bloque["terminos"]["parrafo_1"], "Parrafo personalizado")

    def test_terminos_contenido_tiene_prioridad_sobre_parrafos(self) -> None:
        ConfiguracionFlujoFormulario.objects.create(
            esta_activa=True,
            terminos_contenido="Texto completo de terminos",
            terminos_p1="Parrafo que no se usa como contenido completo",
        )
        bloque = construir_bloque_flujo_formulario_publico()
        self.assertEqual(bloque["terminos"]["contenido"], "Texto completo de terminos")
        self.assertEqual(
            bloque["terminos"]["parrafo_1"],
            "Parrafo que no se usa como contenido completo",
        )

    def test_terminos_incluye_botones_y_enlace_administrables(self) -> None:
        bloque_defecto = construir_bloque_flujo_formulario_publico()
        self.assertEqual(
            bloque_defecto["terminos"]["boton_aceptar"],
            ValoresPorDefectoFlujoFormulario.TERMINOS_BOTON_ACEPTAR,
        )
        self.assertEqual(
            bloque_defecto["terminos"]["boton_cerrar"],
            ValoresPorDefectoFlujoFormulario.TERMINOS_BOTON_CERRAR,
        )
        self.assertEqual(
            bloque_defecto["terminos"]["enlace_terminos"],
            ValoresPorDefectoFlujoFormulario.TERMINOS_ENLACE,
        )
        self.assertEqual(
            bloque_defecto["terminos"]["texto_enlace_ley"],
            ValoresPorDefectoFlujoFormulario.TERMINOS_ENLACE_LEY,
        )
        self.assertIn(
            "Política de Protección",
            bloque_defecto["terminos"]["texto_enlace_politica_datos"],
        )

        ConfiguracionFlujoFormulario.objects.create(
            esta_activa=True,
            terminos_boton_aceptar="Comenzar encuesta",
            terminos_boton_cerrar="Salir",
            terminos_enlace="Ver terminos",
        )
        bloque = construir_bloque_flujo_formulario_publico()
        self.assertEqual(bloque["terminos"]["boton_aceptar"], "Comenzar encuesta")
        self.assertEqual(bloque["terminos"]["boton_cerrar"], "Salir")
        self.assertEqual(bloque["terminos"]["enlace_terminos"], "Ver terminos")

    def test_envio_exitoso_sin_imagen_usa_alt_por_defecto(self) -> None:
        flujo_sin_imagen = ConfiguracionFlujoFormulario(esta_activa=False)
        bloque = construir_bloque_flujo_formulario_publico(flujo=flujo_sin_imagen)
        self.assertIn("envio_exitoso", bloque)
        self.assertIsNone(bloque["envio_exitoso"]["imagen_url"])
        self.assertEqual(
            bloque["envio_exitoso"]["imagen_alt"],
            ValoresPorDefectoFlujoFormulario.ENVIO_EXITO_IMAGEN_ALT,
        )

    def test_envio_exitoso_con_imagen_y_alt_personalizado(self) -> None:
        archivo = crear_archivo_imagen_exito()
        ConfiguracionFlujoFormulario.objects.create(
            esta_activa=True,
            img_enc_enviada_exito=archivo,
            img_enc_enviada_exito_alt="Gracias por responder",
        )
        bloque = construir_bloque_flujo_formulario_publico()
        self.assertEqual(bloque["envio_exitoso"]["imagen_url"], URL_IMAGEN_EXITO)
        self.assertEqual(
            bloque["envio_exitoso"]["imagen_alt"],
            "Gracias por responder",
        )

    def test_email_soporte_usa_configuracion_interfaz(self) -> None:
        interfaz = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App",
            email_soporte="soporte@ejemplo.com",
            esta_activa=True,
        )
        ConfiguracionFlujoFormulario.objects.create(
            esta_activa=True,
            configuracion_interfaz=interfaz,
        )
        bloque = construir_bloque_flujo_formulario_publico(interfaz=interfaz)
        self.assertEqual(bloque["terminos"]["email_soporte"], "soporte@ejemplo.com")


class ConfiguracionFlujoFormularioApiTests(TestCase):
    """Pruebas del endpoint publico de configuracion con flujo_formulario."""

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_endpoint_incluye_flujo_formulario_por_defecto(self) -> None:
        respuesta = self.cliente.get(URL_CONFIGURACION)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertIn("flujo_formulario", datos)
        self.assertIn("modal_salir", datos["flujo_formulario"])
        self.assertIn("modal_sesion", datos["flujo_formulario"])
        self.assertIn("modal_guardado", datos["flujo_formulario"])
        self.assertIn("terminos", datos["flujo_formulario"])
        self.assertIn("envio_exitoso", datos["flujo_formulario"])

    def test_endpoint_expone_imagen_envio_exitoso_absoluta(self) -> None:
        archivo = crear_archivo_imagen_exito()
        ConfiguracionFlujoFormulario.objects.create(
            esta_activa=True,
            img_enc_enviada_exito=archivo,
        )
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App",
            esta_activa=True,
        )
        respuesta = self.cliente.get(URL_CONFIGURACION)
        self.assertEqual(
            respuesta.json()["flujo_formulario"]["envio_exitoso"]["imagen_url"],
            URL_IMAGEN_EXITO,
        )

    def test_endpoint_con_configuracion_activa_y_flujo(self) -> None:
        interfaz = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="AppDiversa",
            esta_activa=True,
        )
        ConfiguracionFlujoFormulario.objects.create(
            esta_activa=True,
            configuracion_interfaz=interfaz,
            modal_guardado_titulo="Guardado custom",
        )
        respuesta = self.cliente.get(URL_CONFIGURACION)
        self.assertEqual(
            respuesta.json()["flujo_formulario"]["modal_guardado"]["titulo"],
            "Guardado custom",
        )

    def test_traduccion_flujo_formulario(self) -> None:
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
        flujo = ConfiguracionFlujoFormulario.objects.create(
            esta_activa=True,
            modal_sesion_titulo="Inicia sesión",
        )
        TraduccionContenido.objects.create(
            idioma=Idioma.objects.get(codigo_iso="en"),
            entidad="ConfiguracionFlujoFormulario",
            entidad_uuid=flujo.uuid,
            campo="modal_sesion_titulo",
            valor_traducido="Sign in or register",
            esta_activa=True,
        )
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App",
            esta_activa=True,
        )
        respuesta = self.cliente.get(URL_CONFIGURACION, {"idioma": "en"})
        self.assertEqual(
            respuesta.json()["flujo_formulario"]["modal_sesion"]["titulo"],
            "Sign in or register",
        )
