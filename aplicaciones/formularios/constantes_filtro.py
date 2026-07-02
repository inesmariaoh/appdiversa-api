"""
Constantes reutilizables para validacion de preguntas filtro/preliminares.
"""

from aplicaciones.formularios.models import TipoValidacionFiltro

CLAVE_VALOR_FILTRO = "valor"
CLAVE_VALORES_FILTRO = "valores"

TIPOS_VALIDACION_FILTRO = frozenset(
    {
        TipoValidacionFiltro.RANGO_EDAD,
        TipoValidacionFiltro.OPCION_EXACTA,
        TipoValidacionFiltro.LISTA_OPCIONES,
        TipoValidacionFiltro.RANGO_NUMERICO,
        TipoValidacionFiltro.BOOLEANO,
    },
)
