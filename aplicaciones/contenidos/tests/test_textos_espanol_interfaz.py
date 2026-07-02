"""
Pruebas de textos en espanol del endpoint de configuracion de interfaz.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.contenidos.constantes import ValoresPorDefectoFlujoFormulario
from aplicaciones.contenidos.models import ConfiguracionFlujoFormulario

URL_CONFIGURACION = "/api/v1/interfaz/configuracion/"


class TextosEspanolInterfazApiTests(TestCase):
    """Verifica textos por defecto del flujo con ortografia correcta."""

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_flujo_formulario_por_defecto_tiene_tildes(self) -> None:
        respuesta = self.cliente.get(URL_CONFIGURACION)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        flujo = respuesta.json()["flujo_formulario"]
        self.assertIn("sesión", flujo["modal_sesion"]["titulo"].lower())
        self.assertIn("éxito", flujo["modal_guardado"]["titulo"].lower())
        self.assertIn("Términos", flujo["terminos"]["titulo"])

    def test_flujo_formulario_activo_expone_textos_corregidos(self) -> None:
        ConfiguracionFlujoFormulario.objects.create(
            modal_sesion_titulo="Inicia sesion o registrate",
            modal_guardado_titulo="Encuesta guardada con exito",
            terminos_enlace="Terminos y condiciones",
            esta_activa=True,
        )

        respuesta = self.cliente.get(URL_CONFIGURACION)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        flujo = respuesta.json()["flujo_formulario"]
        self.assertEqual(
            flujo["modal_sesion"]["titulo"],
            "Inicia sesion o registrate",
        )

    def test_constantes_por_defecto_tienen_ortografia_correcta(self) -> None:
        self.assertEqual(
            ValoresPorDefectoFlujoFormulario.MODAL_SESION_TITULO,
            "Inicia sesión o regístrate",
        )
        self.assertEqual(
            ValoresPorDefectoFlujoFormulario.MODAL_GUARDADO_TITULO,
            "Encuesta guardada con éxito",
        )
        self.assertIn(
            "Términos",
            ValoresPorDefectoFlujoFormulario.TERMINOS_TITULO,
        )
