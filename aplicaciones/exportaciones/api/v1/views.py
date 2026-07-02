"""
Vistas de la API del motor de exportaciones.
"""

from uuid import UUID

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.comun.permisos import PermisoApiInternaTemporal
from aplicaciones.comun.spectacular_parametros import PARAMETROS_API_INTERNA

from aplicaciones.exportaciones.api.v1.serializers import (
    ExportacionAnaliticaEntradaSerializer,
    ExportacionCatalogosEntradaSerializer,
    ExportacionRespuestasEntradaSerializer,
    ExportacionSerializer,
)
from aplicaciones.exportaciones.excepciones import ExportacionNoEncontradaError
from aplicaciones.exportaciones.servicios import (
    exportar_analitica,
    exportar_catalogos,
    exportar_respuestas,
    obtener_exportacion,
)

_DETALLE_ERROR_SERIALIZER = inline_serializer(
    name="DetalleErrorExportacion",
    fields={"detalle": serializers.CharField()},
)


class ExportarRespuestasView(APIView):
    """Genera exportacion de respuestas de formularios."""

    permission_classes = [PermisoApiInternaTemporal]

    @extend_schema(
        tags=["Exportaciones"],
        summary="Exportar respuestas",
        parameters=PARAMETROS_API_INTERNA,
        request=ExportacionRespuestasEntradaSerializer,
        responses={
            status.HTTP_201_CREATED: ExportacionSerializer,
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Ejecuta exportacion de respuestas segun filtros."""
        entrada = ExportacionRespuestasEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        exportacion = exportar_respuestas(
            formato=datos["formato"],
            parametros=datos.get("parametros"),
            usuario=datos.get("usuario", ""),
        )
        serializador = ExportacionSerializer(exportacion)
        return Response(serializador.data, status=status.HTTP_201_CREATED)


class ExportarCatalogosView(APIView):
    """Genera exportacion de catalogos parametrizables."""

    permission_classes = [PermisoApiInternaTemporal]

    @extend_schema(
        tags=["Exportaciones"],
        summary="Exportar catalogos",
        parameters=PARAMETROS_API_INTERNA,
        request=ExportacionCatalogosEntradaSerializer,
        responses={
            status.HTTP_201_CREATED: ExportacionSerializer,
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Ejecuta exportacion de catalogos."""
        entrada = ExportacionCatalogosEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        exportacion = exportar_catalogos(
            formato=datos["formato"],
            parametros=datos.get("parametros"),
            usuario=datos.get("usuario", ""),
        )
        serializador = ExportacionSerializer(exportacion)
        return Response(serializador.data, status=status.HTTP_201_CREATED)


class ExportarAnaliticaView(APIView):
    """Genera exportacion de datos analiticos."""

    permission_classes = [PermisoApiInternaTemporal]

    @extend_schema(
        tags=["Exportaciones"],
        summary="Exportar analitica",
        parameters=PARAMETROS_API_INTERNA,
        request=ExportacionAnaliticaEntradaSerializer,
        responses={
            status.HTTP_201_CREATED: ExportacionSerializer,
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Ejecuta exportacion de analitica."""
        entrada = ExportacionAnaliticaEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        exportacion = exportar_analitica(
            formato=datos["formato"],
            parametros=datos.get("parametros"),
            usuario=datos.get("usuario", ""),
        )
        serializador = ExportacionSerializer(exportacion)
        return Response(serializador.data, status=status.HTTP_201_CREATED)


class DetalleExportacionView(APIView):
    """Consulta el estado de una exportacion."""

    permission_classes = [PermisoApiInternaTemporal]

    @extend_schema(
        tags=["Exportaciones"],
        summary="Consultar exportacion",
        parameters=PARAMETROS_API_INTERNA,
        responses={
            status.HTTP_200_OK: ExportacionSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def get(self, solicitud: Request, uuid_exportacion: UUID) -> Response:
        """Retorna el detalle de una exportacion."""
        try:
            exportacion = obtener_exportacion(uuid_exportacion)
        except ExportacionNoEncontradaError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializador = ExportacionSerializer(exportacion)
        return Response(serializador.data, status=status.HTTP_200_OK)
