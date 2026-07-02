"""
Excepciones funcionales del modulo de catalogos.
"""

from aplicaciones.catalogos.constantes import MensajesCatalogoApi


class CatalogoNoEncontradoError(Exception):
    """Indica que el catalogo solicitado no existe o no esta disponible."""

    def __init__(self) -> None:
        super().__init__(MensajesCatalogoApi.CATALOGO_NO_ENCONTRADO)
        self.mensaje = MensajesCatalogoApi.CATALOGO_NO_ENCONTRADO


class ItemCatalogoNoEncontradoError(Exception):
    """Indica que el item solicitado no existe o no esta disponible."""

    def __init__(self) -> None:
        super().__init__(MensajesCatalogoApi.ITEM_NO_ENCONTRADO)
        self.mensaje = MensajesCatalogoApi.ITEM_NO_ENCONTRADO
