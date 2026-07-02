"""
Validacion de valores de respuesta contra catalogos parametrizables.
"""

from typing import Any

from aplicaciones.catalogos.models import ItemCatalogo
from aplicaciones.formularios.models import Pregunta, TipoPregunta
from aplicaciones.respuestas.excepciones import ValorNoPerteneceCatalogoError

TIPOS_VALOR_SIMPLE_CATALOGO = frozenset(
    {
        TipoPregunta.RADIO,
        TipoPregunta.SELECT,
        TipoPregunta.AUTOCOMPLETE,
    },
)

TIPOS_VALOR_LISTA_CATALOGO = frozenset(
    {
        TipoPregunta.CHECKBOX,
        TipoPregunta.SELECT_MULTIPLE,
    },
)


def _obtener_mapa_items_catalogo(catalogo_id: int) -> dict[str, str]:
    """Construye un mapa de codigos y valores validos hacia el codigo del item."""
    items = ItemCatalogo.objects.filter(
        catalogo_id=catalogo_id,
        esta_eliminado=False,
        esta_activo=True,
    )
    mapa: dict[str, str] = {}
    for item in items.iterator():
        mapa[item.codigo] = item.codigo
        if item.valor:
            mapa[item.valor] = item.codigo
    return mapa


def _resolver_codigo_item(mapa_items: dict[str, str], valor: Any) -> str | None:
    """Resuelve el codigo de item valido desde un valor enviado."""
    clave = str(valor)
    return mapa_items.get(clave)


def _normalizar_valor_lista_catalogo(
    mapa_items: dict[str, str],
    valor: Any,
) -> list[str]:
    """Normaliza una lista de valores contra items del catalogo."""
    if not isinstance(valor, list):
        raise ValorNoPerteneceCatalogoError()

    codigos_normalizados: list[str] = []
    for elemento in valor:
        codigo_item = _resolver_codigo_item(mapa_items, elemento)
        if codigo_item is None:
            raise ValorNoPerteneceCatalogoError()
        codigos_normalizados.append(codigo_item)

    return codigos_normalizados


def validar_y_normalizar_valor_catalogo(
    pregunta: Pregunta,
    valor: Any,
) -> Any:
    """Valida y normaliza un valor de respuesta contra el catalogo asociado."""
    if not pregunta.usa_catalogo or pregunta.catalogo_asociado_id is None:
        return valor

    mapa_items = _obtener_mapa_items_catalogo(pregunta.catalogo_asociado_id)

    if pregunta.tipo_pregunta in TIPOS_VALOR_LISTA_CATALOGO:
        return _normalizar_valor_lista_catalogo(mapa_items, valor)

    if pregunta.tipo_pregunta in TIPOS_VALOR_SIMPLE_CATALOGO:
        codigo_item = _resolver_codigo_item(mapa_items, valor)
        if codigo_item is None:
            raise ValorNoPerteneceCatalogoError()
        return codigo_item

    raise ValorNoPerteneceCatalogoError()
