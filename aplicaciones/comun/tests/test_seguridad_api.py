"""
Pruebas de seguridad minima pre-frontend.
"""

import uuid

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.archivos.constantes import OrigenArchivo, TipoArchivo
from aplicaciones.archivos.servicios import guardar_archivo
from aplicaciones.comun.constantes_seguridad import MensajesAccesoApi
from aplicaciones.comun.tests.helpers_seguridad import (
    TOKEN_API_INTERNA_PRUEBA,
    headers_api_interna,
    headers_sesion_anonima,
)
from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.notificaciones.constantes import TipoNotificacion
from aplicaciones.notificaciones.models import PlantillaNotificacion
from aplicaciones.sesiones_anonimas.constantes import MensajesSesionApi
from aplicaciones.sesiones_anonimas.models import SesionAnonima
from aplicaciones.sesiones_anonimas.seguridad import generar_token_cliente_seguro

CONTENIDO_PNG_MINIMO = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

URL_SESIONES = "/api/v1/sesiones/"
URL_RESPUESTAS = "/api/v1/respuestas/"
URL_ARCHIVOS = "/api/v1/archivos/"
URL_ANALITICA = "/api/v1/analitica/respuestas/"
URL_EXPORTACIONES_RESPUESTAS = "/api/v1/exportaciones/respuestas/"
URL_NOTIFICACIONES_PROBAR = "/api/v1/notificaciones/probar/"


def _crear_formulario_publicado() -> Formulario:
    sufijo = uuid.uuid4().hex[:8]
    return Formulario.objects.create(
        codigo=f"seg_form_{sufijo}",
        nombre="Formulario seguridad",
        tipo_formulario=TipoFormulario.ENCUESTA,
        estado=EstadoFormulario.PUBLICADO,
    )


def _crear_sesion_con_pregunta(
    token_cliente: str | None = None,
) -> tuple[SesionAnonima, str, str, str]:
    """Crea sesion con pregunta y token para pruebas de seguridad."""
    formulario = _crear_formulario_publicado()
    version = FormularioVersion.objects.create(
        formulario=formulario,
        numero_version=1,
        estado=EstadoFormulario.PUBLICADO,
        es_publicada=True,
    )
    uuid_sesion = uuid.uuid4()
    token = token_cliente or generar_token_cliente_seguro()
    sesion = SesionAnonima.objects.create(
        uuid_sesion=uuid_sesion,
        formulario=formulario,
        version_formulario=version,
        token_cliente=token,
    )
    seccion = SeccionFormulario.objects.create(
        formulario_version=version,
        codigo="sec_seg",
        titulo="Seccion seguridad",
        orden=1,
    )
    Pregunta.objects.create(
        seccion=seccion,
        codigo="P_SEG",
        texto="Pregunta seguridad",
        tipo_pregunta=TipoPregunta.NUMERO,
        orden=1,
    )
    return sesion, str(uuid_sesion), token, str(formulario.uuid)


@override_settings(API_INTERNA_TOKEN=TOKEN_API_INTERNA_PRUEBA)
class SeguridadSesionesTests(TestCase):
    """Pruebas de token de sesion anonima."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.formulario = _crear_formulario_publicado()
        FormularioVersion.objects.create(
            formulario=self.formulario,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
        )
        self.uuid_sesion = uuid.uuid4()

    def test_crear_sesion_genera_token_si_no_se_envia(self) -> None:
        respuesta = self.cliente.post(
            URL_SESIONES,
            {
                "uuid_sesion": str(self.uuid_sesion),
                "uuid_formulario": str(self.formulario.uuid),
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertTrue(respuesta.json()["token_cliente"])

    def test_crear_sesion_conserva_token_enviado(self) -> None:
        token_enviado = generar_token_cliente_seguro()
        respuesta = self.cliente.post(
            URL_SESIONES,
            {
                "uuid_sesion": str(self.uuid_sesion),
                "uuid_formulario": str(self.formulario.uuid),
                "token_cliente": token_enviado,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.json()["token_cliente"], token_enviado)

    def test_respuesta_sin_token_retorna_403(self) -> None:
        _, uuid_sesion, _, _ = _crear_sesion_con_pregunta()
        respuesta = self.cliente.post(
            URL_RESPUESTAS,
            {
                "uuid_sesion": uuid_sesion,
                "codigo_pregunta": "P_SEG",
                "valor": 10,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_respuesta_con_token_incorrecto_retorna_403(self) -> None:
        _, uuid_sesion, _, _ = _crear_sesion_con_pregunta()
        respuesta = self.cliente.post(
            URL_RESPUESTAS,
            {
                "uuid_sesion": uuid_sesion,
                "codigo_pregunta": "P_SEG",
                "valor": 10,
                "token_cliente": "token-invalido",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            respuesta.json()["detalle"],
            MensajesSesionApi.TOKEN_SESION_INVALIDO,
        )

    def test_respuesta_con_token_correcto_guarda(self) -> None:
        _, uuid_sesion, token, _ = _crear_sesion_con_pregunta()
        respuesta = self.cliente.post(
            URL_RESPUESTAS,
            {
                "uuid_sesion": uuid_sesion,
                "codigo_pregunta": "P_SEG",
                "valor": 15,
                "token_cliente": token,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

    def test_resumen_sin_token_retorna_403(self) -> None:
        sesion, _, _, _ = _crear_sesion_con_pregunta()
        url = f"/api/v1/sesiones/{sesion.uuid_sesion}/resumen/"
        respuesta = self.cliente.get(url)
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_resumen_con_token_correcto_retorna_200(self) -> None:
        sesion, uuid_sesion, token, _ = _crear_sesion_con_pregunta()
        self.cliente.post(
            URL_RESPUESTAS,
            {
                "uuid_sesion": uuid_sesion,
                "codigo_pregunta": "P_SEG",
                "valor": 20,
                "token_cliente": token,
            },
            format="json",
        )
        url = f"/api/v1/sesiones/{sesion.uuid_sesion}/resumen/"
        respuesta = self.cliente.get(url, **headers_sesion_anonima(uuid_sesion, token))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)


@override_settings(API_INTERNA_TOKEN=TOKEN_API_INTERNA_PRUEBA)
class SeguridadArchivosTests(TestCase):
    """Pruebas de seguridad del repositorio documental."""

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_upload_sin_sesion_token_retorna_403(self) -> None:
        from django.core.files.uploadedfile import SimpleUploadedFile

        archivo = SimpleUploadedFile(
            "sin_token.png",
            CONTENIDO_PNG_MINIMO,
            content_type="image/png",
        )
        respuesta = self.cliente.post(
            URL_ARCHIVOS,
            {
                "archivo": archivo,
                "tipo_archivo": TipoArchivo.IMAGEN,
                "origen": OrigenArchivo.OTRO,
            },
            format="multipart",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_con_sesion_token_valido_retorna_201(self) -> None:
        from django.core.files.uploadedfile import SimpleUploadedFile

        _, uuid_sesion, token, _ = _crear_sesion_con_pregunta()
        archivo = SimpleUploadedFile(
            "con_token.png",
            CONTENIDO_PNG_MINIMO,
            content_type="image/png",
        )
        respuesta = self.cliente.post(
            URL_ARCHIVOS,
            {
                "archivo": archivo,
                "tipo_archivo": TipoArchivo.IMAGEN,
                "origen": OrigenArchivo.RESPUESTA,
                "uuid_sesion": uuid_sesion,
            },
            format="multipart",
            **headers_sesion_anonima(uuid_sesion, token),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

    def test_archivo_publico_se_descarga_sin_token(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="publico.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.OTRO,
            es_publico=True,
        )
        respuesta = self.cliente.get(f"{URL_ARCHIVOS}{archivo.uuid}/descargar/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_archivo_privado_requiere_api_interna(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="privado.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.OTRO,
            es_publico=False,
        )
        sin_token = self.cliente.get(f"{URL_ARCHIVOS}{archivo.uuid}/descargar/")
        self.assertEqual(sin_token.status_code, status.HTTP_403_FORBIDDEN)

        con_token = self.cliente.get(
            f"{URL_ARCHIVOS}{archivo.uuid}/descargar/",
            **headers_api_interna(),
        )
        self.assertEqual(con_token.status_code, status.HTTP_200_OK)

    def test_delete_requiere_api_interna(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="eliminar.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.OTRO,
        )
        sin_token = self.cliente.delete(f"{URL_ARCHIVOS}{archivo.uuid}/")
        self.assertEqual(sin_token.status_code, status.HTTP_403_FORBIDDEN)

        con_token = self.cliente.delete(
            f"{URL_ARCHIVOS}{archivo.uuid}/",
            **headers_api_interna(),
        )
        self.assertEqual(con_token.status_code, status.HTTP_200_OK)


@override_settings(API_INTERNA_TOKEN=TOKEN_API_INTERNA_PRUEBA)
class SeguridadApiInternaTests(TestCase):
    """Pruebas de acceso con token de API interna temporal."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        PlantillaNotificacion.objects.create(
            codigo="plantilla_seg",
            nombre="Plantilla seguridad",
            tipo=TipoNotificacion.CORREO,
            asunto="Asunto",
            contenido_texto="Texto",
            esta_activa=True,
        )

    def test_analitica_sin_api_interna_retorna_403(self) -> None:
        respuesta = self.cliente.get(URL_ANALITICA)
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_analitica_con_api_interna_retorna_200(self) -> None:
        respuesta = self.cliente.get(URL_ANALITICA, **headers_api_interna())
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_exportacion_sin_api_interna_retorna_403(self) -> None:
        respuesta = self.cliente.post(
            URL_EXPORTACIONES_RESPUESTAS,
            {"formato": "json"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_exportacion_con_api_interna_retorna_201(self) -> None:
        respuesta = self.cliente.post(
            URL_EXPORTACIONES_RESPUESTAS,
            {"formato": "json"},
            format="json",
            **headers_api_interna(),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

    def test_notificacion_sin_api_interna_retorna_403(self) -> None:
        respuesta = self.cliente.post(
            URL_NOTIFICACIONES_PROBAR,
            {
                "codigo_plantilla": "plantilla_seg",
                "destinatario": "test@ejemplo.com",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_notificacion_con_api_interna_retorna_201(self) -> None:
        respuesta = self.cliente.post(
            URL_NOTIFICACIONES_PROBAR,
            {
                "codigo_plantilla": "plantilla_seg",
                "destinatario": "test@ejemplo.com",
            },
            format="json",
            **headers_api_interna(),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)


@override_settings(API_INTERNA_TOKEN="")
class SeguridadApiInternaSinConfiguracionTests(TestCase):
    """Pruebas cuando API_INTERNA_TOKEN no esta configurado."""

    def test_analitica_denegada_sin_token_configurado(self) -> None:
        cliente = APIClient()
        respuesta = cliente.get(
            URL_ANALITICA,
            HTTP_X_API_INTERNA="cualquier-valor",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            respuesta.json()["detalle"],
            MensajesAccesoApi.API_INTERNA_NO_CONFIGURADA,
        )
