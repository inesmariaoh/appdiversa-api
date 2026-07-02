"""
Pruebas de validacion de tooltips en preguntas y opciones.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from aplicaciones.formularios.excepciones_admin import ValidacionFormularioAdminError
from aplicaciones.formularios.models import (
    Formulario,
    FormularioVersion,
    MensajesValidacion,
    OpcionRespuesta,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.formularios.validadores_tooltip import (
    normalizar_tooltip,
    tooltip_visible_en_api,
    validar_tooltip_configurado,
    validar_y_normalizar_tooltip_admin,
)


class ValidadoresTooltipTests(TestCase):
    """Pruebas unitarias de validadores de tooltip."""

    def test_normalizar_tooltip_activo_sin_texto_falla(self) -> None:
        with self.assertRaises(ValidationError):
            normalizar_tooltip(True, "   ")

    def test_normalizar_tooltip_con_texto_activa_indicador(self) -> None:
        tiene, texto = normalizar_tooltip(False, "  Definicion DANE  ")
        self.assertTrue(tiene)
        self.assertEqual(texto, "Definicion DANE")

    def test_normalizar_tooltip_inactivo_limpia_texto(self) -> None:
        tiene, texto = normalizar_tooltip(False, "")
        self.assertFalse(tiene)
        self.assertEqual(texto, "")

    def test_validar_admin_propaga_mensaje_funcional(self) -> None:
        with self.assertRaises(ValidacionFormularioAdminError) as contexto:
            validar_y_normalizar_tooltip_admin(True, "")
        self.assertEqual(
            str(contexto.exception),
            MensajesValidacion.TOOLTIP_TEXTO_OBLIGATORIO,
        )

    def test_tooltip_visible_en_api_solo_cuando_activo(self) -> None:
        self.assertEqual(tooltip_visible_en_api(True, " Ayuda "), "Ayuda")
        self.assertEqual(tooltip_visible_en_api(False, "Ayuda"), "")


class TooltipModeloTests(TestCase):
    """Pruebas de clean() en modelos con tooltip."""

    def setUp(self) -> None:
        formulario = Formulario.objects.create(
            codigo="form_tooltip",
            nombre="Formulario tooltip",
            tipo_formulario=TipoFormulario.ENCUESTA,
        )
        version = FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
        )
        seccion = SeccionFormulario.objects.create(
            formulario_version=version,
            codigo="sec_tooltip",
            titulo="Seccion",
            orden=1,
        )
        self.pregunta = Pregunta.objects.create(
            seccion=seccion,
            codigo="preg_tooltip",
            texto="Pregunta",
            tipo_pregunta=TipoPregunta.RADIO,
            orden=1,
        )

    def test_pregunta_clean_rechaza_tooltip_activo_sin_texto(self) -> None:
        self.pregunta.tiene_tooltip = True
        self.pregunta.tooltip = ""
        with self.assertRaises(ValidationError):
            self.pregunta.clean()

    def test_opcion_clean_rechaza_tooltip_activo_sin_texto(self) -> None:
        opcion = OpcionRespuesta(
            pregunta=self.pregunta,
            codigo="op1",
            etiqueta="Opcion",
            valor="1",
            orden=1,
            tiene_tooltip=True,
            tooltip="",
        )
        with self.assertRaises(ValidationError):
            opcion.clean()

    def test_pregunta_clean_acepta_tooltip_activo_con_texto(self) -> None:
        self.pregunta.tiene_tooltip = True
        self.pregunta.tooltip = "Texto explicativo"
        validar_tooltip_configurado(self.pregunta.tiene_tooltip, self.pregunta.tooltip)
