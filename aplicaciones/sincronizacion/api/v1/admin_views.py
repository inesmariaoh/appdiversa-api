"""
Vistas administrativas para la resolucion manual de conflictos de sincronizacion.
"""

from uuid import UUID

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.comun.autenticacion_sesion import AutenticacionSesionApi
from aplicaciones.comun.paginacion import construir_respuesta_paginada
from aplicaciones.sincronizacion.api.v1.serializers import (
    ConflictoSincronizacionSerializer,
    ResolverConflictoEntradaSerializer,
)
from aplicaciones.sincronizacion.constantes import (
    FiltrosConflicto,
    MensajesConflictoApi,
)
from aplicaciones.sincronizacion.excepciones import (
    ConflictoNoEncontradoError,
    ResolucionConflictoInvalidaError,
)
from aplicaciones.sincronizacion.permisos import PermisoAdministrarSincronizacion
from aplicaciones.sincronizacion.selectores import listar_conflictos
from aplicaciones.sincronizacion.servicios import resolver_conflicto

_AUTENTICACION_SESION = [AutenticacionSesionApi]
_DETALLE_ERROR = inline_serializer(
    name="DetalleErrorConflictos",
    fields={"detalle": serializers.CharField()},
)

_FILTROS_CONFLICTO = (
    FiltrosConflicto.TIPO_CONFLICTO,
    FiltrosConflicto.RESOLUCION,
    FiltrosConflicto.RESUELTO,
    FiltrosConflicto.UUID_LOCAL,
)


class ConflictosListView(APIView):
    """Lista los conflictos de sincronizacion registrados."""

    permission_classes = [PermisoAdministrarSincronizacion]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Sincronizacion"],
        summary="Listar conflictos de sincronización",
        responses={
            status.HTTP_200_OK: ConflictoSincronizacionSerializer(many=True),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna conflictos paginados aplicando filtros opcionales."""
        filtros = {
            clave: solicitud.query_params[clave]
            for clave in _FILTROS_CONFLICTO
            if clave in solicitud.query_params
        }
        conflictos = listar_conflictos(filtros)
        return construir_respuesta_paginada(
            self,
            conflictos,
            ConflictoSincronizacionSerializer,
            solicitud,
        )


class ResolverConflictoView(APIView):
    """Resuelve manualmente un conflicto aplicando el valor elegido."""

    permission_classes = [PermisoAdministrarSincronizacion]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Sincronizacion"],
        summary="Resolver conflicto de sincronización",
        request=ResolverConflictoEntradaSerializer,
        responses={
            status.HTTP_200_OK: ConflictoSincronizacionSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def post(self, solicitud: Request, conflicto_uuid: UUID) -> Response:
        """Aplica la resolucion indicada y devuelve el conflicto actualizado."""
        entrada = ResolverConflictoEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        try:
            conflicto = resolver_conflicto(
                conflicto_uuid,
                datos["resolucion"],
                datos.get("valor_manual"),
            )
        except ConflictoNoEncontradoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ResolucionConflictoInvalidaError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )
        salida = ConflictoSincronizacionSerializer(conflicto)
        return Response(
            {"detalle": MensajesConflictoApi.CONFLICTO_RESUELTO, "conflicto": salida.data},
            status=status.HTTP_200_OK,
        )
