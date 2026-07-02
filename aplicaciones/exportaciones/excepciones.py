"""
Excepciones funcionales del motor de exportaciones.
"""

from aplicaciones.exportaciones.constantes import MensajesExportacionApi


class ExportacionNoEncontradaError(Exception):
    """Indica que la exportacion solicitada no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesExportacionApi.EXPORTACION_NO_ENCONTRADA)
        self.mensaje = MensajesExportacionApi.EXPORTACION_NO_ENCONTRADA


class FormatoExportacionNoSoportadoError(Exception):
    """Indica que el formato solicitado no esta implementado."""

    def __init__(self) -> None:
        super().__init__(MensajesExportacionApi.FORMATO_NO_SOPORTADO)
        self.mensaje = MensajesExportacionApi.FORMATO_NO_SOPORTADO


class ParametrosExportacionInvalidosError(Exception):
    """Indica que los parametros de exportacion no son validos."""

    def __init__(self) -> None:
        super().__init__(MensajesExportacionApi.PARAMETROS_INVALIDOS)
        self.mensaje = MensajesExportacionApi.PARAMETROS_INVALIDOS
