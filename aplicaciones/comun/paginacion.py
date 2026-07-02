"""
Paginacion estandar reutilizable para la API.
"""

from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

TAMANO_PAGINA_POR_DEFECTO = 25
TAMANO_PAGINA_MAXIMO = 200
PARAMETRO_PAGINA = "pagina"
PARAMETRO_TAMANO_PAGINA = "tamano_pagina"


class PaginacionEstandar(PageNumberPagination):
    """Paginacion parametrizable comun para los listados de la API."""

    page_query_param = PARAMETRO_PAGINA
    page_size_query_param = PARAMETRO_TAMANO_PAGINA

    def get_page_size(self, request: Request) -> int:
        """Obtiene el tamano de pagina respetando el tope maximo configurado."""
        self.page_size = getattr(
            settings,
            "PAGINACION_TAMANO_PAGINA",
            TAMANO_PAGINA_POR_DEFECTO,
        )
        self.max_page_size = getattr(
            settings,
            "PAGINACION_TAMANO_MAXIMO",
            TAMANO_PAGINA_MAXIMO,
        )
        return super().get_page_size(request)


def construir_respuesta_paginada(
    vista: APIView,
    consulta,
    serializador_clase: type[BaseSerializer],
    solicitud: Request,
) -> Response:
    """Pagina una consulta y devuelve la respuesta serializada estandar."""
    paginador = PaginacionEstandar()
    pagina = paginador.paginate_queryset(consulta, solicitud, view=vista)
    serializador = serializador_clase(pagina, many=True)
    return paginador.get_paginated_response(serializador.data)
