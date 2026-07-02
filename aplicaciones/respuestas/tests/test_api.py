"""
Pruebas de API de respuestas.
"""

import uuid

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.sesiones_anonimas.models import SesionAnonima
from aplicaciones.sesiones_anonimas.seguridad import generar_token_cliente_seguro

URL_RESPUESTAS = "/api/v1/respuestas/"
URL_RESPUESTAS_SESION = "/api/v1/sesiones/{uuid}/respuestas/"


def crear_sesion_con_pregunta() -> tuple[SesionAnonima, str, str]:
    """Crea sesion con pregunta numerica y token para pruebas de API."""
    formulario = Formulario.objects.create(
        codigo="api_resp",
        nombre="Formulario API respuestas",
        tipo_formulario=TipoFormulario.ENCUESTA,
        estado=EstadoFormulario.PUBLICADO,
    )
    version = FormularioVersion.objects.create(
        formulario=formulario,
        numero_version=1,
        estado=EstadoFormulario.PUBLICADO,
        es_publicada=True,
    )
    uuid_sesion = uuid.uuid4()
    token_cliente = generar_token_cliente_seguro()
    sesion = SesionAnonima.objects.create(
        uuid_sesion=uuid_sesion,
        formulario=formulario,
        version_formulario=version,
        token_cliente=token_cliente,
    )
    seccion = SeccionFormulario.objects.create(
        formulario_version=version,
        codigo="sec_api",
        titulo="Seccion API",
        orden=1,
    )
    Pregunta.objects.create(
        seccion=seccion,
        codigo="P1",
        texto="Pregunta API",
        tipo_pregunta=TipoPregunta.NUMERO,
        orden=1,
    )
    return sesion, str(uuid_sesion), token_cliente


class RespuestasApiTests(TestCase):
    """Pruebas de endpoints de respuestas."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.sesion, self.uuid_sesion, self.token_cliente = crear_sesion_con_pregunta()

    def test_post_crea_respuesta(self) -> None:
        respuesta = self.cliente.post(
            URL_RESPUESTAS,
            {
                "uuid_sesion": self.uuid_sesion,
                "codigo_pregunta": "P1",
                "valor": 25,
                "token_cliente": self.token_cliente,
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        datos = respuesta.json()
        self.assertEqual(datos["codigo_pregunta"], "P1")
        self.assertEqual(datos["version_respuesta"], 1)

    def test_post_actualiza_respuesta(self) -> None:
        self.cliente.post(
            URL_RESPUESTAS,
            {
                "uuid_sesion": self.uuid_sesion,
                "codigo_pregunta": "P1",
                "valor": 25,
                "token_cliente": self.token_cliente,
            },
            format="json",
        )
        respuesta = self.cliente.post(
            URL_RESPUESTAS,
            {
                "uuid_sesion": self.uuid_sesion,
                "codigo_pregunta": "P1",
                "valor": 30,
                "token_cliente": self.token_cliente,
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()["version_respuesta"], 2)

    def test_get_lista_respuestas_sesion(self) -> None:
        self.cliente.post(
            URL_RESPUESTAS,
            {
                "uuid_sesion": self.uuid_sesion,
                "codigo_pregunta": "P1",
                "valor": 25,
                "origen_respuesta": "web",
                "fecha_respuesta_cliente": timezone.now().isoformat(),
                "token_cliente": self.token_cliente,
            },
            format="json",
        )

        respuesta = self.cliente.get(
            URL_RESPUESTAS_SESION.format(uuid=self.uuid_sesion),
            HTTP_X_SESION_ANONIMA=self.uuid_sesion,
            HTTP_X_TOKEN_SESION=self.token_cliente,
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertEqual(datos["uuid_sesion"], self.uuid_sesion)
        self.assertEqual(len(datos["respuestas"]), 1)
        self.assertEqual(datos["respuestas"][0]["codigo_pregunta"], "P1")
