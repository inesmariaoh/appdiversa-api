"""
Pruebas de API de analitica.
"""

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.analitica.tests.helpers import crear_datos_analitica
from aplicaciones.comun.tests.helpers_seguridad import (
    TOKEN_API_INTERNA_PRUEBA,
    headers_api_interna,
)
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima

URL_RESPUESTAS_ANALITICA = "/api/v1/analitica/respuestas/"


@override_settings(API_INTERNA_TOKEN=TOKEN_API_INTERNA_PRUEBA)
class RespuestasAnaliticasApiTests(TestCase):
    """Pruebas del endpoint de respuestas analiticas."""

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_endpoint_retorna_200(self) -> None:
        crear_datos_analitica()
        respuesta = self.cliente.get(URL_RESPUESTAS_ANALITICA, **headers_api_interna())
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_endpoint_retorna_lista_vacia_sin_datos(self) -> None:
        respuesta = self.cliente.get(URL_RESPUESTAS_ANALITICA, **headers_api_interna())
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json(), [])

    def test_endpoint_retorna_respuestas_finalizadas(self) -> None:
        crear_datos_analitica(estado_sesion=EstadoSesionAnonima.FINALIZADA)
        respuesta = self.cliente.get(
            URL_RESPUESTAS_ANALITICA,
            {"estado_sesion": EstadoSesionAnonima.FINALIZADA},
            **headers_api_interna(),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.json()), 1)
        self.assertEqual(
            respuesta.json()[0]["estado_sesion"],
            EstadoSesionAnonima.FINALIZADA,
        )

    def test_endpoint_filtra_por_formulario_codigo(self) -> None:
        crear_datos_analitica(codigo_formulario="DISC-001")
        respuesta = self.cliente.get(
            URL_RESPUESTAS_ANALITICA,
            {"formulario_codigo": "DISC-001"},
            **headers_api_interna(),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()[0]["formulario_codigo"], "DISC-001")

    def test_endpoint_filtra_por_estado_sesion(self) -> None:
        crear_datos_analitica(estado_sesion=EstadoSesionAnonima.EN_PROCESO)
        respuesta = self.cliente.get(
            URL_RESPUESTAS_ANALITICA,
            {"estado_sesion": EstadoSesionAnonima.EN_PROCESO},
            **headers_api_interna(),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.json()), 1)
