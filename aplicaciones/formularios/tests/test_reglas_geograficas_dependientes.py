"""
Pruebas de preguntas geograficas dependientes condicionales y flujo visual.
"""

import uuid

from django.test import TestCase

from aplicaciones.catalogos.constantes import TiposCatalogo
from aplicaciones.catalogos.models import Catalogo, ItemCatalogo
from aplicaciones.formularios.models import (
    AccionRegla,
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    OperadorRegla,
    Pregunta,
    ReglaPregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.formularios.reglas.visibilidad import (
    pregunta_obligatoria_efectiva,
    pregunta_visible_efectiva,
)
from aplicaciones.respuestas.mapeo_valores import asignar_valor_a_respuesta
from aplicaciones.respuestas.models import Respuesta
from aplicaciones.respuestas.servicios import (
    guardar_o_actualizar_respuesta,
    limpiar_respuestas_preguntas_ocultas,
    validar_formulario_sesion,
)
from aplicaciones.respuestas.selectores import obtener_preguntas_flujo_visual_sesion
from aplicaciones.respuestas.validadores_ubicacion_geografica import (
    validar_y_normalizar_ubicacion_geografica,
)
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima


class ReglasGeograficasDependientesTests(TestCase):
    """Pruebas del flujo P7 condicional con ubicacion geografica compuesta."""

    def setUp(self) -> None:
        self.catalogo_departamentos = Catalogo.objects.create(
            codigo="departamentos",
            nombre="Departamentos",
            tipo_catalogo=TiposCatalogo.GEOGRAFICO,
        )
        self.catalogo_municipios = Catalogo.objects.create(
            codigo="municipios",
            nombre="Municipios",
            tipo_catalogo=TiposCatalogo.JERARQUICO,
        )
        self.item_departamento = ItemCatalogo.objects.create(
            catalogo=self.catalogo_departamentos,
            codigo="15",
            nombre="Boyacá",
            valor="15",
        )
        self.item_municipio = ItemCatalogo.objects.create(
            catalogo=self.catalogo_municipios,
            codigo="15001",
            nombre="Tunja",
            valor="15001",
            item_padre=self.item_departamento,
        )

        self.formulario = Formulario.objects.create(
            codigo="form_geo_dep",
            nombre="Formulario geografico dependiente",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.PUBLICADO,
        )
        self.version = FormularioVersion.objects.create(
            formulario=self.formulario,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
        )
        self.seccion = SeccionFormulario.objects.create(
            formulario_version=self.version,
            codigo="SEC1",
            titulo="Seccion",
            orden=1,
        )
        self.p7 = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P7",
            texto="¿Ha cambiado de municipio?",
            tipo_pregunta=TipoPregunta.RADIO,
            orden=1,
            es_obligatoria=True,
        )
        self.p7_ant = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P7-ANT",
            texto="Indique el departamento y municipio donde residía anteriormente.",
            tipo_pregunta=TipoPregunta.UBICACION_GEOGRAFICA,
            orden=2,
            es_obligatoria=False,
            visible_por_defecto=False,
            limpiar_respuesta_al_ocultar=True,
            pregunta_origen_flujo=self.p7,
            usa_catalogo=True,
            catalogo_asociado=self.catalogo_municipios,
            codigo_catalogo_departamento="departamentos",
        )
        self.p8 = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P8",
            texto="Pregunta siguiente",
            tipo_pregunta=TipoPregunta.TEXTO_CORTO,
            orden=3,
            es_obligatoria=True,
        )
        ReglaPregunta.objects.create(
            pregunta_origen=self.p7,
            operador=OperadorRegla.EQUALS,
            valor_esperado={"valor": "si"},
            accion=AccionRegla.MOSTRAR,
            pregunta_destino=self.p7_ant,
        )
        ReglaPregunta.objects.create(
            pregunta_origen=self.p7,
            operador=OperadorRegla.EQUALS,
            valor_esperado={"valor": "si"},
            accion=AccionRegla.HACER_OBLIGATORIA,
            pregunta_destino=self.p7_ant,
        )

        self.sesion = SesionAnonima.objects.create(
            uuid_sesion=uuid.uuid4(),
            formulario=self.formulario,
            version_formulario=self.version,
            estado=EstadoSesionAnonima.EN_PROCESO,
        )

    def _guardar_respuesta(self, codigo: str, valor: object) -> None:
        guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta=codigo,
            valor=valor,
        )

    def test_ubicacion_geografica_normaliza_json(self) -> None:
        valor = {
            "departamento_codigo": "15",
            "departamento_nombre": "Boyacá",
            "municipio_codigo": "15001",
            "municipio_nombre": "Tunja",
        }
        normalizado = validar_y_normalizar_ubicacion_geografica(self.p7_ant, valor)
        self.assertEqual(normalizado["municipio_codigo"], "15001")

    def test_p7_ant_oculta_sin_respuesta_si(self) -> None:
        self._guardar_respuesta("P7", "no")
        self._guardar_respuesta("P8", "texto")
        resultado = validar_formulario_sesion(self.sesion.uuid_sesion)
        self.assertTrue(resultado["es_valido"])

    def test_p7_ant_obligatoria_y_pendiente_con_si(self) -> None:
        self._guardar_respuesta("P7", "si")
        resultado = validar_formulario_sesion(self.sesion.uuid_sesion)
        self.assertFalse(resultado["es_valido"])
        codigos_pendientes = {
            item["codigo"] for item in resultado["preguntas_pendientes"]
        }
        self.assertIn("P7-ANT", codigos_pendientes)

    def test_flujo_visual_inserta_dependiente_despues_de_origen(self) -> None:
        self._guardar_respuesta("P7", "si")
        preguntas_flujo = obtener_preguntas_flujo_visual_sesion(self.sesion)
        codigos = [pregunta.codigo for pregunta in preguntas_flujo]
        self.assertEqual(codigos.index("P7-ANT"), codigos.index("P7") + 1)

    def test_limpia_respuesta_al_ocultar_dependiente(self) -> None:
        valor_geo = {
            "departamento_codigo": "15",
            "departamento_nombre": "Boyacá",
            "municipio_codigo": "15001",
            "municipio_nombre": "Tunja",
        }
        self._guardar_respuesta("P7", "si")
        self._guardar_respuesta("P7-ANT", valor_geo)
        self._guardar_respuesta("P7", "no")

        respuesta = Respuesta.todos.get(sesion=self.sesion, pregunta=self.p7_ant)
        self.assertTrue(respuesta.esta_eliminado)

    def test_limpieza_explicita_preguntas_ocultas(self) -> None:
        valor_geo = {
            "departamento_codigo": "15",
            "departamento_nombre": "Boyacá",
            "municipio_codigo": "15001",
            "municipio_nombre": "Tunja",
        }
        self._guardar_respuesta("P7", "si")
        self._guardar_respuesta("P7-ANT", valor_geo)

        respuesta_p7 = Respuesta.objects.get(sesion=self.sesion, pregunta=self.p7)
        respuesta_p7.valor_texto = "no"
        respuesta_p7.save(update_fields=["valor_texto", "fecha_modificacion"])

        codigos_limpiados = limpiar_respuestas_preguntas_ocultas(self.sesion)
        self.assertIn("P7-ANT", codigos_limpiados)

    def test_visibilidad_y_obligatoriedad_efectiva(self) -> None:
        from aplicaciones.respuestas.selectores import evaluar_resultado_reglas_sesion

        self._guardar_respuesta("P7", "si")
        resultado = evaluar_resultado_reglas_sesion(self.sesion)
        self.assertTrue(pregunta_visible_efectiva(self.p7_ant, resultado))
        self.assertTrue(pregunta_obligatoria_efectiva(self.p7_ant, resultado))

        respuesta = Respuesta(pregunta=self.p7_ant, sesion=self.sesion)
        asignar_valor_a_respuesta(
            respuesta,
            TipoPregunta.UBICACION_GEOGRAFICA,
            {
                "departamento_codigo": "15",
                "departamento_nombre": "Boyacá",
                "municipio_codigo": "15001",
                "municipio_nombre": "Tunja",
            },
        )
        respuesta.save()
        self._guardar_respuesta("P8", "continuar")
        resultado_validacion = validar_formulario_sesion(self.sesion.uuid_sesion)
        self.assertTrue(resultado_validacion["es_valido"])
