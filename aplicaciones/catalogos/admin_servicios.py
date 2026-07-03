"""
Servicios administrativos de catalogos parametrizables (alta, edicion y baja).
"""

from typing import Any

from django.db import transaction

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import crear_snapshot_modelo, registrar_auditoria
from aplicaciones.catalogos.excepciones import (
    CatalogoDuplicadoError,
    CatalogoProtegidoError,
    ItemCatalogoDuplicadoError,
    ItemCatalogoNoEncontradoError,
)
from aplicaciones.catalogos.models import Catalogo, ItemCatalogo
from aplicaciones.catalogos.selectores import (
    existe_codigo_catalogo,
    existe_codigo_item,
    obtener_item_por_codigo,
)

_CAMPOS_CATALOGO = ("codigo", "nombre", "descripcion", "tipo_catalogo", "esta_activo", "orden")
_CAMPOS_ITEM = (
    "codigo",
    "nombre",
    "descripcion",
    "valor",
    "codigo_externo",
    "metadatos",
    "orden",
    "esta_activo",
)


def _auditar(entidad: str, entidad_id: int, accion: str, snapshot: dict[str, Any]) -> None:
    """Registra una accion administrativa de catalogo en auditoria."""
    registrar_auditoria(
        entidad=entidad,
        entidad_id=str(entidad_id),
        accion=accion,
        valor_nuevo=snapshot,
        descripcion="Operacion administrativa sobre catalogo parametrizable.",
    )


@transaction.atomic
def crear_catalogo_admin(datos: dict[str, Any]) -> Catalogo:
    """Crea un catalogo validando la unicidad del codigo."""
    if existe_codigo_catalogo(datos["codigo"]):
        raise CatalogoDuplicadoError()
    catalogo = Catalogo.objects.create(
        **{campo: datos[campo] for campo in _CAMPOS_CATALOGO if campo in datos},
    )
    _auditar(Catalogo.__name__, catalogo.pk, AccionAuditoria.CREAR, crear_snapshot_modelo(catalogo))
    return catalogo


@transaction.atomic
def actualizar_catalogo_admin(catalogo: Catalogo, datos: dict[str, Any]) -> Catalogo:
    """Actualiza campos editables de un catalogo validando el codigo."""
    codigo_nuevo = datos.get("codigo")
    if codigo_nuevo and existe_codigo_catalogo(codigo_nuevo, excluir_id=catalogo.pk):
        raise CatalogoDuplicadoError()

    campos_actualizados = [campo for campo in _CAMPOS_CATALOGO if campo in datos]
    for campo in campos_actualizados:
        setattr(catalogo, campo, datos[campo])
    if campos_actualizados:
        catalogo.save(update_fields=[*campos_actualizados, "fecha_modificacion"])
        _auditar(
            Catalogo.__name__,
            catalogo.pk,
            AccionAuditoria.EDITAR,
            crear_snapshot_modelo(catalogo),
        )
    return catalogo


@transaction.atomic
def eliminar_catalogo_admin(catalogo: Catalogo) -> None:
    """Elimina logicamente un catalogo que no sea del sistema."""
    if catalogo.es_sistema:
        raise CatalogoProtegidoError()
    catalogo.esta_eliminado = True
    catalogo.save(update_fields=["esta_eliminado", "fecha_modificacion"])
    _auditar(
        Catalogo.__name__,
        catalogo.pk,
        AccionAuditoria.ELIMINAR,
        {"codigo": catalogo.codigo},
    )


def _resolver_item_padre(catalogo: Catalogo, codigo_padre: str | None) -> ItemCatalogo | None:
    """Resuelve el item padre por codigo dentro del catalogo indicado."""
    if not codigo_padre:
        return None
    item_padre = obtener_item_por_codigo(catalogo.codigo, codigo_padre)
    if item_padre is None:
        raise ItemCatalogoNoEncontradoError()
    return item_padre


@transaction.atomic
def crear_item_admin(catalogo: Catalogo, datos: dict[str, Any]) -> ItemCatalogo:
    """Crea un item en un catalogo validando la unicidad del codigo."""
    if existe_codigo_item(catalogo, datos["codigo"]):
        raise ItemCatalogoDuplicadoError()
    item_padre = _resolver_item_padre(catalogo, datos.get("codigo_padre"))
    item = ItemCatalogo.objects.create(
        catalogo=catalogo,
        item_padre=item_padre,
        **{campo: datos[campo] for campo in _CAMPOS_ITEM if campo in datos},
    )
    _auditar(ItemCatalogo.__name__, item.pk, AccionAuditoria.CREAR, crear_snapshot_modelo(item))
    return item


@transaction.atomic
def actualizar_item_admin(item: ItemCatalogo, datos: dict[str, Any]) -> ItemCatalogo:
    """Actualiza campos editables de un item validando el codigo."""
    codigo_nuevo = datos.get("codigo")
    if codigo_nuevo and existe_codigo_item(item.catalogo, codigo_nuevo, excluir_id=item.pk):
        raise ItemCatalogoDuplicadoError()

    campos_actualizados = [campo for campo in _CAMPOS_ITEM if campo in datos]
    for campo in campos_actualizados:
        setattr(item, campo, datos[campo])

    if "codigo_padre" in datos:
        item.item_padre = _resolver_item_padre(item.catalogo, datos.get("codigo_padre"))
        campos_actualizados.append("item_padre")

    if campos_actualizados:
        item.save(update_fields=[*campos_actualizados, "fecha_modificacion"])
        _auditar(
            ItemCatalogo.__name__,
            item.pk,
            AccionAuditoria.EDITAR,
            crear_snapshot_modelo(item),
        )
    return item


@transaction.atomic
def eliminar_item_admin(item: ItemCatalogo) -> None:
    """Elimina logicamente un item de catalogo."""
    item.esta_eliminado = True
    item.save(update_fields=["esta_eliminado", "fecha_modificacion"])
    _auditar(
        ItemCatalogo.__name__,
        item.pk,
        AccionAuditoria.ELIMINAR,
        {"codigo": item.codigo},
    )