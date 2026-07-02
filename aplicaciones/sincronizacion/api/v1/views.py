"""
Vistas de la API de sincronizacion offline.
"""

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.comun.spectacular_parametros import PARAMETROS_SESION_ANONIMA
from aplicaciones.respuestas.excepciones import SesionRespuestaNoExisteError
from aplicaciones.sesiones_anonimas.permisos import PermisoSesionAnonimaValida
from aplicaciones.sincronizacion.api.v1.serializers import (
    SincronizarBatchEntradaSerializer,
    SincronizarBatchSalidaSerializer,
)
from aplicaciones.sincronizacion.servicios import sincronizar_batch

_DETALLE_ERROR_SERIALIZER = inline_serializer(
    name="DetalleErrorSincronizacion",
    fields={"detalle": serializers.CharField()},
)


class SincronizarBatchView(APIView):
    """Procesa un lote de operaciones de sincronizacion offline."""

    permission_classes = [PermisoSesionAnonimaValida]

    @extend_schema(
        tags=["Sincronizacion"],
        summary="Sincronizar lote de respuestas offline",
        description=(
            "Procesa un lote de operaciones enviadas por un dispositivo offline. "
            "Cada operacion se valida con uuid_local y version_cliente para "
            "garantizar idempotencia. Los conflictos se resuelven con Last Write Wins "
            "y se registran sin perder informacion. Una operacion fallida no cancela "
            "el resto del lote."
        ),
        parameters=PARAMETROS_SESION_ANONIMA,
        request=SincronizarBatchEntradaSerializer,
        responses={
            status.HTTP_200_OK: SincronizarBatchSalidaSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Ejecuta la sincronizacion del lote recibido."""
        entrada = SincronizarBatchEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        try:
            resultado = sincronizar_batch(
                uuid_sesion=datos["uuid_sesion"],
                dispositivo=datos["dispositivo"],
                version_app=datos["version_app"],
                operaciones=datos["operaciones"],
            )
        except SesionRespuestaNoExisteError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializador = SincronizarBatchSalidaSerializer(
            {
                "operaciones_procesadas": resultado.operaciones_procesadas,
                "operaciones_actualizadas": resultado.operaciones_actualizadas,
                "duplicadas": resultado.duplicadas,
                "conflictos": resultado.conflictos,
                "errores": resultado.errores,
            },
        )
        return Response(serializador.data, status=status.HTTP_200_OK)
