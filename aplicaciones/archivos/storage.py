"""
Interfaz y backends de almacenamiento del repositorio documental.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from django.conf import settings


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


def obtener_storage_backend() -> StorageBackend:
    """Retorna el backend de almacenamiento configurado para el entorno."""
    return LocalStorageBackend()
