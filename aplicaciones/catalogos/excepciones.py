"""
Excepciones funcionales del modulo de catalogos.
"""

from aplicaciones.catalogos.constantes import MensajesCatalogoAdmin, MensajesCatalogoApi


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


class CatalogoDuplicadoError(Exception):
    """Indica que ya existe un catalogo con el codigo indicado."""

    def __init__(self) -> None:
        super().__init__(MensajesCatalogoAdmin.CODIGO_DUPLICADO)
        self.mensaje = MensajesCatalogoAdmin.CODIGO_DUPLICADO


class ItemCatalogoDuplicadoError(Exception):
    """Indica que ya existe un item con el codigo indicado en el catalogo."""

    def __init__(self) -> None:
        super().__init__(MensajesCatalogoAdmin.ITEM_CODIGO_DUPLICADO)
        self.mensaje = MensajesCatalogoAdmin.ITEM_CODIGO_DUPLICADO


class CatalogoProtegidoError(Exception):
    """Indica que un catalogo del sistema no puede eliminarse."""

    def __init__(self) -> None:
        super().__init__(MensajesCatalogoAdmin.CATALOGO_PROTEGIDO)
        self.mensaje = MensajesCatalogoAdmin.CATALOGO_PROTEGIDO
