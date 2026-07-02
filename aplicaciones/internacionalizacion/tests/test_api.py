"""
Pruebas de integracion de internacionalizacion con API de formularios.
"""

import uuid

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    OpcionRespuesta,
    Pregunta,
    SeccionFormulario,
    TextoFormulario,
    TipoFormulario,
    TipoPregunta,
    TipoTextoFormulario,
)
from aplicaciones.internacionalizacion.models import Idioma, TraduccionContenido
from aplicaciones.internacionalizacion.servicios import (
    guardar_traduccion,
    resolver_uuid_entidad,
)

URL_ESTRUCTURA = "/api/v1/formularios/{uuid}/estructura/"
URL_TRADUCCIONES = "/api/v1/internacionalizacion/traducciones/"


class FormularioI18nApiTests(TestCase):
    """Pruebas del endpoint de estructura con traducciones."""

    def setUp(self) -> None:
        self.cliente = APIClient()
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
        self.formulario = Formulario.objects.create(
            codigo="form_i18n_api",
            nombre="Encuesta de Discriminacion",
            descripcion="Descripcion en espanol",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.PUBLICADO,
        )
        version = FormularioVersion.objects.create(
            formulario=self.formulario,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
            fecha_publicacion=timezone.now(),
        )
        TextoFormulario.objects.create(
            formulario_version=version,
            tipo=TipoTextoFormulario.INTRODUCCION,
            titulo="Intro",
            contenido="Contenido intro espanol",
            orden=1,
        )
        seccion = SeccionFormulario.objects.create(
            formulario_version=version,
            codigo="cap_i",
            titulo="Capitulo I",
            orden=1,
        )
        pregunta = Pregunta.objects.create(
            seccion=seccion,
            codigo="p1",
            texto="Pregunta en espanol",
            tipo_pregunta=TipoPregunta.RADIO,
            orden=1,
        )
        OpcionRespuesta.objects.create(
            pregunta=pregunta,
            codigo="opc_1",
            etiqueta="Opcion espanol",
            valor="1",
            orden=1,
        )

        uuid_formulario = resolver_uuid_entidad(self.formulario, "Formulario")
        guardar_traduccion(
            codigo_idioma="en",
            entidad="Formulario",
            entidad_uuid=uuid_formulario,
            campo="nombre",
            valor_traducido="Discrimination Survey",
        )
        uuid_pregunta = resolver_uuid_entidad(pregunta, "Pregunta")
        guardar_traduccion(
            codigo_idioma="en",
            entidad="Pregunta",
            entidad_uuid=uuid_pregunta,
            campo="texto",
            valor_traducido="Question in English",
        )
        self.pregunta = pregunta
        self.uuid_pregunta = uuid_pregunta
        self.texto_formulario = version.textos.first()

    def test_endpoint_estructura_sin_idioma(self) -> None:
        respuesta = self.cliente.get(
            URL_ESTRUCTURA.format(uuid=self.formulario.uuid),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()["nombre"], "Encuesta de Discriminacion")
        self.assertEqual(
            respuesta.json()["secciones"][0]["preguntas"][0]["texto"],
            "Pregunta en espanol",
        )

    def test_endpoint_estructura_con_idioma(self) -> None:
        respuesta = self.cliente.get(
            URL_ESTRUCTURA.format(uuid=self.formulario.uuid),
            {"idioma": "en"},
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()["nombre"], "Discrimination Survey")
        self.assertEqual(
            respuesta.json()["secciones"][0]["preguntas"][0]["texto"],
            "Question in English",
        )

    def test_estructura_incluye_contenido_accesible_en_pregunta(self) -> None:
        TraduccionContenido.objects.filter(
            entidad="Pregunta",
            entidad_uuid=self.uuid_pregunta,
            campo="texto",
        ).update(lectura_facil="Easy read question")

        respuesta = self.cliente.get(
            URL_ESTRUCTURA.format(uuid=self.formulario.uuid),
            {"idioma": "en"},
        )
        pregunta = respuesta.json()["secciones"][0]["preguntas"][0]
        self.assertIn("contenido_accesible", pregunta)
        self.assertEqual(
            pregunta["contenido_accesible"]["texto"]["lectura_facil"],
            "Easy read question",
        )
        self.assertIn("tooltip", pregunta["contenido_accesible"])

    def test_estructura_incluye_contenido_accesible_en_texto_formulario(self) -> None:
        uuid_texto = resolver_uuid_entidad(self.texto_formulario, "TextoFormulario")
        TraduccionContenido.objects.create(
            idioma=Idioma.objects.get(codigo_iso="en"),
            entidad="TextoFormulario",
            entidad_uuid=uuid_texto,
            campo="contenido",
            valor_traducido="Intro content EN",
            lectura_facil="Intro lectura facil",
            esta_activa=True,
        )

        respuesta = self.cliente.get(
            URL_ESTRUCTURA.format(uuid=self.formulario.uuid),
            {"idioma": "en"},
        )
        texto = respuesta.json()["textos"][0]
        self.assertIn("contenido_accesible", texto)
        self.assertEqual(
            texto["contenido_accesible"]["contenido"]["lectura_facil"],
            "Intro lectura facil",
        )

    def test_estructura_contenido_accesible_vacio_sin_traduccion(self) -> None:
        respuesta = self.cliente.get(
            URL_ESTRUCTURA.format(uuid=self.formulario.uuid),
            {"idioma": "en"},
        )
        tooltip = respuesta.json()["secciones"][0]["preguntas"][0][
            "contenido_accesible"
        ]["tooltip"]
        self.assertEqual(tooltip["lectura_facil"], "")
        self.assertIsNone(tooltip["archivo_audio"])
        self.assertEqual(tooltip["metadatos"], {})

    def test_endpoint_traducciones_retorna_campos_multimodales(self) -> None:
        entidad_uuid = uuid.uuid4()
        TraduccionContenido.objects.create(
            idioma=Idioma.objects.get(codigo_iso="en"),
            entidad="Pregunta",
            entidad_uuid=entidad_uuid,
            campo="texto",
            valor_traducido="Question",
            lectura_facil="Easy question",
            texto_alternativo="Alt text",
            transcripcion="Audio transcript",
            metadatos={"tipo": "audio"},
            esta_activa=True,
        )

        respuesta = self.cliente.get(
            URL_TRADUCCIONES,
            {"idioma": "en", "entidad_uuid": str(entidad_uuid)},
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()[0]
        self.assertEqual(datos["lectura_facil"], "Easy question")
        self.assertEqual(datos["texto_alternativo"], "Alt text")
        self.assertEqual(datos["transcripcion"], "Audio transcript")
        self.assertEqual(datos["metadatos"], {"tipo": "audio"})
        self.assertTrue(datos["esta_activa"])
