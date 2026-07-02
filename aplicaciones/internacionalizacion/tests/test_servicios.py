"""
Pruebas de servicios de internacionalizacion.
"""

import uuid

from django.test import TestCase

from aplicaciones.catalogos.constantes import TiposCatalogo
from aplicaciones.catalogos.models import Catalogo
from aplicaciones.contenidos.models import ConfiguracionInterfaz
from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    OpcionRespuesta,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.internacionalizacion.models import Idioma, TraduccionContenido
from aplicaciones.internacionalizacion.servicios import (
    guardar_traduccion,
    listar_traducciones,
    obtener_contenido_accesible,
    obtener_texto,
    obtener_traduccion,
    resolver_uuid_entidad,
)


class InternacionalizacionServiciosTests(TestCase):
    """Pruebas de servicios de traduccion de contenido."""

    def setUp(self) -> None:
        self.idioma_es = Idioma.objects.create(
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
        self.uuid_formulario = uuid.uuid4()

    def test_obtener_texto_traducido(self) -> None:
        guardar_traduccion(
            codigo_idioma="en",
            entidad="Formulario",
            entidad_uuid=self.uuid_formulario,
            campo="nombre",
            valor_traducido="Discrimination Survey",
        )
        texto = obtener_texto(
            codigo_idioma="en",
            entidad="Formulario",
            entidad_uuid=self.uuid_formulario,
            campo="nombre",
            texto_original="Encuesta de Discriminacion",
        )
        self.assertEqual(texto, "Discrimination Survey")

    def test_obtener_texto_original_sin_traduccion(self) -> None:
        texto = obtener_texto(
            codigo_idioma="en",
            entidad="Formulario",
            entidad_uuid=self.uuid_formulario,
            campo="nombre",
            texto_original="Encuesta de Discriminacion",
        )
        self.assertEqual(texto, "Encuesta de Discriminacion")

    def test_obtener_texto_idioma_predeterminado(self) -> None:
        guardar_traduccion(
            codigo_idioma="en",
            entidad="Formulario",
            entidad_uuid=self.uuid_formulario,
            campo="nombre",
            valor_traducido="Survey",
        )
        texto = obtener_texto(
            codigo_idioma="es",
            entidad="Formulario",
            entidad_uuid=self.uuid_formulario,
            campo="nombre",
            texto_original="Encuesta",
        )
        self.assertEqual(texto, "Encuesta")

    def test_guardar_traduccion_actualiza_existente(self) -> None:
        primera = guardar_traduccion(
            codigo_idioma="en",
            entidad="Pregunta",
            entidad_uuid=uuid.uuid4(),
            campo="texto",
            valor_traducido="First",
        )
        segunda = guardar_traduccion(
            codigo_idioma="en",
            entidad="Pregunta",
            entidad_uuid=primera.entidad_uuid,
            campo="texto",
            valor_traducido="Updated",
        )
        self.assertEqual(primera.pk, segunda.pk)
        self.assertEqual(segunda.valor_traducido, "Updated")

    def test_listar_traducciones_con_filtros(self) -> None:
        guardar_traduccion(
            codigo_idioma="en",
            entidad="Catalogo",
            entidad_uuid=uuid.uuid4(),
            campo="nombre",
            valor_traducido="Departments",
        )
        traducciones = listar_traducciones(codigo_idioma="en", entidad="Catalogo")
        self.assertEqual(len(traducciones), 1)

    def test_obtener_traduccion(self) -> None:
        entidad_uuid = uuid.uuid4()
        guardar_traduccion(
            codigo_idioma="en",
            entidad="OpcionRespuesta",
            entidad_uuid=entidad_uuid,
            campo="etiqueta",
            valor_traducido="Woman",
        )
        traduccion = obtener_traduccion(
            codigo_idioma="en",
            entidad="OpcionRespuesta",
            entidad_uuid=entidad_uuid,
            campo="etiqueta",
        )
        self.assertIsNotNone(traduccion)
        self.assertEqual(traduccion.valor_traducido, "Woman")

    def test_traducir_formulario(self) -> None:
        formulario = Formulario.objects.create(
            codigo="form_i18n",
            nombre="Encuesta",
            tipo_formulario=TipoFormulario.ENCUESTA,
        )
        uuid_entidad = resolver_uuid_entidad(formulario, "Formulario")
        guardar_traduccion(
            codigo_idioma="en",
            entidad="Formulario",
            entidad_uuid=uuid_entidad,
            campo="nombre",
            valor_traducido="Survey",
        )
        texto = obtener_texto("en", "Formulario", uuid_entidad, "nombre", formulario.nombre)
        self.assertEqual(texto, "Survey")

    def test_traducir_pregunta(self) -> None:
        formulario = Formulario.objects.create(
            codigo="form_preg",
            nombre="Formulario",
            tipo_formulario=TipoFormulario.ENCUESTA,
        )
        from aplicaciones.formularios.models import FormularioVersion

        version = FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
        )
        seccion = SeccionFormulario.objects.create(
            formulario_version=version,
            codigo="sec",
            titulo="Seccion",
            orden=1,
        )
        pregunta = Pregunta.objects.create(
            seccion=seccion,
            codigo="P1",
            texto="Cuantos anos tiene?",
            tipo_pregunta=TipoPregunta.NUMERO,
            orden=1,
        )
        uuid_entidad = resolver_uuid_entidad(pregunta, "Pregunta")
        guardar_traduccion(
            codigo_idioma="en",
            entidad="Pregunta",
            entidad_uuid=uuid_entidad,
            campo="texto",
            valor_traducido="How old are you?",
        )
        texto = obtener_texto("en", "Pregunta", uuid_entidad, "texto", pregunta.texto)
        self.assertEqual(texto, "How old are you?")

    def test_traducir_opcion(self) -> None:
        formulario = Formulario.objects.create(
            codigo="form_opc",
            nombre="Formulario",
            tipo_formulario=TipoFormulario.ENCUESTA,
        )
        from aplicaciones.formularios.models import FormularioVersion

        version = FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
        )
        seccion = SeccionFormulario.objects.create(
            formulario_version=version,
            codigo="sec",
            titulo="Seccion",
            orden=1,
        )
        pregunta = Pregunta.objects.create(
            seccion=seccion,
            codigo="P1",
            texto="Sexo",
            tipo_pregunta=TipoPregunta.RADIO,
            orden=1,
        )
        opcion = OpcionRespuesta.objects.create(
            pregunta=pregunta,
            codigo="M",
            etiqueta="Masculino",
            valor="M",
            orden=1,
        )
        uuid_entidad = resolver_uuid_entidad(opcion, "OpcionRespuesta")
        guardar_traduccion(
            codigo_idioma="en",
            entidad="OpcionRespuesta",
            entidad_uuid=uuid_entidad,
            campo="etiqueta",
            valor_traducido="Male",
        )
        texto = obtener_texto(
            "en",
            "OpcionRespuesta",
            uuid_entidad,
            "etiqueta",
            opcion.etiqueta,
        )
        self.assertEqual(texto, "Male")

    def test_traducir_catalogo(self) -> None:
        catalogo = Catalogo.objects.create(
            codigo="departamentos",
            nombre="Departamentos",
            tipo_catalogo=TiposCatalogo.GEOGRAFICO,
        )
        uuid_entidad = resolver_uuid_entidad(catalogo, "Catalogo")
        guardar_traduccion(
            codigo_idioma="en",
            entidad="Catalogo",
            entidad_uuid=uuid_entidad,
            campo="nombre",
            valor_traducido="Departments",
        )
        texto = obtener_texto("en", "Catalogo", uuid_entidad, "nombre", catalogo.nombre)
        self.assertEqual(texto, "Departments")

    def test_traducir_parametrizacion_ui(self) -> None:
        configuracion = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="AppDiversa",
            descripcion_aplicativo="Descripcion",
            texto_pie_pagina="Pie de pagina",
        )
        uuid_entidad = resolver_uuid_entidad(configuracion, "ConfiguracionInterfaz")
        guardar_traduccion(
            codigo_idioma="en",
            entidad="ConfiguracionInterfaz",
            entidad_uuid=uuid_entidad,
            campo="nombre_aplicativo",
            valor_traducido="AppDiversa EN",
        )
        texto = obtener_texto(
            "en",
            "ConfiguracionInterfaz",
            uuid_entidad,
            "nombre_aplicativo",
            configuracion.nombre_aplicativo,
        )
        self.assertEqual(texto, "AppDiversa EN")

    def test_traducir_nuevos_campos_configuracion_interfaz(self) -> None:
        from rest_framework.test import APIClient

        configuracion = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="AppDiversa",
            texto_titulo_seccion_encuestas="Encuestas",
            meta_titulo_seo="Titulo SEO",
            esta_activa=True,
        )
        uuid_entidad = resolver_uuid_entidad(configuracion, "ConfiguracionInterfaz")
        guardar_traduccion(
            codigo_idioma="en",
            entidad="ConfiguracionInterfaz",
            entidad_uuid=uuid_entidad,
            campo="texto_titulo_seccion_encuestas",
            valor_traducido="Surveys",
        )
        guardar_traduccion(
            codigo_idioma="en",
            entidad="ConfiguracionInterfaz",
            entidad_uuid=uuid_entidad,
            campo="meta_titulo_seo",
            valor_traducido="SEO Title",
        )

        cliente = APIClient()
        respuesta = cliente.get(
            "/api/v1/interfaz/configuracion/",
            {"idioma": "en"},
        )
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(datos["texto_titulo_seccion_encuestas"], "Surveys")
        self.assertEqual(datos["meta_titulo_seo"], "SEO Title")

    def test_auditoria_no_rompe_creacion(self) -> None:
        idioma = Idioma.objects.create(
            codigo_iso="qu",
            nombre="Quechua",
            nombre_nativo="Runasimi",
        )
        traduccion = TraduccionContenido.objects.create(
            idioma=idioma,
            entidad="Formulario",
            entidad_uuid=uuid.uuid4(),
            campo="nombre",
            valor_traducido="Formulario",
        )
        self.assertFalse(idioma.esta_eliminado)
        self.assertFalse(traduccion.esta_eliminado)
        self.assertIsNotNone(idioma.fecha_creacion)

    def test_obtener_contenido_accesible_vacio_sin_traduccion(self) -> None:
        contenido = obtener_contenido_accesible(
            entidad="Formulario",
            entidad_id=str(self.uuid_formulario),
            campo="nombre",
            codigo_idioma="en",
        )
        self.assertEqual(contenido["lectura_facil"], "")
        self.assertEqual(contenido["texto_alternativo"], "")
        self.assertIsNone(contenido["archivo_audio"])
        self.assertEqual(contenido["metadatos"], {})

    def test_obtener_contenido_accesible_retorna_lectura_facil(self) -> None:
        TraduccionContenido.objects.create(
            idioma=self.idioma_en,
            entidad="Formulario",
            entidad_uuid=self.uuid_formulario,
            campo="nombre",
            valor_traducido="Survey",
            lectura_facil="Encuesta en lectura facil",
            esta_activa=True,
        )
        contenido = obtener_contenido_accesible(
            entidad="Formulario",
            entidad_id=str(self.uuid_formulario),
            campo="nombre",
            codigo_idioma="en",
        )
        self.assertEqual(contenido["lectura_facil"], "Encuesta en lectura facil")

    def test_obtener_contenido_accesible_retorna_metadatos(self) -> None:
        metadatos = {"nivel_lectura": "basico"}
        TraduccionContenido.objects.create(
            idioma=self.idioma_en,
            entidad="Formulario",
            entidad_uuid=self.uuid_formulario,
            campo="nombre",
            valor_traducido="Survey",
            metadatos=metadatos,
            esta_activa=True,
        )
        contenido = obtener_contenido_accesible(
            entidad="Formulario",
            entidad_id=str(self.uuid_formulario),
            campo="nombre",
            codigo_idioma="en",
        )
        self.assertEqual(contenido["metadatos"], metadatos)
