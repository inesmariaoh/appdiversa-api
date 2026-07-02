"""
Vistas de la API publica de internacionalizacion.
"""

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.internacionalizacion.api.serializers import (
    FiltrosTraduccionesSerializer,
    TraduccionContenidoSerializer,
)
from aplicaciones.internacionalizacion.servicios import listar_traducciones

_PARAMETRO_IDIOMA = OpenApiParameter(
    name="idioma",
    type=str,
    required=False,
    description="Codigo ISO del idioma para filtrar traducciones.",
)

_PARAMETRO_ENTIDAD = OpenApiParameter(
    name="entidad",
    type=str,
    required=False,
    description="Nombre de la entidad traducible (Formulario, Pregunta, etc.).",
)

_PARAMETRO_ENTIDAD_UUID = OpenApiParameter(
    name="entidad_uuid",
    type=str,
    required=False,
    description="UUID de la entidad traducida.",
)

_PARAMETRO_CAMPO = OpenApiParameter(
    name="campo",
    type=str,
    required=False,
    description="Nombre del campo traducido.",
)


class ListarTraduccionesView(APIView):
    """Lista traducciones de contenido con filtros opcionales."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Internacionalizacion"],
        summary="Listar traducciones de contenido",
        description=(
            "Retorna traducciones activas con contenido textual y accesible "
            "multimodal. Los archivos se retornan como URLs absolutas cuando "
            "existen."
        ),
        parameters=[
            _PARAMETRO_IDIOMA,
            _PARAMETRO_ENTIDAD,
            _PARAMETRO_ENTIDAD_UUID,
            _PARAMETRO_CAMPO,
        ],
        responses={
            status.HTTP_200_OK: TraduccionContenidoSerializer(many=True),
        },
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna traducciones segun filtros opcionales."""
        filtros = FiltrosTraduccionesSerializer(data=solicitud.query_params)
        filtros.is_valid(raise_exception=True)
        datos = filtros.validated_data

        traducciones = listar_traducciones(
            codigo_idioma=datos.get("idioma"),
            entidad=datos.get("entidad"),
            entidad_uuid=datos.get("entidad_uuid"),
            campo=datos.get("campo"),
        )

        serializador = TraduccionContenidoSerializer(
            traducciones,
            many=True,
            context={"request": solicitud},
        )
        return Response(serializador.data, status=status.HTTP_200_OK)
