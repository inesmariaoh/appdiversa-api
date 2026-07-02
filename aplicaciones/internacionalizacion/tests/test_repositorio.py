"""
Pruebas de integracion internacionalizacion con repositorio documental.
"""

import uuid

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.archivos.constantes import OrigenArchivo, TipoArchivo
from aplicaciones.archivos.servicios import guardar_archivo
from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.internacionalizacion.models import Idioma, TraduccionContenido
from aplicaciones.internacionalizacion.servicios import (
    obtener_contenido_accesible,
    resolver_uuid_entidad,
)

CONTENIDO_PNG_MINIMO = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

URL_ESTRUCTURA = "/api/v1/formularios/{uuid}/estructura/"


class InternacionalizacionRepositorioTests(TestCase):
    """Pruebas de contenido accesible con archivos del repositorio."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        Idioma.objects.create(
            codigo_iso="es",
            nombre="Espanol",
            nombre_nativo="Espanol",
            es_predeterminado=True,
        )
        self.idioma_en = Idioma.objects.create(
            codigo_iso="en",
            nombre="Ingles",
            nombre_nativo="English",
        )
        self.formulario = Formulario.objects.create(
            codigo="form_repo_i18n",
            nombre="Formulario repo",
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
        seccion = SeccionFormulario.objects.create(
            formulario_version=version,
            codigo="sec",
            titulo="Seccion",
            orden=1,
        )
        self.pregunta = Pregunta.objects.create(
            seccion=seccion,
            codigo="P1",
            texto="Pregunta",
            tipo_pregunta=TipoPregunta.RADIO,
            orden=1,
        )
        self.uuid_pregunta = resolver_uuid_entidad(self.pregunta, "Pregunta")

    def test_contenido_accesible_con_repositorio_imagen(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="accesible.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.INTERNACIONALIZACION,
            es_publico=True,
        )
        TraduccionContenido.objects.create(
            idioma=self.idioma_en,
            entidad="Pregunta",
            entidad_uuid=self.uuid_pregunta,
            campo="texto",
            valor_traducido="Question",
            repositorio_imagen=archivo,
            esta_activa=True,
        )

        contenido = obtener_contenido_accesible(
            entidad="Pregunta",
            entidad_id=str(self.uuid_pregunta),
            campo="texto",
            codigo_idioma="en",
        )
        self.assertIsNotNone(contenido["archivo_imagen"])
        self.assertIn("media/", contenido["archivo_imagen"])

    def test_estructura_formulario_url_repositorio(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="pregunta.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.INTERNACIONALIZACION,
            es_publico=True,
        )
        TraduccionContenido.objects.create(
            idioma=self.idioma_en,
            entidad="Pregunta",
            entidad_uuid=self.uuid_pregunta,
            campo="texto",
            valor_traducido="Question EN",
            repositorio_imagen=archivo,
            esta_activa=True,
        )

        respuesta = self.cliente.get(
            URL_ESTRUCTURA.format(uuid=self.formulario.uuid),
            {"idioma": "en"},
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        imagen = respuesta.json()["secciones"][0]["preguntas"][0][
            "contenido_accesible"
        ]["texto"]["archivo_imagen"]
        self.assertIsNotNone(imagen)
        self.assertIn("media/", imagen)
