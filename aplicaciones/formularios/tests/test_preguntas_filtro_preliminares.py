"""
Pruebas de preguntas filtro/preliminares configurables.
"""

import uuid
from datetime import date

from django.test import TestCase

from aplicaciones.formularios.filtros.evaluador import (
    calcular_edad,
    evaluar_pregunta_filtro,
)
from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
    TipoValidacionFiltro,
)
from aplicaciones.respuestas.selectores import evaluar_filtros_sesion
from aplicaciones.respuestas.servicios import (
    finalizar_formulario_sesion,
    guardar_o_actualizar_respuesta,
    validar_formulario_sesion,
)
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima


class FiltrosPreliminaresTests(TestCase):
    """Pruebas del motor de filtros preliminares parametrizables."""

    def setUp(self) -> None:
        self.formulario = Formulario.objects.create(
            codigo="form_filtro",
            nombre="Formulario con filtros",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.PUBLICADO,
        )
        self.version = FormularioVersion.objects.create(
            formulario=self.formulario,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
        )
        self.seccion_filtro = SeccionFormulario.objects.create(
            formulario_version=self.version,
            codigo="PRE",
            titulo="Preliminar",
            orden=1,
        )
        self.seccion_principal = SeccionFormulario.objects.create(
            formulario_version=self.version,
            codigo="MAIN",
            titulo="Principal",
            orden=2,
        )
        self.p_fecha = Pregunta.objects.create(
            seccion=self.seccion_filtro,
            codigo="P-FEC",
            texto="Fecha de nacimiento",
            tipo_pregunta=TipoPregunta.FECHA,
            orden=1,
            es_obligatoria=True,
            es_pregunta_filtro=True,
            tipo_validacion_filtro=TipoValidacionFiltro.RANGO_EDAD,
            valor_minimo=18,
            valor_maximo=109,
            mensaje_error="Debe tener entre 18 y 109 años.",
            bloquea_continuacion_si_no_cumple=True,
        )
        self.p_radio = Pregunta.objects.create(
            seccion=self.seccion_filtro,
            codigo="P-RES",
            texto="Residencia en Colombia",
            tipo_pregunta=TipoPregunta.RADIO,
            orden=2,
            es_obligatoria=True,
            es_pregunta_filtro=True,
            tipo_validacion_filtro=TipoValidacionFiltro.OPCION_EXACTA,
            valor_filtro_esperado={"valor": "si"},
            mensaje_no_cumple="No cumple condiciones de residencia.",
            bloquea_continuacion_si_no_cumple=True,
        )
        self.p_principal = Pregunta.objects.create(
            seccion=self.seccion_principal,
            codigo="P-MAIN",
            texto="Pregunta principal",
            tipo_pregunta=TipoPregunta.TEXTO_CORTO,
            orden=1,
            es_obligatoria=True,
        )
        self.sesion = SesionAnonima.objects.create(
            uuid_sesion=uuid.uuid4(),
            formulario=self.formulario,
            version_formulario=self.version,
            estado=EstadoSesionAnonima.EN_PROCESO,
        )

    def test_calcular_edad_con_fecha_valida(self) -> None:
        edad = calcular_edad(date(2000, 1, 1), date(2026, 7, 1))
        self.assertEqual(edad, 26)

    def test_edad_menor_de_18_no_cumple(self) -> None:
        cumple, mensaje = evaluar_pregunta_filtro(
            self.p_fecha,
            {"anio": "2012", "mes": "9", "dia": "23"},
            fecha_referencia=date(2026, 7, 1),
        )
        self.assertFalse(cumple)
        self.assertIsNotNone(mensaje)

    def test_edad_mayor_de_109_no_cumple(self) -> None:
        cumple, _ = evaluar_pregunta_filtro(
            self.p_fecha,
            {"anio": "1900", "mes": "1", "dia": "1"},
            fecha_referencia=date(2026, 7, 1),
        )
        self.assertFalse(cumple)

    def test_edad_dentro_del_rango_cumple(self) -> None:
        cumple, mensaje = evaluar_pregunta_filtro(
            self.p_fecha,
            {"anio": "1990", "mes": "5", "dia": "10"},
            fecha_referencia=date(2026, 7, 1),
        )
        self.assertTrue(cumple)
        self.assertIsNone(mensaje)

    def test_opcion_si_cumple_y_no_no_cumple(self) -> None:
        cumple_si, _ = evaluar_pregunta_filtro(self.p_radio, "si")
        cumple_no, mensaje_no = evaluar_pregunta_filtro(self.p_radio, "no")
        self.assertTrue(cumple_si)
        self.assertFalse(cumple_no)
        self.assertEqual(mensaje_no, "No cumple condiciones de residencia.")

    def test_no_finaliza_si_filtros_no_cumplen(self) -> None:
        guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P-FEC",
            valor={"anio": "2015", "mes": "1", "dia": "1"},
        )
        guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P-RES",
            valor="no",
        )

        resultado_filtros = evaluar_filtros_sesion(self.sesion)
        self.assertFalse(resultado_filtros["cumple_filtros"])

        validacion = validar_formulario_sesion(self.sesion.uuid_sesion)
        self.assertFalse(validacion["es_valido"])
        self.assertFalse(validacion["cumple_filtros"])

        finalizacion = finalizar_formulario_sesion(self.sesion.uuid_sesion)
        self.assertFalse(finalizacion["es_valido"])

    def test_finaliza_cuando_filtros_y_principal_cumplen(self) -> None:
        guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P-FEC",
            valor={"anio": "1995", "mes": "3", "dia": "15"},
        )
        guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P-RES",
            valor="si",
        )
        guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P-MAIN",
            valor="respuesta",
        )

        self.assertTrue(evaluar_filtros_sesion(self.sesion)["cumple_filtros"])
        validacion = validar_formulario_sesion(self.sesion.uuid_sesion)
        self.assertTrue(validacion["es_valido"])
