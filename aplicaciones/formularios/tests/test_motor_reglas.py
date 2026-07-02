"""
Pruebas del motor avanzado de reglas del form engine.
"""

import uuid
from decimal import Decimal

from django.test import TestCase

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
from aplicaciones.formularios.reglas.evaluador import evaluar_operador, evaluar_reglas
from aplicaciones.formularios.reglas.normalizadores import (
    normalizar_valor_esperado,
    normalizar_valor_respuesta,
)
from aplicaciones.formularios.reglas.servicio import evaluar_reglas_sesion
from aplicaciones.respuestas.excepciones import SesionRespuestaNoExisteError
from aplicaciones.respuestas.mapeo_valores import asignar_valor_a_respuesta
from aplicaciones.respuestas.models import Respuesta
from aplicaciones.sesiones_anonimas.models import SesionAnonima


class EvaluadorOperadoresTests(TestCase):
    """Pruebas de evaluacion de operadores de reglas."""

    def test_equals_verdadero(self) -> None:
        self.assertTrue(evaluar_operador(25, OperadorRegla.EQUALS, 25))

    def test_equals_falso(self) -> None:
        self.assertFalse(evaluar_operador(25, OperadorRegla.EQUALS, 30))

    def test_not_equals(self) -> None:
        self.assertTrue(evaluar_operador("no", OperadorRegla.NOT_EQUALS, "si"))

    def test_contains_con_lista(self) -> None:
        self.assertTrue(
            evaluar_operador(
                ["si", "tal vez"],
                OperadorRegla.CONTAINS,
                "si",
            ),
        )

    def test_contains_con_texto(self) -> None:
        self.assertTrue(
            evaluar_operador(
                "respuesta larga",
                OperadorRegla.CONTAINS,
                "larga",
            ),
        )

    def test_gt_con_numero(self) -> None:
        self.assertTrue(evaluar_operador(30, OperadorRegla.GT, 18))

    def test_lt_con_numero(self) -> None:
        self.assertTrue(evaluar_operador(10, OperadorRegla.LT, 18))

    def test_in_con_lista(self) -> None:
        self.assertTrue(
            evaluar_operador(
                "si",
                OperadorRegla.IN,
                ["si", "no"],
            ),
        )

    def test_normalizar_valor_esperado_valor(self) -> None:
        self.assertEqual(
            normalizar_valor_esperado({"valor": "si"}),
            "si",
        )

    def test_normalizar_valor_esperado_valores(self) -> None:
        self.assertEqual(
            normalizar_valor_esperado({"valores": ["si", "no"]}),
            ["si", "no"],
        )


class MotorReglasAccionesTests(TestCase):
    """Pruebas de acciones del motor de reglas."""

    def setUp(self) -> None:
        self.formulario = Formulario.objects.create(
            codigo="form_reglas",
            nombre="Formulario reglas",
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
            titulo="Seccion 1",
            orden=1,
        )
        self.seccion_destino = SeccionFormulario.objects.create(
            formulario_version=self.version,
            codigo="SEC2",
            titulo="Seccion 2",
            orden=2,
        )
        self.p1 = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P1",
            texto="Pregunta 1",
            tipo_pregunta=TipoPregunta.NUMERO,
            orden=1,
        )
        self.p2 = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="P2",
            texto="Pregunta 2",
            tipo_pregunta=TipoPregunta.TEXTO_CORTO,
            orden=2,
        )
        self.p3 = Pregunta.objects.create(
            seccion=self.seccion_destino,
            codigo="P3",
            texto="Pregunta 3",
            tipo_pregunta=TipoPregunta.TEXTO_CORTO,
            orden=1,
            es_obligatoria=True,
        )

    def _crear_regla(
        self,
        accion: str,
        valor_esperado: object = {"valor": 25},
        pregunta_destino: Pregunta | None = None,
        seccion_destino: SeccionFormulario | None = None,
        mensaje: str = "",
    ) -> ReglaPregunta:
        return ReglaPregunta.objects.create(
            pregunta_origen=self.p1,
            operador=OperadorRegla.EQUALS,
            valor_esperado=valor_esperado,
            accion=accion,
            pregunta_destino=pregunta_destino,
            seccion_destino=seccion_destino,
            mensaje=mensaje,
        )

    def _evaluar_con_valor_p1(self, valor: object, reglas: list[ReglaPregunta]) -> dict:
        mapa = {"P1": valor}
        return evaluar_reglas(reglas, mapa).to_dict()

    def test_regla_mostrar_pregunta(self) -> None:
        regla = self._crear_regla(AccionRegla.MOSTRAR, pregunta_destino=self.p2)
        resultado = self._evaluar_con_valor_p1(25, [regla])
        self.assertIn("P2", resultado["preguntas_visibles"])

    def test_regla_ocultar_pregunta(self) -> None:
        regla = self._crear_regla(AccionRegla.OCULTAR, pregunta_destino=self.p2)
        resultado = self._evaluar_con_valor_p1(25, [regla])
        self.assertIn("P2", resultado["preguntas_ocultas"])

    def test_regla_hacer_obligatoria(self) -> None:
        regla = self._crear_regla(
            AccionRegla.HACER_OBLIGATORIA,
            pregunta_destino=self.p2,
        )
        resultado = self._evaluar_con_valor_p1(25, [regla])
        self.assertIn("P2", resultado["preguntas_obligatorias"])

    def test_regla_hacer_opcional(self) -> None:
        regla = self._crear_regla(
            AccionRegla.HACER_OPCIONAL,
            pregunta_destino=self.p3,
        )
        resultado = self._evaluar_con_valor_p1(25, [regla])
        self.assertIn("P3", resultado["preguntas_opcionales"])

    def test_regla_saltar_a_pregunta(self) -> None:
        regla = self._crear_regla(
            AccionRegla.SALTAR_A_PREGUNTA,
            pregunta_destino=self.p3,
        )
        resultado = self._evaluar_con_valor_p1(25, [regla])
        self.assertEqual(resultado["saltar_a_pregunta"], "P3")

    def test_regla_saltar_a_seccion(self) -> None:
        regla = self._crear_regla(
            AccionRegla.SALTAR_A_SECCION,
            seccion_destino=self.seccion_destino,
        )
        resultado = self._evaluar_con_valor_p1(25, [regla])
        self.assertEqual(resultado["saltar_a_seccion"], "SEC2")

    def test_regla_finalizar_formulario(self) -> None:
        regla = self._crear_regla(AccionRegla.FINALIZAR_FORMULARIO)
        resultado = self._evaluar_con_valor_p1(25, [regla])
        self.assertTrue(resultado["finalizar_formulario"])

    def test_regla_no_aplica_formulario(self) -> None:
        regla = self._crear_regla(AccionRegla.NO_APLICA_FORMULARIO)
        resultado = self._evaluar_con_valor_p1(25, [regla])
        self.assertTrue(resultado["no_aplica_formulario"])

    def test_regla_habilitar_y_deshabilitar(self) -> None:
        regla_habilitar = self._crear_regla(
            AccionRegla.HABILITAR,
            pregunta_destino=self.p2,
        )
        regla_deshabilitar = self._crear_regla(
            AccionRegla.DESHABILITAR,
            pregunta_destino=self.p3,
        )
        resultado = self._evaluar_con_valor_p1(
            25,
            [regla_habilitar, regla_deshabilitar],
        )
        self.assertIn("P2", resultado["preguntas_habilitadas"])
        self.assertIn("P3", resultado["preguntas_deshabilitadas"])

    def test_normalizar_valor_respuesta_numero(self) -> None:
        respuesta = Respuesta(pregunta=self.p1)
        asignar_valor_a_respuesta(respuesta, TipoPregunta.NUMERO, 25)
        self.assertEqual(normalizar_valor_respuesta(respuesta), Decimal("25"))

    def test_sesion_inexistente_retorna_error(self) -> None:
        with self.assertRaises(SesionRespuestaNoExisteError):
            evaluar_reglas_sesion(str(uuid.uuid4()))

    def test_evaluar_reglas_sesion_con_respuesta(self) -> None:
        sesion = SesionAnonima.objects.create(
            uuid_sesion=uuid.uuid4(),
            formulario=self.formulario,
            version_formulario=self.version,
        )
        respuesta = Respuesta(sesion=sesion, pregunta=self.p1)
        asignar_valor_a_respuesta(respuesta, TipoPregunta.NUMERO, 25)
        respuesta.save()

        regla = self._crear_regla(AccionRegla.MOSTRAR, pregunta_destino=self.p2)
        regla.pregunta_origen = self.p1
        regla.save()

        resultado = evaluar_reglas_sesion(str(sesion.uuid_sesion))
        self.assertIn("P2", resultado["preguntas_visibles"])
