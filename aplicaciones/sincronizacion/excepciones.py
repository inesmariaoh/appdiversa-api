"""
Excepciones funcionales del motor de sincronizacion.
"""

from aplicaciones.sincronizacion.constantes import MensajesSincronizacionApi


class ChecksumInvalidoError(Exception):
    """Indica que el checksum de la operacion no coincide."""

    def __init__(self) -> None:
        super().__init__(MensajesSincronizacionApi.CHECKSUM_INVALIDO)
        self.mensaje = MensajesSincronizacionApi.CHECKSUM_INVALIDO


class RespuestaEliminadaSyncError(Exception):
    """Indica que la respuesta fue eliminada logicamente en el servidor."""

    def __init__(self) -> None:
        super().__init__(MensajesSincronizacionApi.RESPUESTA_ELIMINADA)
        self.mensaje = MensajesSincronizacionApi.RESPUESTA_ELIMINADA
