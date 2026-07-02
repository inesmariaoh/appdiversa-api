"""
Excepciones funcionales del modulo de analitica.
"""

from aplicaciones.analitica.constantes import MensajesAnaliticaApi


class FiltroAnaliticaInvalidoError(Exception):
    """Indica que un filtro de consulta analitica no es valido."""

    def __init__(self, mensaje: str = MensajesAnaliticaApi.FILTRO_FECHA_INVALIDO) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
