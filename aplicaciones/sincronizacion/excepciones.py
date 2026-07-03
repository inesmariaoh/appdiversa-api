"""
Excepciones funcionales del motor de sincronizacion.
"""

from aplicaciones.sincronizacion.constantes import (
    MensajesConflictoApi,
    MensajesSincronizacionApi,
)


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


class ConflictoNoEncontradoError(Exception):
    """Indica que el conflicto solicitado no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesConflictoApi.CONFLICTO_NO_ENCONTRADO)
        self.mensaje = MensajesConflictoApi.CONFLICTO_NO_ENCONTRADO


class ResolucionConflictoInvalidaError(Exception):
    """Indica que la resolucion solicitada no puede aplicarse al conflicto."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
