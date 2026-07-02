"""
Pruebas de deteccion de opciones que activan campo otro.
"""

from django.test import SimpleTestCase

from aplicaciones.formularios.utilidades_opcion_otro import (
    etiqueta_activa_campo_otro,
    resolver_activa_otro,
)


class EtiquetaActivaCampoOtroTests(SimpleTestCase):
    """Verifica la deteccion de etiquetas que requieren texto adicional."""

    def test_detecta_otros_motivos_cuales(self) -> None:
        """Historia de usuario asociada: deteccion de campo otro en opciones."""
        self.assertTrue(etiqueta_activa_campo_otro("Otros motivos, ¿cuáles?"))

    def test_detecta_otro_cual_sin_tilde(self) -> None:
        """Historia de usuario asociada: deteccion de campo otro en opciones."""
        self.assertTrue(etiqueta_activa_campo_otro("Otro, ¿cual?"))

    def test_no_detecta_etiqueta_generica_con_otros_al_final(self) -> None:
        """Historia de usuario asociada: deteccion de campo otro en opciones."""
        etiqueta = "Apariencia fisica (tatuajes, piercings, vestuario, otros)"
        self.assertFalse(etiqueta_activa_campo_otro(etiqueta))

    def test_no_detecta_etiqueta_sin_palabras_clave(self) -> None:
        """Historia de usuario asociada: deteccion de campo otro en opciones."""
        self.assertFalse(etiqueta_activa_campo_otro("Discriminacion racial"))


class ResolverActivaOtroTests(SimpleTestCase):
    """Verifica la resolucion final de activa_otro para la API."""

    def test_respeta_flag_configurado(self) -> None:
        """Historia de usuario asociada: deteccion de campo otro en opciones."""
        self.assertTrue(resolver_activa_otro(True, True, "Cualquier etiqueta"))

    def test_inferencia_por_etiqueta_cuando_permite_otro(self) -> None:
        """Historia de usuario asociada: deteccion de campo otro en opciones."""
        self.assertTrue(resolver_activa_otro(False, True, "Otros motivos, ¿cuáles?"))

    def test_no_activa_si_pregunta_no_permite_otro(self) -> None:
        """Historia de usuario asociada: deteccion de campo otro en opciones."""
        self.assertFalse(resolver_activa_otro(False, False, "Otro, ¿cual?"))
