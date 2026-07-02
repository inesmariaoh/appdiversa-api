"""
Pruebas de integracion de preguntas con catalogos parametrizables.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.catalogos.constantes import TiposCatalogo
from aplicaciones.catalogos.models import Catalogo
from aplicaciones.formularios.constantes import FuenteOpciones
from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    MensajesValidacion,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.formularios.servicios import obtener_fuente_opciones_pregunta

URL_ESTRUCTURA = "/api/v1/formularios/{uuid}/estructura/"


def crear_contexto_pregunta_catalogo() -> tuple[Formulario, SeccionFormulario, Catalogo]:
    """Crea formulario publicado, seccion y catalogo para pruebas."""
    formulario = Formulario.objects.create(
        codigo="form_cat",
        nombre="Formulario catalogo",
        tipo_formulario=TipoFormulario.ENCUESTA,
        estado=EstadoFormulario.PUBLICADO,
    )
    FormularioVersion.objects.create(
        formulario=formulario,
        numero_version=1,
        estado=EstadoFormulario.PUBLICADO,
        es_publicada=True,
        fecha_publicacion=timezone.now(),
    )
    version = formulario.versiones.first()
    seccion = SeccionFormulario.objects.create(
        formulario_version=version,
        codigo="sec_cat",
        titulo="Seccion catalogo",
        orden=1,
    )
    catalogo = Catalogo.objects.create(
        codigo="departamentos",
        nombre="Departamentos",
        tipo_catalogo=TiposCatalogo.GEOGRAFICO,
    )
    return formulario, seccion, catalogo


class PreguntaCatalogoModelTests(TestCase):
    """Pruebas del modelo Pregunta con catalogos."""

    def setUp(self) -> None:
        _, self.seccion, self.catalogo = crear_contexto_pregunta_catalogo()

    def test_pregunta_puede_asociarse_a_catalogo(self) -> None:
        pregunta = Pregunta(
            seccion=self.seccion,
            codigo="P_DEP",
            texto="Seleccione departamento",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=1,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo,
        )
        pregunta.full_clean()
        pregunta.save()
        self.assertEqual(pregunta.catalogo_asociado.codigo, "departamentos")

    def test_error_usa_catalogo_sin_catalogo_asociado(self) -> None:
        pregunta = Pregunta(
            seccion=self.seccion,
            codigo="P_ERR",
            texto="Sin catalogo",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=1,
            usa_catalogo=True,
        )
        with self.assertRaises(ValidationError) as contexto:
            pregunta.full_clean()
        self.assertIn("catalogo_asociado", contexto.exception.message_dict)

    def test_error_tipo_pregunta_no_permite_catalogo(self) -> None:
        pregunta = Pregunta(
            seccion=self.seccion,
            codigo="P_NUM",
            texto="Numero",
            tipo_pregunta=TipoPregunta.NUMERO,
            orden=1,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo,
        )
        with self.assertRaises(ValidationError) as contexto:
            pregunta.full_clean()
        self.assertIn("tipo_pregunta", contexto.exception.message_dict)

    def test_pregunta_dependiente_misma_version(self) -> None:
        padre = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P5_DEP",
            texto="Seleccione departamento",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=1,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo,
        )
        catalogo_mun = Catalogo.objects.create(
            codigo="municipios",
            nombre="Municipios",
            tipo_catalogo=TiposCatalogo.GEOGRAFICO,
        )
        hija = Pregunta(
            seccion=self.seccion,
            codigo="P_MUN",
            texto="Seleccione municipio",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=2,
            usa_catalogo=True,
            catalogo_asociado=catalogo_mun,
            pregunta_padre_catalogo=padre,
        )
        hija.full_clean()
        hija.save()
        self.assertEqual(hija.pregunta_padre_catalogo, padre)

    def test_error_pregunta_padre_es_la_misma(self) -> None:
        pregunta = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P_SELF",
            texto="Pregunta",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=1,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo,
        )
        pregunta.pregunta_padre_catalogo = pregunta
        with self.assertRaises(ValidationError) as contexto:
            pregunta.full_clean()
        self.assertIn("pregunta_padre_catalogo", contexto.exception.message_dict)

    def test_error_pregunta_padre_otra_version(self) -> None:
        otro_formulario = Formulario.objects.create(
            codigo="form_otro",
            nombre="Otro formulario",
            tipo_formulario=TipoFormulario.ENCUESTA,
        )
        otra_version = FormularioVersion.objects.create(
            formulario=otro_formulario,
            numero_version=1,
        )
        otra_seccion = SeccionFormulario.objects.create(
            formulario_version=otra_version,
            codigo="sec_otra",
            titulo="Otra seccion",
            orden=1,
        )
        padre_otra_version = Pregunta.objects.create(
            seccion=otra_seccion,
            codigo="P_OTRA",
            texto="Otra pregunta",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=1,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo,
        )
        hija = Pregunta(
            seccion=self.seccion,
            codigo="P_HIJA",
            texto="Hija",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=2,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo,
            pregunta_padre_catalogo=padre_otra_version,
        )
        with self.assertRaises(ValidationError) as contexto:
            hija.full_clean()
        self.assertEqual(
            contexto.exception.message_dict["pregunta_padre_catalogo"][0],
            MensajesValidacion.PREGUNTA_PADRE_OTRA_VERSION,
        )


class PreguntaCatalogoServicioTests(TestCase):
    """Pruebas del servicio de fuente de opciones."""

    def test_fuente_opciones_catalogo(self) -> None:
        _, seccion, catalogo = crear_contexto_pregunta_catalogo()
        pregunta = Pregunta.objects.create(
            seccion=seccion,
            codigo="P1",
            texto="Pregunta",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=1,
            usa_catalogo=True,
            catalogo_asociado=catalogo,
        )
        self.assertEqual(
            obtener_fuente_opciones_pregunta(pregunta),
            FuenteOpciones.CATALOGO,
        )

    def test_fuente_opciones_opciones(self) -> None:
        _, seccion, _ = crear_contexto_pregunta_catalogo()
        pregunta = Pregunta.objects.create(
            seccion=seccion,
            codigo="P2",
            texto="Pregunta",
            tipo_pregunta=TipoPregunta.RADIO,
            orden=1,
        )
        self.assertEqual(
            obtener_fuente_opciones_pregunta(pregunta),
            FuenteOpciones.OPCIONES,
        )


class PreguntaCatalogoApiTests(TestCase):
    """Pruebas de estructura de formulario con catalogos."""

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_estructura_retorna_catalogo_asociado(self) -> None:
        formulario, seccion, catalogo = crear_contexto_pregunta_catalogo()
        Pregunta.objects.create(
            seccion=seccion,
            codigo="P_DEP",
            texto="Seleccione departamento",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=1,
            usa_catalogo=True,
            catalogo_asociado=catalogo,
            permite_busqueda_catalogo=True,
            limite_items_catalogo=50,
        )

        respuesta = self.cliente.get(URL_ESTRUCTURA.format(uuid=formulario.uuid))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        pregunta = respuesta.json()["secciones"][0]["preguntas"][0]
        self.assertEqual(pregunta["fuente_opciones"], FuenteOpciones.CATALOGO)
        self.assertEqual(pregunta["catalogo_asociado"]["codigo"], "departamentos")
        self.assertEqual(
            pregunta["catalogo_asociado"]["endpoint_items"],
            "/api/v1/catalogos/departamentos/items/",
        )
        self.assertTrue(pregunta["permite_busqueda_catalogo"])
        self.assertEqual(pregunta["limite_items_catalogo"], 50)

    def test_estructura_retorna_fuente_opciones_opciones(self) -> None:
        formulario, seccion, _ = crear_contexto_pregunta_catalogo()
        Pregunta.objects.create(
            seccion=seccion,
            codigo="P_NUM",
            texto="Edad",
            tipo_pregunta=TipoPregunta.NUMERO,
            orden=1,
        )

        respuesta = self.cliente.get(URL_ESTRUCTURA.format(uuid=formulario.uuid))
        pregunta = respuesta.json()["secciones"][0]["preguntas"][0]
        self.assertEqual(pregunta["fuente_opciones"], FuenteOpciones.OPCIONES)
        self.assertIsNone(pregunta["catalogo_asociado"])
