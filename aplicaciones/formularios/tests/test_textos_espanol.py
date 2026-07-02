"""
Pruebas de textos visibles en espanol de la API publica de formularios.
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.formularios.models import EstadoFormulario
from aplicaciones.formularios.constantes import (
    EtiquetaEstadoFormulario,
    MensajesFormularioApi,
)
from aplicaciones.formularios.tests.test_api import (
    crear_formulario_base,
    crear_version_publicada,
)

URL_DISPONIBLES = "/api/v1/formularios/disponibles/"


class TextosEspanolFormulariosApiTests(TestCase):
    """Verifica mensajes y etiquetas en espanol correcto."""

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_etiqueta_proximamente_con_tilde(self) -> None:
        ahora = timezone.now()
        formulario = crear_formulario_base(
            codigo="proximamente_tilde",
            estado=EstadoFormulario.PUBLICADO,
            fecha_inicio=ahora + timedelta(days=2),
        )
        crear_version_publicada(formulario)

        respuesta = self.cliente.get(URL_DISPONIBLES)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertEqual(len(datos), 1)
        self.assertEqual(
            datos[0]["etiqueta_estado"],
            EtiquetaEstadoFormulario.PROXIMAMENTE,
        )
        self.assertEqual(datos[0]["etiqueta_estado"], "Próximamente")

    def test_mensaje_formulario_no_disponible_con_tildes(self) -> None:
        uuid_inexistente = "00000000-0000-0000-0000-000000000099"
        respuesta = self.cliente.get(
            f"/api/v1/formularios/{uuid_inexistente}/estructura/",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            respuesta.json()["detalle"],
            MensajesFormularioApi.FORMULARIO_NO_DISPONIBLE,
        )
        self.assertIn("disponible", respuesta.json()["detalle"])

    def test_mensaje_aun_no_disponible_con_tilde(self) -> None:
        self.assertIn(
            "aún",
            MensajesFormularioApi.FORMULARIO_AUN_NO_DISPONIBLE,
        )
        self.assertIn(
            "versión",
            MensajesFormularioApi.VERSION_NO_DISPONIBLE,
        )
