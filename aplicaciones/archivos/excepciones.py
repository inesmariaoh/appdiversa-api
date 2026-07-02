"""
Excepciones funcionales del repositorio documental.
"""

from aplicaciones.archivos.constantes import MensajesArchivoApi


class ArchivoNoEncontradoError(Exception):
    """Indica que el archivo solicitado no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesArchivoApi.ARCHIVO_NO_ENCONTRADO)
        self.mensaje = MensajesArchivoApi.ARCHIVO_NO_ENCONTRADO


class ArchivoValidacionError(Exception):
    """Indica que el archivo no cumple las validaciones de seguridad."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
