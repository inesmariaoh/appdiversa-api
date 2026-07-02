"""
Pruebas de vinculacion de sesion anonima con usuario autenticado.
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
from aplicaciones.sesiones_anonimas.constantes import MensajesSesionApi
from aplicaciones.sesiones_anonimas.models import SesionAnonima
from aplicaciones.usuarios.tests.helpers import (
    CONTRASENA_PRUEBA,
    URL_LOGIN,
    autenticar_cliente,
    crear_usuario_prueba,
    inicializar_entorno_usuarios,
)

URL_SESIONES = "/api/v1/sesiones/"


class VincularUsuarioSesionApiTests(TestCase):
    """Pruebas del endpoint de vinculacion sesion-usuario."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.usuario = crear_usuario_prueba("encuestado_vincular")
        self.formulario = Formulario.objects.create(
            codigo="form_vincular",
            nombre="Formulario vincular",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.PUBLICADO,
        )
        FormularioVersion.objects.create(
            formulario=self.formulario,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
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
        self.url_vincular = (
            f"/api/v1/sesiones/{self.uuid_sesion}/vincular-usuario/"
        )

    def test_sin_autenticacion_retorna_401(self) -> None:
        respuesta = self.cliente.post(
            self.url_vincular,
            format="json",
            **headers_sesion_anonima(str(self.uuid_sesion), self.token),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sin_token_sesion_retorna_403(self) -> None:
        autenticar_cliente(self.cliente, "encuestado_vincular", CONTRASENA_PRUEBA)
        respuesta = self.cliente.post(self.url_vincular, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_vinculacion_exitosa(self) -> None:
        autenticar_cliente(self.cliente, "encuestado_vincular", CONTRASENA_PRUEBA)
        respuesta = self.cliente.post(
            self.url_vincular,
            format="json",
            **headers_sesion_anonima(str(self.uuid_sesion), self.token),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["detalle"], MensajesSesionApi.SESION_VINCULADA)
        sesion = SesionAnonima.objects.get(uuid_sesion=self.uuid_sesion)
        self.assertEqual(sesion.usuario_id, self.usuario.pk)

    def test_vinculacion_idempotente_mismo_usuario(self) -> None:
        autenticar_cliente(self.cliente, "encuestado_vincular", CONTRASENA_PRUEBA)
        headers = headers_sesion_anonima(str(self.uuid_sesion), self.token)
        primera = self.cliente.post(self.url_vincular, format="json", **headers)
        segunda = self.cliente.post(self.url_vincular, format="json", **headers)
        self.assertEqual(primera.status_code, status.HTTP_200_OK)
        self.assertEqual(segunda.status_code, status.HTTP_200_OK)

    def test_sesion_ya_vinculada_otro_usuario_retorna_400(self) -> None:
        otro_usuario = crear_usuario_prueba("otro_encuestado")
        autenticar_cliente(self.cliente, "encuestado_vincular", CONTRASENA_PRUEBA)
        headers = headers_sesion_anonima(str(self.uuid_sesion), self.token)
        self.cliente.post(self.url_vincular, format="json", **headers)
        self.cliente.post(URL_LOGIN, format="json")
        autenticar_cliente(self.cliente, "otro_encuestado", CONTRASENA_PRUEBA)
        respuesta = self.cliente.post(self.url_vincular, format="json", **headers)
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(respuesta.data["detalle"], MensajesSesionApi.SESION_YA_VINCULADA)
        sesion = SesionAnonima.objects.get(uuid_sesion=self.uuid_sesion)
        self.assertEqual(sesion.usuario_id, self.usuario.pk)
        self.assertNotEqual(sesion.usuario_id, otro_usuario.pk)
