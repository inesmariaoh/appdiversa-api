"""
Validacion de respuestas compuestas de ubicacion geografica (departamento/municipio).
"""

from typing import Any

from aplicaciones.catalogos.models import Catalogo, ItemCatalogo
from aplicaciones.formularios.constantes_geograficas import CLAVES_UBICACION_GEOGRAFICA
from aplicaciones.formularios.models import Pregunta, TipoPregunta
from aplicaciones.respuestas.excepciones import ValorInvalidoError, ValorNoPerteneceCatalogoError


def _obtener_item_catalogo(catalogo: Catalogo, codigo: str) -> ItemCatalogo | None:
    """Retorna un item activo del catalogo por codigo."""
    return (
        ItemCatalogo.objects.filter(
            catalogo=catalogo,
            codigo=codigo,
            esta_activo=True,
            esta_eliminado=False,
        )
        .select_related("item_padre")
        .first()
    )


def _validar_texto_no_vacio(valor: object) -> str:
    """Valida que un campo de texto no este vacio."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValorInvalidoError()
    return valor.strip()


def validar_y_normalizar_ubicacion_geografica(
    pregunta: Pregunta,
    valor: Any,
) -> dict[str, str]:
    """Valida y normaliza el JSON de una respuesta de ubicacion geografica."""
    if not isinstance(valor, dict):
        raise ValorInvalidoError()

    claves_recibidas = set(valor.keys())
    if not CLAVES_UBICACION_GEOGRAFICA.issubset(claves_recibidas):
        raise ValorInvalidoError()

    departamento_codigo = _validar_texto_no_vacio(valor.get("departamento_codigo"))
    departamento_nombre = _validar_texto_no_vacio(valor.get("departamento_nombre"))
    municipio_codigo = _validar_texto_no_vacio(valor.get("municipio_codigo"))
    municipio_nombre = _validar_texto_no_vacio(valor.get("municipio_nombre"))

    codigo_catalogo_departamento = pregunta.codigo_catalogo_departamento.strip()
    if not codigo_catalogo_departamento:
        raise ValorInvalidoError()

    catalogo_departamentos = Catalogo.objects.filter(
        codigo=codigo_catalogo_departamento,
        esta_activo=True,
        esta_eliminado=False,
    ).first()
    if catalogo_departamentos is None:
        raise ValorNoPerteneceCatalogoError()

    item_departamento = _obtener_item_catalogo(catalogo_departamentos, departamento_codigo)
    if item_departamento is None:
        raise ValorNoPerteneceCatalogoError()

    if pregunta.catalogo_asociado_id is None:
        raise ValorInvalidoError()

    item_municipio = _obtener_item_catalogo(pregunta.catalogo_asociado, municipio_codigo)
    if item_municipio is None:
        raise ValorNoPerteneceCatalogoError()

    if item_municipio.item_padre_id is not None:
        if item_municipio.item_padre.codigo != departamento_codigo:
            raise ValorNoPerteneceCatalogoError()

    nombre_departamento_catalogo = item_departamento.nombre.strip()
    nombre_municipio_catalogo = item_municipio.nombre.strip()
    if departamento_nombre != nombre_departamento_catalogo:
        departamento_nombre = nombre_departamento_catalogo
    if municipio_nombre != nombre_municipio_catalogo:
        municipio_nombre = nombre_municipio_catalogo

    return {
        "departamento_codigo": departamento_codigo,
        "departamento_nombre": departamento_nombre,
        "municipio_codigo": municipio_codigo,
        "municipio_nombre": municipio_nombre,
    }


def es_pregunta_ubicacion_geografica(pregunta: Pregunta) -> bool:
    """Indica si la pregunta almacena una ubicacion geografica compuesta."""
    return pregunta.tipo_pregunta == TipoPregunta.UBICACION_GEOGRAFICA
