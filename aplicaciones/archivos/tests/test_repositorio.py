"""
Pruebas del repositorio documental transversal.
"""

import tempfile
import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from aplicaciones.archivos.storage import LocalStorageBackend
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.archivos.constantes import (
    EstadoArchivo,
    OrigenArchivo,
    TipoArchivo,
    MensajesArchivoApi,
)
from aplicaciones.archivos.excepciones import (
    ArchivoNoEncontradoError,
    ArchivoValidacionError,
)
from aplicaciones.archivos.servicios import (
    calcular_checksum,
    construir_url,
    eliminar_archivo,
    guardar_archivo,
    leer_contenido_archivo,
    obtener_archivo,
    preparar_asociacion_archivo_respuesta,
)
from aplicaciones.comun.tests.helpers_seguridad import (
    TOKEN_API_INTERNA_PRUEBA,
    headers_api_interna,
    headers_sesion_anonima,
)
from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    TipoFormulario,
)
from aplicaciones.sesiones_anonimas.models import SesionAnonima
from aplicaciones.sesiones_anonimas.seguridad import generar_token_cliente_seguro
from aplicaciones.archivos.validadores import validar_archivo, validar_extension

URL_ARCHIVOS = "/api/v1/archivos/"

CONTENIDO_PNG_MINIMO = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


class ArchivosServiciosTests(TestCase):
    """Pruebas de servicios del repositorio documental."""

    def test_calcular_checksum(self) -> None:
        contenido = b"contenido de prueba"
        checksum = calcular_checksum(contenido)
        self.assertEqual(len(checksum), 64)

    def test_guardar_archivo_crea_registro(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="imagen.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.OTRO,
        )
        self.assertEqual(archivo.extension, "png")
        self.assertEqual(archivo.estado, EstadoArchivo.ACTIVO)
        self.assertTrue(archivo.ruta_relativa.startswith("repositorio/"))

    def test_soft_delete_archivo(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="eliminar.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.OTRO,
        )
        eliminado = eliminar_archivo(archivo.uuid)
        self.assertTrue(eliminado.esta_eliminado)
        self.assertEqual(eliminado.estado, EstadoArchivo.ELIMINADO)

    def test_leer_contenido_archivo(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="leer.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.OTRO,
        )
        contenido = leer_contenido_archivo(archivo)
        self.assertEqual(contenido, CONTENIDO_PNG_MINIMO)

    def test_obtener_archivo_inexistente(self) -> None:
        with self.assertRaises(ArchivoNoEncontradoError):
            obtener_archivo(uuid.uuid4())

    def test_preparar_asociacion_archivo_respuesta(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="respuesta.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.RESPUESTA,
        )
        asociado = preparar_asociacion_archivo_respuesta(archivo.uuid)
        self.assertIsNotNone(asociado)
        self.assertEqual(asociado.uuid, archivo.uuid)


class ArchivosValidadoresTests(TestCase):
    """Pruebas de validadores de archivos."""

    def test_validar_extension_prohibida(self) -> None:
        with self.assertRaises(ArchivoValidacionError):
            validar_extension("malware.exe")

    def test_validar_mime_y_tamano(self) -> None:
        extension = validar_archivo(
            "foto.png",
            "image/png",
            len(CONTENIDO_PNG_MINIMO),
            TipoArchivo.IMAGEN,
        )
        self.assertEqual(extension, "png")

    def test_validar_tamano_no_permitido(self) -> None:
        with self.assertRaises(ArchivoValidacionError) as contexto:
            validar_archivo(
                "grande.png",
                "image/png",
                50 * 1024 * 1024,
                TipoArchivo.IMAGEN,
            )
        self.assertEqual(
            contexto.exception.mensaje,
            MensajesArchivoApi.TAMANO_NO_PERMITIDO,
        )


class LocalStorageBackendTests(TestCase):
    """Pruebas del backend de almacenamiento local."""

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_backend_guardar_leer_eliminar(self) -> None:
        backend = LocalStorageBackend()
        ruta = "repositorio/test/archivo.txt"
        contenido = b"prueba backend"
        backend.guardar(ruta, contenido)
        self.assertTrue(backend.existe(ruta))
        self.assertEqual(backend.leer(ruta), contenido)
        self.assertIn("media/", backend.obtener_url(ruta))
        backend.eliminar(ruta)
        self.assertFalse(backend.existe(ruta))


class ArchivosApiTests(TestCase):
    """Pruebas de API del repositorio documental."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        formulario = Formulario.objects.create(
            codigo="arch_api",
            nombre="Form archivo API",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.PUBLICADO,
        )
        version = FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
            estado=EstadoFormulario.PUBLICADO,
            es_publicada=True,
        )
        self.uuid_sesion = str(uuid.uuid4())
        self.token_cliente = generar_token_cliente_seguro()
        SesionAnonima.objects.create(
            uuid_sesion=self.uuid_sesion,
            formulario=formulario,
            version_formulario=version,
            token_cliente=self.token_cliente,
        )

    @override_settings(API_INTERNA_TOKEN=TOKEN_API_INTERNA_PRUEBA)
    def test_api_upload(self) -> None:
        archivo = SimpleUploadedFile(
            "subida.png",
            CONTENIDO_PNG_MINIMO,
            content_type="image/png",
        )
        respuesta = self.cliente.post(
            URL_ARCHIVOS,
            {
                "archivo": archivo,
                "tipo_archivo": TipoArchivo.IMAGEN,
                "origen": OrigenArchivo.OTRO,
                "uuid_sesion": self.uuid_sesion,
            },
            format="multipart",
            **headers_sesion_anonima(self.uuid_sesion, self.token_cliente),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertIn("uuid", respuesta.json())

    def test_api_consulta_metadatos(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="meta.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.OTRO,
            es_publico=True,
        )
        respuesta = self.cliente.get(f"{URL_ARCHIVOS}{archivo.uuid}/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()["nombre_original"], "meta.png")

    def test_api_descarga(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="descarga.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.OTRO,
            es_publico=True,
        )
        respuesta = self.cliente.get(f"{URL_ARCHIVOS}{archivo.uuid}/descargar/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        contenido = b"".join(respuesta.streaming_content)
        self.assertEqual(contenido, CONTENIDO_PNG_MINIMO)

    @override_settings(API_INTERNA_TOKEN=TOKEN_API_INTERNA_PRUEBA)
    def test_api_delete(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="delete.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.OTRO,
        )
        respuesta = self.cliente.delete(
            f"{URL_ARCHIVOS}{archivo.uuid}/",
            **headers_api_interna(),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()["estado"], EstadoArchivo.ELIMINADO)

    def test_construir_url_absoluta(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="url.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.OTRO,
        )
        url = construir_url(archivo, None)
        self.assertIsNotNone(url)
        self.assertIn("media/", url)
