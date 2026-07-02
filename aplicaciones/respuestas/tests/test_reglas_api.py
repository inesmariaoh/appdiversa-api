"""
Pruebas de API del motor de reglas.
"""

import uuid

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

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
from aplicaciones.sesiones_anonimas.models import SesionAnonima
from aplicaciones.sesiones_anonimas.seguridad import generar_token_cliente_seguro

URL_RESPUESTAS = "/api/v1/respuestas/"
URL_EVALUAR_REGLAS = "/api/v1/sesiones/{uuid}/evaluar-reglas/"
URL_EVALUAR_REGLAS_PREGUNTA = (
    "/api/v1/sesiones/{uuid}/preguntas/{codigo}/evaluar-reglas/"
)


def crear_contexto_reglas() -> tuple[SesionAnonima, str, str, Pregunta, Pregunta]:
    """Crea sesion con regla mostrar P2 cuando P1 equals 25."""
    formulario = Formulario.objects.create(
        codigo="form_reglas_api",
        nombre="Formulario reglas API",
        tipo_formulario=TipoFormulario.ENCUESTA,
        estado=EstadoFormulario.PUBLICADO,
    )
    version = FormularioVersion.objects.create(
        formulario=formulario,
        numero_version=1,
        estado=EstadoFormulario.PUBLICADO,
        es_publicada=True,
    )
    seccion = SeccionFormulario.objects.create(
        formulario_version=version,
        codigo="SEC_API",
        titulo="Seccion API",
        orden=1,
    )
    p1 = Pregunta.objects.create(
        seccion=seccion,
        codigo="P1",
        texto="Edad",
        tipo_pregunta=TipoPregunta.NUMERO,
        orden=1,
    )
    p2 = Pregunta.objects.create(
        seccion=seccion,
        codigo="P2",
        texto="Detalle",
        tipo_pregunta=TipoPregunta.TEXTO_CORTO,
        orden=2,
    )
    ReglaPregunta.objects.create(
        pregunta_origen=p1,
        operador=OperadorRegla.EQUALS,
        valor_esperado={"valor": 25},
        pregunta_destino=p2,
        accion=AccionRegla.MOSTRAR,
    )
    uuid_sesion = uuid.uuid4()
    token_cliente = generar_token_cliente_seguro()
    sesion = SesionAnonima.objects.create(
        uuid_sesion=uuid_sesion,
        formulario=formulario,
        version_formulario=version,
        token_cliente=token_cliente,
    )
    return sesion, str(uuid_sesion), token_cliente, p1, p2


class ReglasApiTests(TestCase):
    """Pruebas de endpoints de evaluacion de reglas."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.sesion, self.uuid_sesion, self.token_cliente, self.p1, self.p2 = (
            crear_contexto_reglas()
        )
        self.headers_sesion = {
            "HTTP_X_SESION_ANONIMA": self.uuid_sesion,
            "HTTP_X_TOKEN_SESION": self.token_cliente,
        }

    def test_sesion_inexistente_retorna_error(self) -> None:
        uuid_inexistente = uuid.uuid4()
        respuesta = self.cliente.post(
            URL_EVALUAR_REGLAS.format(uuid=uuid_inexistente),
            HTTP_X_SESION_ANONIMA=str(uuid_inexistente),
            HTTP_X_TOKEN_SESION="token-invalido",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_endpoint_evaluar_reglas_retorna_200(self) -> None:
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
            URL_EVALUAR_REGLAS.format(uuid=self.uuid_sesion),
            **self.headers_sesion,
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("P2", respuesta.json()["preguntas_visibles"])

    def test_endpoint_evaluar_reglas_por_pregunta_retorna_200(self) -> None:
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
            URL_EVALUAR_REGLAS_PREGUNTA.format(
                uuid=self.uuid_sesion,
                codigo="P1",
            ),
            **self.headers_sesion,
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("P2", respuesta.json()["preguntas_visibles"])

    def test_pregunta_inexistente_retorna_error(self) -> None:
        respuesta = self.cliente.post(
            URL_EVALUAR_REGLAS_PREGUNTA.format(
                uuid=self.uuid_sesion,
                codigo="PX",
            ),
            **self.headers_sesion,
        )
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            respuesta.json()["detalle"],
            "La pregunta solicitada no existe para este formulario.",
        )

    def test_post_respuesta_retorna_bloque_reglas(self) -> None:
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
        self.assertIn("reglas", datos)
        self.assertIn("P2", datos["reglas"]["preguntas_visibles"])
