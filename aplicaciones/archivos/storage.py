"""
Interfaz y backends de almacenamiento del repositorio documental.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from django.conf import settings

BACKEND_LOCAL = "local"
BACKEND_S3 = "s3"


class StorageBackend(ABC):
    """Contrato de almacenamiento desacoplado del proveedor fisico."""

    @abstractmethod
    def guardar(self, ruta_relativa: str, contenido: bytes) -> str:
        """Persiste contenido y retorna la ruta relativa almacenada."""

    @abstractmethod
    def eliminar(self, ruta_relativa: str) -> None:
        """Elimina el archivo almacenado en la ruta indicada."""

    @abstractmethod
    def existe(self, ruta_relativa: str) -> bool:
        """Indica si existe un archivo en la ruta relativa."""

    @abstractmethod
    def obtener_url(self, ruta_relativa: str) -> str:
        """Retorna la URL relativa publica del archivo."""

    @abstractmethod
    def leer(self, ruta_relativa: str) -> bytes:
        """Lee el contenido binario del archivo almacenado."""


class LocalStorageBackend(StorageBackend):
    """Backend de almacenamiento en disco local para desarrollo."""

    def __init__(self, directorio_base: Path | None = None) -> None:
        self._directorio_base = directorio_base or Path(settings.MEDIA_ROOT)

    def _resolver_ruta_absoluta(self, ruta_relativa: str) -> Path:
        """Resuelve la ruta absoluta dentro del directorio base."""
        return self._directorio_base / ruta_relativa

    def guardar(self, ruta_relativa: str, contenido: bytes) -> str:
        """Persiste contenido en el directorio local configurado."""
        ruta_absoluta = self._resolver_ruta_absoluta(ruta_relativa)
        ruta_absoluta.parent.mkdir(parents=True, exist_ok=True)
        ruta_absoluta.write_bytes(contenido)
        return ruta_relativa

    def eliminar(self, ruta_relativa: str) -> None:
        """Elimina el archivo del directorio local si existe."""
        ruta_absoluta = self._resolver_ruta_absoluta(ruta_relativa)
        if ruta_absoluta.exists():
            ruta_absoluta.unlink()

    def existe(self, ruta_relativa: str) -> bool:
        """Indica si el archivo existe en el directorio local."""
        return self._resolver_ruta_absoluta(ruta_relativa).exists()

    def obtener_url(self, ruta_relativa: str) -> str:
        """Retorna la URL relativa bajo MEDIA_URL."""
        media_url = settings.MEDIA_URL
        if not media_url.endswith("/"):
            media_url = f"{media_url}/"
        return f"{media_url}{ruta_relativa}"

    def leer(self, ruta_relativa: str) -> bytes:
        """Lee el contenido binario desde el directorio local."""
        return self._resolver_ruta_absoluta(ruta_relativa).read_bytes()


def _construir_cliente_s3() -> Any:
    """Construye el cliente boto3 de S3 con la configuracion del entorno."""
    import boto3

    parametros: dict[str, Any] = {
        "service_name": "s3",
        "region_name": settings.AWS_S3_REGION or None,
        "aws_access_key_id": settings.AWS_S3_ACCESS_KEY_ID or None,
        "aws_secret_access_key": settings.AWS_S3_SECRET_ACCESS_KEY or None,
    }
    if settings.AWS_S3_ENDPOINT_URL:
        parametros["endpoint_url"] = settings.AWS_S3_ENDPOINT_URL
    return boto3.client(**parametros)


class S3StorageBackend(StorageBackend):
    """Backend de almacenamiento en Amazon S3 o compatible, parametrizable."""

    def __init__(self, cliente: Any | None = None) -> None:
        self._cliente = cliente if cliente is not None else _construir_cliente_s3()
        self._bucket = settings.AWS_S3_BUCKET
        self._prefijo = settings.AWS_S3_PREFIJO.strip("/")

    def _clave(self, ruta_relativa: str) -> str:
        """Construye la clave del objeto aplicando el prefijo configurado."""
        if self._prefijo:
            return f"{self._prefijo}/{ruta_relativa}"
        return ruta_relativa

    def guardar(self, ruta_relativa: str, contenido: bytes) -> str:
        """Sube el contenido al bucket configurado y retorna la ruta relativa."""
        self._cliente.put_object(
            Bucket=self._bucket,
            Key=self._clave(ruta_relativa),
            Body=contenido,
        )
        return ruta_relativa

    def eliminar(self, ruta_relativa: str) -> None:
        """Elimina el objeto del bucket configurado."""
        self._cliente.delete_object(
            Bucket=self._bucket,
            Key=self._clave(ruta_relativa),
        )

    def existe(self, ruta_relativa: str) -> bool:
        """Indica si el objeto existe en el bucket configurado."""
        from botocore.exceptions import ClientError

        try:
            self._cliente.head_object(
                Bucket=self._bucket,
                Key=self._clave(ruta_relativa),
            )
        except ClientError:
            return False
        return True

    def obtener_url(self, ruta_relativa: str) -> str:
        """Retorna la URL publica del objeto segun la configuracion del bucket."""
        clave = self._clave(ruta_relativa)
        base_publica = settings.AWS_S3_PUBLIC_BASE_URL.rstrip("/")
        if base_publica:
            return f"{base_publica}/{clave}"
        if settings.AWS_S3_ENDPOINT_URL:
            endpoint = settings.AWS_S3_ENDPOINT_URL.rstrip("/")
            return f"{endpoint}/{self._bucket}/{clave}"
        return f"https://{self._bucket}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{clave}"

    def leer(self, ruta_relativa: str) -> bytes:
        """Lee el contenido binario del objeto almacenado en el bucket."""
        respuesta = self._cliente.get_object(
            Bucket=self._bucket,
            Key=self._clave(ruta_relativa),
        )
        return respuesta["Body"].read()


def obtener_storage_backend() -> StorageBackend:
    """Retorna el backend de almacenamiento configurado para el entorno."""
    if settings.STORAGE_BACKEND == BACKEND_S3:
        return S3StorageBackend()
    return LocalStorageBackend()
