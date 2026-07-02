"""
Pruebas de preguntas con catalogos geograficos parametrizables.
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.catalogos.constantes import TiposCatalogo
from aplicaciones.catalogos.models import Catalogo
from aplicaciones.formularios.catalogo_geografico import (
    es_pregunta_catalogo_geografico,
    obtener_dependientes_geograficos_ordenados,
)
from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.formularios.tests.test_catalogo_pregunta import (
    crear_contexto_pregunta_catalogo,
)

URL_ESTRUCTURA = "/api/v1/formularios/{uuid}/estructura/"


class CatalogoGeograficoServicioTests(TestCase):
    """Pruebas del servicio de preguntas geograficas."""

    def setUp(self) -> None:
        _, self.seccion, self.catalogo_departamentos = crear_contexto_pregunta_catalogo()
        self.catalogo_municipios = Catalogo.objects.create(
            codigo="municipios",
            nombre="Municipios",
            tipo_catalogo=TiposCatalogo.JERARQUICO,
        )
        self.catalogo_ocupaciones = Catalogo.objects.create(
            codigo="ocupaciones",
            nombre="Ocupaciones",
            tipo_catalogo=TiposCatalogo.GENERAL,
        )

    def test_detecta_pregunta_geografica_por_tipo_catalogo(self) -> None:
        pregunta = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P_DEP",
            texto="Departamento",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=1,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo_departamentos,
        )
        self.assertTrue(es_pregunta_catalogo_geografico(pregunta))

    def test_detecta_dependiente_geografico_por_cadena(self) -> None:
        padre = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P_DEP",
            texto="Departamento",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=1,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo_departamentos,
        )
        hija = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P_MUN",
            texto="Municipio",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=2,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo_municipios,
            pregunta_padre_catalogo=padre,
        )
        self.assertTrue(es_pregunta_catalogo_geografico(hija))

    def test_no_marca_catalogo_general_como_geografico(self) -> None:
        pregunta = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P_OCUP",
            texto="Ocupacion",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=1,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo_ocupaciones,
        )
        self.assertFalse(es_pregunta_catalogo_geografico(pregunta))

    def test_obtiene_dependientes_geograficos_en_cadena(self) -> None:
        pais = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P_PAIS",
            texto="Pais",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=1,
            usa_catalogo=True,
            catalogo_asociado=Catalogo.objects.create(
                codigo="paises",
                nombre="Paises",
                tipo_catalogo=TiposCatalogo.GEOGRAFICO,
            ),
        )
        departamento = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P_DEP",
            texto="Departamento",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=2,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo_departamentos,
            pregunta_padre_catalogo=pais,
        )
        municipio = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P_MUN",
            texto="Municipio",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=3,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo_municipios,
            pregunta_padre_catalogo=departamento,
        )

        dependientes = obtener_dependientes_geograficos_ordenados(pais)
        self.assertEqual([item.codigo for item in dependientes], ["P_DEP", "P_MUN"])
        dependientes_departamento = obtener_dependientes_geograficos_ordenados(departamento)
        self.assertEqual([item.codigo for item in dependientes_departamento], ["P_MUN"])


class CatalogoGeograficoApiTests(TestCase):
    """Pruebas de metadata geografica en la estructura del formulario."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        formulario, self.seccion, self.catalogo_departamentos = (
            crear_contexto_pregunta_catalogo()
        )
        formulario.estado = EstadoFormulario.PUBLICADO
        formulario.save(update_fields=["estado"])
        version = formulario.versiones.first()
        version.estado = EstadoFormulario.PUBLICADO
        version.es_publicada = True
        version.fecha_publicacion = timezone.now()
        version.save(
            update_fields=["estado", "es_publicada", "fecha_publicacion"],
        )
        self.formulario = formulario
        self.departamento = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P_DEP",
            texto="Departamento de residencia",
            descripcion="Seleccione una opcion en cada lista.",
            tooltip="Departamento",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=1,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo_departamentos,
        )
        self.catalogo_municipios = Catalogo.objects.create(
            codigo="municipios_geo",
            nombre="Municipios",
            tipo_catalogo=TiposCatalogo.JERARQUICO,
        )
        self.municipio = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P_MUN",
            texto="Ciudad o Municipio",
            descripcion="Seleccione ciudad",
            tooltip="Ciudad o Municipio",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=2,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo_municipios,
            pregunta_padre_catalogo=self.departamento,
        )

    def test_estructura_expone_metadata_geografica(self) -> None:
        respuesta = self.cliente.get(
            URL_ESTRUCTURA.format(uuid=self.formulario.uuid),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        preguntas = respuesta.json()["secciones"][0]["preguntas"]
        departamento = next(item for item in preguntas if item["codigo"] == "P_DEP")
        municipio = next(item for item in preguntas if item["codigo"] == "P_MUN")

        self.assertTrue(departamento["es_pregunta_geografica"])
        self.assertEqual(
            departamento["catalogo_asociado"]["tipo_catalogo"],
            TiposCatalogo.GEOGRAFICO,
        )
        self.assertEqual(
            [item["codigo"] for item in departamento["preguntas_dependientes_geograficas"]],
            ["P_MUN"],
        )
        self.assertTrue(municipio["es_pregunta_geografica"])
        self.assertEqual(municipio["pregunta_padre_catalogo"]["codigo"], "P_DEP")
