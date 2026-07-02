"""
Pruebas de deteccion de opciones excluyentes en seleccion multiple.
"""

from django.test import SimpleTestCase

from aplicaciones.formularios.models import TipoPregunta
from aplicaciones.formularios.utilidades_opcion_excluyente import (
    etiqueta_es_opcion_excluyente,
    resolver_es_excluyente,
)


class EtiquetaOpcionExcluyenteTests(SimpleTestCase):
    """Verifica la deteccion de etiquetas de negacion o no aplica."""

    def test_detecta_no_he_sentido(self) -> None:
        """Historia de usuario asociada: opciones excluyentes en seleccion multiple."""
        self.assertTrue(etiqueta_es_opcion_excluyente("No he sentido discriminacion"))

    def test_detecta_nunca(self) -> None:
        """Historia de usuario asociada: opciones excluyentes en seleccion multiple."""
        self.assertTrue(etiqueta_es_opcion_excluyente("Nunca me ha pasado"))

    def test_no_detecta_opcion_afirmativa(self) -> None:
        """Historia de usuario asociada: opciones excluyentes en seleccion multiple."""
        self.assertFalse(etiqueta_es_opcion_excluyente("Identidad cultural"))


class ResolverEsExcluyenteTests(SimpleTestCase):
    """Verifica la resolucion final de es_excluyente para la API."""

    def test_respeta_flag_configurado(self) -> None:
        """Historia de usuario asociada: opciones excluyentes en seleccion multiple."""
        self.assertTrue(
            resolver_es_excluyente(True, TipoPregunta.CHECKBOX, "Cualquier etiqueta"),
        )

    def test_inferencia_por_etiqueta_en_checkbox(self) -> None:
        """Historia de usuario asociada: opciones excluyentes en seleccion multiple."""
        self.assertTrue(
            resolver_es_excluyente(
                False,
                TipoPregunta.CHECKBOX,
                "No he sentido discriminacion",
            ),
        )

    def test_no_aplica_en_radio(self) -> None:
        """Historia de usuario asociada: opciones excluyentes en seleccion multiple."""
        self.assertFalse(
            resolver_es_excluyente(
                False,
                TipoPregunta.RADIO,
                "No he sentido discriminacion",
            ),
        )
