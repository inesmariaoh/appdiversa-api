"""
Constantes del modulo de catalogos parametrizables.
"""


class MensajesCatalogoApi:
    """Mensajes funcionales de la API de catalogos."""

    CATALOGO_NO_ENCONTRADO = "El catálogo solicitado no existe o no está disponible."
    ITEM_NO_ENCONTRADO = "El ítem solicitado no existe o no está disponible."


class MensajesCatalogoAdmin:
    """Mensajes de la API administrativa de catalogos."""

    SIN_PERMISO = "No tiene permisos para administrar catálogos."
    CODIGO_DUPLICADO = "Ya existe un catálogo con el código indicado."
    ITEM_CODIGO_DUPLICADO = "Ya existe un ítem con el código indicado en el catálogo."
    CATALOGO_PROTEGIDO = "El catálogo del sistema no puede eliminarse."
    ITEM_PADRE_NO_ENCONTRADO = "El ítem padre indicado no existe en el catálogo."


LIMITE_MAXIMO_ITEMS_CATALOGO = 1000


class TiposCatalogo:
    """Tipos de catalogo soportados por el motor parametrizable."""

    GEOGRAFICO = "geografico"
    JERARQUICO = "jerarquico"
    DEMOGRAFICO = "demografico"
    SOCIOECONOMICO = "socioeconomico"
    DISCAPACIDAD = "discapacidad"
    IDENTIDAD = "identidad"
    GENERAL = "general"


class DivipolaConstantes:
    """Parametros de la carga DIVIPOLA desde Datos Abiertos Colombia."""

    URL_API = "https://www.datos.gov.co/resource/gdxc-w37w.json"
    LIMITE_API = 5000
    RECURSO_SOCRATA = "gdxc-w37w"
    FUENTE = "DIVIPOLA"
    CODIGO_CATALOGO_DEPARTAMENTOS = "departamentos"
    CODIGO_CATALOGO_MUNICIPIOS = "municipios"
    NOMBRE_CATALOGO_DEPARTAMENTOS = "Departamentos"
    NOMBRE_CATALOGO_MUNICIPIOS = "Municipios"


TIPOS_CATALOGO_GEOGRAFICO = frozenset(
    {
        TiposCatalogo.GEOGRAFICO,
        TiposCatalogo.JERARQUICO,
    },
)


def es_tipo_catalogo_geografico(tipo_catalogo: str) -> bool:
    """Indica si un tipo de catalogo corresponde a jerarquias geograficas."""
    return tipo_catalogo in TIPOS_CATALOGO_GEOGRAFICO
