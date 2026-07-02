"""
Pruebas de formateo legible de valores en resumen de respuestas.
"""

from django.test import TestCase

from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    OpcionRespuesta,
    Pregunta,
    PreguntaMatrizColumna,
    PreguntaMatrizFila,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.respuestas.formateo_valor_resumen import formatear_valor_resumen_legible


class FormateoValorResumenTests(TestCase):
    """Pruebas del formateo legible de respuestas para resumen."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.formulario = Formulario.objects.create(
            codigo="form_formato",
            nombre="Formulario formato",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.PUBLICADO,
        )
        cls.version = FormularioVersion.objects.create(
            formulario=cls.formulario,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
        )
        cls.seccion = SeccionFormulario.objects.create(
            formulario_version=cls.version,
            codigo="s1",
            titulo="Seccion",
            orden=1,
        )

    def _crear_pregunta(self, codigo: str, tipo: str) -> Pregunta:
        return Pregunta.objects.create(
            seccion=self.seccion,
            codigo=codigo,
            texto=f"Pregunta {codigo}",
            tipo_pregunta=tipo,
            orden=1,
        )

    def test_checkbox_formatea_etiquetas(self) -> None:
        pregunta = self._crear_pregunta("p_checkbox", TipoPregunta.CHECKBOX)
        OpcionRespuesta.objects.create(
            pregunta=pregunta,
            codigo="opc_a",
            etiqueta="Opcion A",
            valor="a",
            orden=1,
        )
        OpcionRespuesta.objects.create(
            pregunta=pregunta,
            codigo="opc_b",
            etiqueta="Opcion B",
            valor="b",
            orden=2,
        )
        salida = formatear_valor_resumen_legible(
            pregunta,
            TipoPregunta.CHECKBOX,
            ["opc_a", "opc_b"],
        )
        self.assertEqual(salida, "Opcion A, Opcion B")

    def test_matriz_formatea_filas_y_columnas(self) -> None:
        pregunta = self._crear_pregunta("p_matriz", TipoPregunta.MATRIZ)
        PreguntaMatrizFila.objects.create(
            pregunta=pregunta,
            codigo="f1",
            etiqueta="Entorno laboral",
            orden=1,
        )
        PreguntaMatrizColumna.objects.create(
            pregunta=pregunta,
            codigo="c1",
            etiqueta="Siempre",
            valor="siempre",
            orden=1,
        )
        salida = formatear_valor_resumen_legible(
            pregunta,
            TipoPregunta.MATRIZ,
            {"f1": "c1"},
        )
        self.assertEqual(salida, "Entorno laboral: Siempre")

    def test_radio_formatea_etiqueta(self) -> None:
        pregunta = self._crear_pregunta("p_radio", TipoPregunta.RADIO)
        OpcionRespuesta.objects.create(
            pregunta=pregunta,
            codigo="si",
            etiqueta="Sí",
            valor="si",
            orden=1,
        )
        salida = formatear_valor_resumen_legible(
            pregunta,
            TipoPregunta.RADIO,
            "si",
        )
        self.assertEqual(salida, "Sí")

    def test_radio_otro_incluye_observacion(self) -> None:
        pregunta = self._crear_pregunta("p_otro", TipoPregunta.RADIO)
        OpcionRespuesta.objects.create(
            pregunta=pregunta,
            codigo="otro",
            etiqueta="Otro",
            valor="otro",
            orden=1,
            activa_otro=True,
        )
        salida = formatear_valor_resumen_legible(
            pregunta,
            TipoPregunta.RADIO,
            "otro",
            "Texto personalizado",
        )
        self.assertEqual(salida, "Otro: Texto personalizado")

    def test_valor_nulo_retorna_cadena_vacia(self) -> None:
        pregunta = self._crear_pregunta("p_texto", TipoPregunta.TEXTO_CORTO)
        salida = formatear_valor_resumen_legible(
            pregunta,
            TipoPregunta.TEXTO_CORTO,
            None,
        )
        self.assertEqual(salida, "")
