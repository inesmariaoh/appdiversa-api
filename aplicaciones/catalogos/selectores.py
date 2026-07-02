"""
Selectores de consulta para catalogos parametrizables.
"""

from django.db.models import Q, QuerySet

from aplicaciones.catalogos.constantes import LIMITE_MAXIMO_ITEMS_CATALOGO
from aplicaciones.catalogos.models import Catalogo, ItemCatalogo


def obtener_catalogo_por_codigo(codigo_catalogo: str) -> Catalogo | None:
    """Retorna un catalogo activo por su codigo o None si no existe."""
    return Catalogo.objects.filter(
        codigo=codigo_catalogo,
        esta_eliminado=False,
    ).first()


def obtener_item_por_codigo(
    codigo_catalogo: str,
    codigo_item: str,
) -> ItemCatalogo | None:
    """Retorna un item activo por codigo de catalogo e item o None."""
    return (
        ItemCatalogo.objects.filter(
            catalogo__codigo=codigo_catalogo,
            catalogo__esta_eliminado=False,
            codigo=codigo_item,
            esta_eliminado=False,
        )
        .select_related("catalogo", "item_padre")
        .first()
    )


def obtener_catalogos_activos() -> QuerySet[Catalogo]:
    """Retorna catalogos activos y no eliminados."""
    return Catalogo.objects.filter(
        esta_activo=True,
        esta_eliminado=False,
    ).order_by("orden", "nombre")


def obtener_items_hijos_item(
    item: ItemCatalogo,
    solo_activos: bool = True,
) -> QuerySet[ItemCatalogo]:
    """Retorna hijos directos de un item de catalogo."""
    consulta = ItemCatalogo.objects.filter(
        item_padre=item,
        esta_eliminado=False,
    ).select_related("catalogo", "item_padre")

    if solo_activos:
        consulta = consulta.filter(esta_activo=True)

    return consulta.order_by("orden", "nombre")


def obtener_items_por_catalogo(
    codigo_catalogo: str,
    codigo_padre: str | None = None,
    solo_activos: bool = True,
    busqueda: str | None = None,
    limite: int | None = None,
) -> QuerySet[ItemCatalogo]:
    """Retorna items de un catalogo con filtros opcionales de padre y estado."""
    consulta = ItemCatalogo.objects.filter(
        catalogo__codigo=codigo_catalogo,
        catalogo__esta_eliminado=False,
        esta_eliminado=False,
    ).select_related("catalogo", "item_padre")

    if solo_activos:
        consulta = consulta.filter(esta_activo=True)

    if codigo_padre is not None:
        consulta = consulta.filter(item_padre__codigo=codigo_padre)

    if busqueda is not None and busqueda.strip():
        termino = busqueda.strip()
        consulta = consulta.filter(
            Q(nombre__icontains=termino) | Q(codigo__icontains=termino),
        )

    consulta = consulta.order_by("orden", "nombre")

    if limite is not None:
        limite_aplicado = min(limite, LIMITE_MAXIMO_ITEMS_CATALOGO)
        return consulta[:limite_aplicado]

    return consulta
