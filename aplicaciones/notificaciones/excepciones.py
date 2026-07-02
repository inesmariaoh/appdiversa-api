"""
Excepciones funcionales del motor de notificaciones.
"""

from aplicaciones.notificaciones.constantes import MensajesNotificacionApi


class NotificacionNoEncontradaError(Exception):
    """Indica que la notificacion solicitada no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesNotificacionApi.NOTIFICACION_NO_ENCONTRADA)
        self.mensaje = MensajesNotificacionApi.NOTIFICACION_NO_ENCONTRADA


class PlantillaNotificacionNoEncontradaError(Exception):
    """Indica que la plantilla solicitada no existe o no esta activa."""

    def __init__(self) -> None:
        super().__init__(MensajesNotificacionApi.PLANTILLA_NO_ENCONTRADA)
        self.mensaje = MensajesNotificacionApi.PLANTILLA_NO_ENCONTRADA
