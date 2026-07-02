"""
Servicios de catalogos parametrizables empresariales.
"""

from django.db.models import QuerySet

from aplicaciones.catalogos.excepciones import (
    CatalogoNoEncontradoError,
    ItemCatalogoNoEncontradoError,
)
from aplicaciones.catalogos.models import Catalogo, ItemCatalogo
from aplicaciones.catalogos.selectores import (
    obtener_catalogos_activos,
    obtener_item_por_codigo,
    obtener_items_hijos_item,
    obtener_items_por_catalogo,
)


def crear_catalogo_si_no_existe(
    codigo: str,
    nombre: str,
    tipo_catalogo: str,
    descripcion: str = "",
) -> Catalogo:
    """Crea un catalogo si no existe uno con el mismo codigo."""
    catalogo = Catalogo.todos.filter(codigo=codigo).first()
    if catalogo is not None:
        return catalogo

    return Catalogo.objects.create(
        codigo=codigo,
        nombre=nombre,
        tipo_catalogo=tipo_catalogo,
        descripcion=descripcion,
    )


def crear_item_catalogo_si_no_existe(
    catalogo: Catalogo,
    codigo: str,
    nombre: str,
    valor: str = "",
    item_padre: ItemCatalogo | None = None,
    codigo_externo: str = "",
    metadatos: dict | None = None,
) -> ItemCatalogo:
    """Crea un item si no existe uno con el mismo codigo en el catalogo."""
    item = ItemCatalogo.todos.filter(
        catalogo=catalogo,
        codigo=codigo,
    ).first()
    if item is not None:
        return item

    return ItemCatalogo.objects.create(
        catalogo=catalogo,
        codigo=codigo,
        nombre=nombre,
        valor=valor,
        item_padre=item_padre,
        codigo_externo=codigo_externo,
        metadatos=metadatos,
    )


def obtener_items_catalogo(
    codigo_catalogo: str,
    codigo_padre: str | None = None,
    solo_activos: bool = True,
    busqueda: str | None = None,
    limite: int | None = None,
) -> QuerySet[ItemCatalogo]:
    """Retorna items de un catalogo aplicando filtros de padre y estado activo."""
    if not Catalogo.objects.filter(
        codigo=codigo_catalogo,
        esta_eliminado=False,
    ).exists():
        raise CatalogoNoEncontradoError()

    return obtener_items_por_catalogo(
        codigo_catalogo=codigo_catalogo,
        codigo_padre=codigo_padre,
        solo_activos=solo_activos,
        busqueda=busqueda,
        limite=limite,
    )


def listar_catalogos_activos() -> QuerySet[Catalogo]:
    """Retorna catalogos activos y no eliminados para consumo publico."""
    return obtener_catalogos_activos()


def listar_items_catalogo_publico(
    codigo_catalogo: str,
    codigo_padre: str | None = None,
    solo_activos: bool = True,
    busqueda: str | None = None,
    limite: int | None = None,
) -> QuerySet[ItemCatalogo]:
    """Retorna items de un catalogo para consumo publico de la API."""
    return obtener_items_catalogo(
        codigo_catalogo=codigo_catalogo,
        codigo_padre=codigo_padre,
        solo_activos=solo_activos,
        busqueda=busqueda,
        limite=limite,
    )


def listar_hijos_item_catalogo(
    codigo_catalogo: str,
    codigo_item: str,
    solo_activos: bool = True,
) -> QuerySet[ItemCatalogo]:
    """Retorna hijos de un item dentro de su catalogo."""
    item = obtener_item_por_codigo(codigo_catalogo, codigo_item)
    if item is None:
        raise ItemCatalogoNoEncontradoError()

    return obtener_items_hijos_item(item=item, solo_activos=solo_activos)
