"""
Pruebas de API de sesiones anonimas.
"""

import uuid
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.formularios.constantes import MensajesFormularioApi
from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    TipoFormulario,
)
from aplicaciones.sesiones_anonimas.constantes import MensajesSesionApi

URL_SESIONES = "/api/v1/sesiones/"


def crear_formulario_publicado(
    codigo: str = "api_sesion",
    fecha_inicio=None,
    fecha_fin=None,
) -> Formulario:
    """Crea un formulario publicado para pruebas de API."""
    return Formulario.objects.create(
        codigo=codigo,
        nombre=f"Formulario {codigo}",
        tipo_formulario=TipoFormulario.ENCUESTA,
        estado=EstadoFormulario.PUBLICADO,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


class SesionesAnonimasApiTests(TestCase):
    """Pruebas de endpoints de sesiones anonimas."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.formulario = crear_formulario_publicado()
        FormularioVersion.objects.create(
            formulario=self.formulario,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
        )
        self.uuid_sesion = uuid.uuid4()

    def test_post_crea_sesion(self) -> None:
        respuesta = self.cliente.post(
            URL_SESIONES,
            {
                "uuid_sesion": str(self.uuid_sesion),
                "uuid_formulario": str(self.formulario.uuid),
                "idioma": "es-CO",
                "zona_horaria": "America/Bogota",
                "es_offline": False,
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertIn("token_cliente", respuesta.json())
        self.assertTrue(respuesta.json()["token_cliente"])

    def test_post_reutiliza_sesion(self) -> None:
        self.cliente.post(
            URL_SESIONES,
            {
                "uuid_sesion": str(self.uuid_sesion),
                "uuid_formulario": str(self.formulario.uuid),
            },
            format="json",
        )
        respuesta = self.cliente.post(
            URL_SESIONES,
            {
                "uuid_sesion": str(self.uuid_sesion),
                "uuid_formulario": str(self.formulario.uuid),
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_post_rechaza_formulario_futuro(self) -> None:
        ahora = timezone.now()
        formulario = crear_formulario_publicado(
            codigo="sesion_futuro",
            fecha_inicio=ahora + timedelta(days=1),
        )
        FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
        )

        respuesta = self.cliente.post(
            URL_SESIONES,
            {
                "uuid_sesion": str(uuid.uuid4()),
                "uuid_formulario": str(formulario.uuid),
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            respuesta.json()["detalle"],
            MensajesFormularioApi.FORMULARIO_AUN_NO_DISPONIBLE,
        )

    def test_post_rechaza_formulario_vencido(self) -> None:
        ahora = timezone.now()
        formulario = crear_formulario_publicado(
            codigo="sesion_vencido",
            fecha_fin=ahora - timedelta(days=1),
        )
        FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
        )

        respuesta = self.cliente.post(
            URL_SESIONES,
            {
                "uuid_sesion": str(uuid.uuid4()),
                "uuid_formulario": str(formulario.uuid),
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            respuesta.json()["detalle"],
            MensajesSesionApi.FORMULARIO_NO_DISPONIBLE,
        )
