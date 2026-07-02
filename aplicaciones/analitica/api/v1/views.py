"""
Vistas de la API de analitica.
"""

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter, OpenApiResponse
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.analitica.api.v1.serializers import (
    FiltrosRespuestasAnaliticasSerializer,
    RespuestaAnaliticaSerializer,
)
from aplicaciones.analitica.excepciones import FiltroAnaliticaInvalidoError
from aplicaciones.analitica.servicios import listar_respuestas_analiticas
from aplicaciones.comun.permisos import PermisoApiInternaTemporal
from aplicaciones.comun.spectacular_parametros import PARAMETROS_API_INTERNA

_DETALLE_ERROR_SERIALIZER = inline_serializer(
    name="DetalleErrorAnalitica",
    fields={"detalle": serializers.CharField()},
)


class ListarRespuestasAnaliticasView(APIView):
    """Lista respuestas normalizadas para validacion de analitica."""

    permission_classes = [PermisoApiInternaTemporal]

    @extend_schema(
        tags=["Analitica"],
        summary="Listar respuestas analíticas",
        description=(
            "Endpoint de datos analíticos. Requiere token de API interna autorizado."
        ),
        parameters=[
            OpenApiParameter(
                name="formulario_codigo",
                type=str,
                required=False,
                description="Código del formulario a filtrar.",
            ),
            OpenApiParameter(
                name="fecha_inicio",
                type=str,
                required=False,
                description="Fecha inicial de sesión en formato ISO.",
            ),
            OpenApiParameter(
                name="fecha_fin",
                type=str,
                required=False,
                description="Fecha final de sesión en formato ISO.",
            ),
            OpenApiParameter(
                name="estado_sesion",
                type=str,
                required=False,
                description="Estado de la sesión anónima.",
            ),
            *PARAMETROS_API_INTERNA,
        ],
        responses={
            status.HTTP_200_OK: RespuestaAnaliticaSerializer(many=True),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna respuestas en formato plano orientado a BI."""
        filtros = FiltrosRespuestasAnaliticasSerializer(data=solicitud.query_params)
        filtros.is_valid(raise_exception=True)
        datos = filtros.validated_data

        try:
            respuestas = listar_respuestas_analiticas(
                formulario_codigo=datos.get("formulario_codigo") or None,
                fecha_inicio=datos.get("fecha_inicio") or None,
                fecha_fin=datos.get("fecha_fin") or None,
                estado_sesion=datos.get("estado_sesion") or None,
            )
        except FiltroAnaliticaInvalidoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializador = RespuestaAnaliticaSerializer(respuestas, many=True)
        return Response(serializador.data, status=status.HTTP_200_OK)
