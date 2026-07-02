"""
Pruebas de parametrizacion UI y portada de formularios.
"""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
    TipoTextoFormulario,
    TextoFormulario,
    Pregunta,
)

URL_DISPONIBLES = "/api/v1/formularios/disponibles/"
URL_ESTRUCTURA = "/api/v1/formularios/{uuid}/estructura/"

IMAGEN_GIF_MINIMA = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00"
    b"\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00"
    b"\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02"
    b"\x44\x01\x00\x3b"
)


def crear_imagen_portada() -> SimpleUploadedFile:
    """Crea un archivo de imagen minimo para pruebas."""
    return SimpleUploadedFile(
        "portada.gif",
        IMAGEN_GIF_MINIMA,
        content_type="image/gif",
    )


class FormularioPortadaTests(TestCase):
    """Pruebas de imagen de portada en formularios."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.formulario = Formulario.objects.create(
            codigo="form_portada",
            nombre="Formulario portada",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.PUBLICADO,
        )
        self.version = FormularioVersion.objects.create(
            formulario=self.formulario,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
            fecha_publicacion=timezone.now(),
        )
        seccion = SeccionFormulario.objects.create(
            formulario_version=self.version,
            codigo="sec_1",
            titulo="Seccion",
            orden=1,
        )
        Pregunta.objects.create(
            seccion=seccion,
            codigo="p1",
            texto="Pregunta",
            tipo_pregunta=TipoPregunta.NUMERO,
            orden=1,
        )

    def test_formulario_permite_imagen_portada(self) -> None:
        self.formulario.imagen_portada.save(
            "portada.gif",
            crear_imagen_portada(),
            save=True,
        )
        self.formulario.refresh_from_db()
        self.assertTrue(self.formulario.imagen_portada.name.endswith(".gif"))

    @override_settings(MEDIA_URL="/media/")
    def test_disponibles_retorna_imagen_portada(self) -> None:
        self.formulario.imagen_portada.save(
            "portada.gif",
            crear_imagen_portada(),
            save=True,
        )

        respuesta = self.cliente.get(URL_DISPONIBLES)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()[0]
        self.assertIsNotNone(datos["imagen_portada"])
        self.assertIn("/media/formularios/portadas/", datos["imagen_portada"])

    @override_settings(MEDIA_URL="/media/")
    def test_estructura_retorna_imagen_portada(self) -> None:
        self.formulario.imagen_portada.save(
            "portada.gif",
            crear_imagen_portada(),
            save=True,
        )

        respuesta = self.cliente.get(
            URL_ESTRUCTURA.format(uuid=self.formulario.uuid),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(respuesta.json()["imagen_portada"])

    def test_sin_imagen_portada_retorna_null(self) -> None:
        respuesta = self.cliente.get(URL_DISPONIBLES)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIsNone(respuesta.json()[0]["imagen_portada"])

    def test_disponibles_respeta_orden_parametrizado(self) -> None:
        self.formulario.estado = EstadoFormulario.BORRADOR
        self.formulario.save(update_fields=["estado"])
        formulario_primero = Formulario.objects.create(
            codigo="orden_1",
            nombre="Primero",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.PUBLICADO,
            orden=1,
        )
        formulario_segundo = Formulario.objects.create(
            codigo="orden_2",
            nombre="Segundo",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.PUBLICADO,
            orden=2,
        )
        FormularioVersion.objects.create(
            formulario=formulario_primero,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
            fecha_publicacion=timezone.now(),
        )
        FormularioVersion.objects.create(
            formulario=formulario_segundo,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
            fecha_publicacion=timezone.now(),
        )

        respuesta = self.cliente.get(URL_DISPONIBLES)
        codigos = [item["codigo"] for item in respuesta.json()]
        self.assertEqual(codigos[:2], ["orden_1", "orden_2"])


class TipoTextoFormularioTests(TestCase):
    """Pruebas de tipos de texto de formulario."""

    def test_tipos_nuevos_son_validos(self) -> None:
        tipos_nuevos = (
            TipoTextoFormulario.CONSENTIMIENTO_DATOS,
            TipoTextoFormulario.CONFIRMACION_ENVIO,
            TipoTextoFormulario.VERIFICACION_EXITOSA,
            TipoTextoFormulario.AUTORIZACION_DATOS,
            TipoTextoFormulario.RESUMEN_RESPUESTAS,
            TipoTextoFormulario.REGISTRO_OPCIONAL,
            TipoTextoFormulario.ENVIO_CORREO,
            TipoTextoFormulario.CONTACTO,
            TipoTextoFormulario.AYUDA_ACCESIBILIDAD,
        )
        formulario = Formulario.objects.create(
            codigo="form_textos",
            nombre="Formulario textos",
            tipo_formulario=TipoFormulario.ENCUESTA,
        )
        version = FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
        )
        for indice, tipo in enumerate(tipos_nuevos, start=1):
            texto = TextoFormulario.objects.create(
                formulario_version=version,
                tipo=tipo,
                contenido=f"Contenido {tipo}",
                orden=indice,
            )
            self.assertEqual(texto.tipo, tipo)

    def test_tipos_existentes_no_eliminados(self) -> None:
        tipos_existentes = (
            TipoTextoFormulario.INTRODUCCION,
            TipoTextoFormulario.DEFINICION,
            TipoTextoFormulario.CONSENTIMIENTO,
            TipoTextoFormulario.TERMINOS,
            TipoTextoFormulario.AGRADECIMIENTO,
            TipoTextoFormulario.AYUDA,
            TipoTextoFormulario.CIERRE,
        )
        for tipo in tipos_existentes:
            self.assertIn(tipo, TipoTextoFormulario.values)
