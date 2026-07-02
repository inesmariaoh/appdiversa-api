"""
Pruebas del historial de respuestas del usuario autenticado.
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
    TipoFormulario,
)
from aplicaciones.sesiones_anonimas.servicios_vinculacion import (
    vincular_sesion_anonima_a_usuario,
)
from aplicaciones.usuarios.tests.helpers import (
    CONTRASENA_PRUEBA,
    autenticar_cliente,
    crear_usuario_prueba,
    inicializar_entorno_usuarios,
)

URL_MIS_RESPUESTAS = "/api/v1/auth/mis-respuestas/"
URL_SESIONES = "/api/v1/sesiones/"


class MisRespuestasApiTests(TestCase):
    """Pruebas del endpoint de historial de respuestas del usuario."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.usuario = crear_usuario_prueba("usuario_historial")
        self.formulario = Formulario.objects.create(
            codigo="form_historial",
            nombre="Formulario historial",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.PUBLICADO,
        )
        FormularioVersion.objects.create(
            formulario=self.formulario,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
        )

    def test_sin_autenticacion_retorna_401(self) -> None:
        respuesta = self.cliente.get(URL_MIS_RESPUESTAS)
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lista_vacia_sin_vinculaciones(self) -> None:
        autenticar_cliente(self.cliente, "usuario_historial", CONTRASENA_PRUEBA)
        respuesta = self.cliente.get(URL_MIS_RESPUESTAS)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["resultados"], [])

    def test_lista_sesiones_vinculadas(self) -> None:
        uuid_sesion = uuid.uuid4()
        respuesta_creacion = self.cliente.post(
            URL_SESIONES,
            {
                "uuid_sesion": str(uuid_sesion),
                "uuid_formulario": str(self.formulario.uuid),
            },
            format="json",
        )
        token = respuesta_creacion.data["token_cliente"]
        vincular_sesion_anonima_a_usuario(uuid_sesion, token, self.usuario)

        autenticar_cliente(self.cliente, "usuario_historial", CONTRASENA_PRUEBA)
        respuesta = self.cliente.get(URL_MIS_RESPUESTAS)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data["resultados"]), 1)
        item = respuesta.data["resultados"][0]
        self.assertEqual(item["uuid_sesion"], str(uuid_sesion))
        self.assertEqual(item["codigo_formulario"], "form_historial")
        self.assertEqual(item["nombre_formulario"], "Formulario historial")

    def test_vinculacion_via_api_aparece_en_historial(self) -> None:
        uuid_sesion = uuid.uuid4()
        respuesta_creacion = self.cliente.post(
            URL_SESIONES,
            {
                "uuid_sesion": str(uuid_sesion),
                "uuid_formulario": str(self.formulario.uuid),
            },
            format="json",
        )
        token = respuesta_creacion.data["token_cliente"]
        autenticar_cliente(self.cliente, "usuario_historial", CONTRASENA_PRUEBA)
        url_vincular = f"/api/v1/sesiones/{uuid_sesion}/vincular-usuario/"
        self.cliente.post(
            url_vincular,
            format="json",
            **headers_sesion_anonima(str(uuid_sesion), token),
        )
        respuesta = self.cliente.get(URL_MIS_RESPUESTAS)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data["resultados"]), 1)
