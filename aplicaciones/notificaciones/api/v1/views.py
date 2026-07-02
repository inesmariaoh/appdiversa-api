"""
Vistas de la API del motor de notificaciones.
"""

from uuid import UUID

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.comun.permisos import PermisoApiInternaTemporal
from aplicaciones.comun.spectacular_parametros import PARAMETROS_API_INTERNA
from aplicaciones.notificaciones.api.v1.serializers import (
    NotificacionSerializer,
    ProbarNotificacionEntradaSerializer,
)
from aplicaciones.notificaciones.excepciones import (
    NotificacionNoEncontradaError,
    PlantillaNotificacionNoEncontradaError,
)
from aplicaciones.notificaciones.selectores import listar_notificaciones_registros
from aplicaciones.notificaciones.servicios import obtener_notificacion, probar_notificacion

_DETALLE_ERROR_SERIALIZER = inline_serializer(
    name="DetalleErrorNotificacion",
    fields={"detalle": serializers.CharField()},
)


class ListarNotificacionesView(APIView):
    """Lista notificaciones registradas en el sistema."""

    permission_classes = [PermisoApiInternaTemporal]

    @extend_schema(
        tags=["Notificaciones"],
        summary="Listar notificaciones",
        parameters=PARAMETROS_API_INTERNA,
        responses={status.HTTP_200_OK: NotificacionSerializer(many=True)},
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna las notificaciones registradas."""
        notificaciones = listar_notificaciones_registros()
        serializador = NotificacionSerializer(notificaciones, many=True)
        return Response(serializador.data, status=status.HTTP_200_OK)


class DetalleNotificacionView(APIView):
    """Consulta una notificacion por UUID."""

    permission_classes = [PermisoApiInternaTemporal]

    @extend_schema(
        tags=["Notificaciones"],
        summary="Consultar notificacion",
        parameters=PARAMETROS_API_INTERNA,
        responses={
            status.HTTP_200_OK: NotificacionSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def get(self, solicitud: Request, uuid_notificacion: UUID) -> Response:
        """Retorna el detalle de una notificacion."""
        try:
            notificacion = obtener_notificacion(uuid_notificacion)
        except NotificacionNoEncontradaError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializador = NotificacionSerializer(notificacion)
        return Response(serializador.data, status=status.HTTP_200_OK)


class ProbarNotificacionView(APIView):
    """Genera una notificacion de prueba sin envio externo."""

    permission_classes = [PermisoApiInternaTemporal]

    @extend_schema(
        tags=["Notificaciones"],
        summary="Probar generacion de notificacion",
        description=(
            "Genera y registra una notificacion sin enviarla a proveedores externos. "
            "Requiere token temporal de API interna hasta integrar Keycloak."
        ),
        parameters=PARAMETROS_API_INTERNA,
        request=ProbarNotificacionEntradaSerializer,
        responses={
            status.HTTP_201_CREATED: NotificacionSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Genera una notificacion de prueba."""
        entrada = ProbarNotificacionEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        try:
            notificacion = probar_notificacion(
                codigo_plantilla=datos["codigo_plantilla"],
                destinatario=datos["destinatario"],
                variables=datos.get("variables"),
            )
        except PlantillaNotificacionNoEncontradaError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializador = NotificacionSerializer(notificacion)
        return Response(serializador.data, status=status.HTTP_201_CREATED)
