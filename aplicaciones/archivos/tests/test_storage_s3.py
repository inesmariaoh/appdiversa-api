"""
Pruebas del backend de almacenamiento en S3 y del selector de backend.
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from aplicaciones.archivos.storage import (
    LocalStorageBackend,
    S3StorageBackend,
    obtener_storage_backend,
)

RUTA = "repositorio/2026/archivo.txt"
CONTENIDO = b"contenido de prueba s3"
BUCKET = "appdiversa-media"
REGION = "us-east-1"


@override_settings(
    AWS_S3_BUCKET=BUCKET,
    AWS_S3_REGION=REGION,
    AWS_S3_ENDPOINT_URL="",
    AWS_S3_PUBLIC_BASE_URL="",
    AWS_S3_PREFIJO="",
)
class S3StorageBackendTests(TestCase):
    """Pruebas unitarias del backend S3 con cliente simulado."""

    def setUp(self) -> None:
        self.cliente = MagicMock()
        self.backend = S3StorageBackend(cliente=self.cliente)

    def test_guardar_sube_objeto(self) -> None:
        ruta = self.backend.guardar(RUTA, CONTENIDO)
        self.assertEqual(ruta, RUTA)
        self.cliente.put_object.assert_called_once_with(
            Bucket=BUCKET,
            Key=RUTA,
            Body=CONTENIDO,
        )

    def test_leer_devuelve_contenido(self) -> None:
        cuerpo = MagicMock()
        cuerpo.read.return_value = CONTENIDO
        self.cliente.get_object.return_value = {"Body": cuerpo}
        self.assertEqual(self.backend.leer(RUTA), CONTENIDO)

    def test_eliminar_borra_objeto(self) -> None:
        self.backend.eliminar(RUTA)
        self.cliente.delete_object.assert_called_once_with(Bucket=BUCKET, Key=RUTA)

    def test_existe_true(self) -> None:
        self.assertTrue(self.backend.existe(RUTA))

    def test_existe_false_cuando_no_encuentra(self) -> None:
        from botocore.exceptions import ClientError

        self.cliente.head_object.side_effect = ClientError({}, "HeadObject")
        self.assertFalse(self.backend.existe(RUTA))

    def test_obtener_url_por_defecto(self) -> None:
        url = self.backend.obtener_url(RUTA)
        self.assertEqual(
            url,
            f"https://{BUCKET}.s3.{REGION}.amazonaws.com/{RUTA}",
        )

    @override_settings(AWS_S3_PUBLIC_BASE_URL="https://cdn.appdiversa.co")
    def test_obtener_url_con_base_publica(self) -> None:
        backend = S3StorageBackend(cliente=self.cliente)
        self.assertEqual(
            backend.obtener_url(RUTA),
            f"https://cdn.appdiversa.co/{RUTA}",
        )

    @override_settings(AWS_S3_PREFIJO="medios")
    def test_prefijo_se_aplica_a_la_clave(self) -> None:
        backend = S3StorageBackend(cliente=self.cliente)
        backend.guardar(RUTA, CONTENIDO)
        self.cliente.put_object.assert_called_once_with(
            Bucket=BUCKET,
            Key=f"medios/{RUTA}",
            Body=CONTENIDO,
        )


class ObtenerStorageBackendTests(TestCase):
    """Pruebas del selector de backend segun configuracion."""

    @override_settings(STORAGE_BACKEND="local")
    def test_selecciona_local_por_defecto(self) -> None:
        self.assertIsInstance(obtener_storage_backend(), LocalStorageBackend)

    @override_settings(STORAGE_BACKEND="s3", AWS_S3_BUCKET=BUCKET, AWS_S3_PREFIJO="")
    def test_selecciona_s3_cuando_configurado(self) -> None:
        with patch(
            "aplicaciones.archivos.storage._construir_cliente_s3",
            return_value=MagicMock(),
        ):
            self.assertIsInstance(obtener_storage_backend(), S3StorageBackend)
