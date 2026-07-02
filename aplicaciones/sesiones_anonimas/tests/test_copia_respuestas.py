"""
Pruebas de envio de copia de respuestas por correo.
"""

import uuid

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.comun.tests.helpers_seguridad import headers_sesion_anonima
from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.respuestas.models import Respuesta
from aplicaciones.sesiones_anonimas.models import SesionAnonima
from aplicaciones.usuarios.constantes import MensajesCopiaRespuestas
from aplicaciones.usuarios.tests.helpers import inicializar_entorno_usuarios

URL_SESIONES = "/api/v1/sesiones/"


class CopiaRespuestasApiTests(TestCase):
    """Pruebas del endpoint de envio de copia de respuestas."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.formulario = Formulario.objects.create(
            codigo="copia_form",
            nombre="Formulario copia",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.PUBLICADO,
        )
        self.version = FormularioVersion.objects.create(
            formulario=self.formulario,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
        )
        self.seccion = SeccionFormulario.objects.create(
            formulario_version=self.version,
            codigo="s1",
            titulo="Seccion",
            orden=1,
        )
        self.pregunta = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="p1",
            texto="Pregunta",
            tipo_pregunta=TipoPregunta.TEXTO_CORTO,
            orden=1,
        )
        self.uuid_sesion = uuid.uuid4()
        respuesta_creacion = self.cliente.post(
            URL_SESIONES,
            {
                "uuid_sesion": str(self.uuid_sesion),
                "uuid_formulario": str(self.formulario.uuid),
            },
            format="json",
        )
        self.token = respuesta_creacion.data["token_cliente"]
        self.sesion = SesionAnonima.objects.get(uuid_sesion=self.uuid_sesion)
        Respuesta.objects.create(
            sesion=self.sesion,
            pregunta=self.pregunta,
            valor_texto="respuesta prueba",
        )

    def test_sin_token_retorna_403(self) -> None:
        url = f"/api/v1/sesiones/{self.uuid_sesion}/enviar-copia/"
        respuesta = self.cliente.post(
            url,
            {"correo": "copia@example.com"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_con_token_valido_envia_correo(self) -> None:
        url = f"/api/v1/sesiones/{self.uuid_sesion}/enviar-copia/"
        respuesta = self.cliente.post(
            url,
            {"correo": "copia@example.com"},
            format="json",
            **headers_sesion_anonima(str(self.uuid_sesion), self.token),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["detalle"], MensajesCopiaRespuestas.ENVIADA)

    def test_sesion_finalizada_permite_enviar_copia(self) -> None:
        self.sesion.estado = "finalizada"
        self.sesion.save(update_fields=["estado"])
        url = f"/api/v1/sesiones/{self.uuid_sesion}/enviar-copia/"
        respuesta = self.cliente.post(
            url,
            {"correo": "copia@example.com"},
            format="json",
            **headers_sesion_anonima(str(self.uuid_sesion), self.token),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_correo_invalido_retorna_400(self) -> None:
        url = f"/api/v1/sesiones/{self.uuid_sesion}/enviar-copia/"
        respuesta = self.cliente.post(
            url,
            {"correo": "correo-invalido"},
            format="json",
            **headers_sesion_anonima(str(self.uuid_sesion), self.token),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sesion_inexistente_retorna_404(self) -> None:
        uuid_inexistente = uuid.uuid4()
        url = f"/api/v1/sesiones/{uuid_inexistente}/enviar-copia/"
        respuesta = self.cliente.post(
            url,
            {"correo": "copia@example.com"},
            format="json",
            **headers_sesion_anonima(str(uuid_inexistente), "token-invalido"),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
