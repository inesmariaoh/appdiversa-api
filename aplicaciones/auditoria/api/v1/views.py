"""
Vistas de la API de consulta de registros de auditoria.
"""

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.auditoria.api.v1.serializers import (
    FiltrosAuditoriaSerializer,
    RegistroAuditoriaSerializer,
)
from aplicaciones.auditoria.constantes import MensajesAuditoriaApi
from aplicaciones.auditoria.permisos import PermisoConsultarAuditoria
from aplicaciones.auditoria.selectores import (
    FiltrosConsultaAuditoria,
    listar_registros_auditoria,
    obtener_registro_auditoria,
)
from aplicaciones.comun.autenticacion_sesion import AutenticacionSesionApi
from aplicaciones.comun.paginacion import construir_respuesta_paginada

_AUTENTICACION_SESION = [AutenticacionSesionApi]
_DETALLE_ERROR = inline_serializer(
    name="DetalleErrorAuditoria",
    fields={"detalle": serializers.CharField()},
)


def _construir_filtros(datos: dict) -> FiltrosConsultaAuditoria:
    """Traduce los datos validados a la estructura de filtros del selector."""
    return FiltrosConsultaAuditoria(
        entidad=datos.get("entidad", ""),
        entidad_id=datos.get("entidad_id", ""),
        accion=datos.get("accion", ""),
        usuario=datos.get("usuario"),
        fecha_inicio=datos.get("fecha_inicio"),
        fecha_fin=datos.get("fecha_fin"),
        busqueda=datos.get("busqueda", ""),
    )


class RegistrosAuditoriaListView(APIView):
    """Lista registros de auditoria con filtros y paginacion."""

    permission_classes = [PermisoConsultarAuditoria]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Auditoria"],
        summary="Listar registros de auditoria",
        parameters=[FiltrosAuditoriaSerializer],
        responses={status.HTTP_200_OK: RegistroAuditoriaSerializer(many=True)},
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna los registros de auditoria filtrados y paginados."""
        filtros_serializer = FiltrosAuditoriaSerializer(data=solicitud.query_params)
        filtros_serializer.is_valid(raise_exception=True)
        filtros = _construir_filtros(filtros_serializer.validated_data)
        registros = listar_registros_auditoria(filtros)
        return construir_respuesta_paginada(
            self,
            registros,
            RegistroAuditoriaSerializer,
            solicitud,
        )


class RegistroAuditoriaDetalleView(APIView):
    """Consulta el detalle de un registro de auditoria."""

    permission_classes = [PermisoConsultarAuditoria]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Auditoria"],
        summary="Detalle de registro de auditoria",
        responses={
            status.HTTP_200_OK: RegistroAuditoriaSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def get(self, solicitud: Request, registro_id: int) -> Response:
        """Retorna un registro de auditoria por identificador."""
        registro = obtener_registro_auditoria(registro_id)
        if registro is None:
            return Response(
                {"detalle": MensajesAuditoriaApi.REGISTRO_NO_ENCONTRADO},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializador = RegistroAuditoriaSerializer(registro)
        return Response(serializador.data, status=status.HTTP_200_OK)
