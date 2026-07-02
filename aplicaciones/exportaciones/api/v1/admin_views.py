"""
Vistas administrativas de exportacion protegidas por RBAC de sesion.
"""

from uuid import UUID

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from django.http import HttpResponse
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.archivos.excepciones import ArchivoNoEncontradoError
from aplicaciones.archivos.servicios import leer_contenido_archivo
from aplicaciones.comun.autenticacion_sesion import AutenticacionSesionApi
from aplicaciones.exportaciones.api.v1.serializers import (
    ExportacionRespuestasEntradaSerializer,
    ExportacionSerializer,
)
from aplicaciones.exportaciones.constantes import (
    EstadoExportacion,
    MIME_POR_FORMATO,
    MensajesExportacionApi,
)
from aplicaciones.exportaciones.excepciones import ExportacionNoEncontradaError
from aplicaciones.exportaciones.servicios import exportar_respuestas, obtener_exportacion
from aplicaciones.usuarios.permisos import PermisoExportarRespuestas

_AUTENTICACION_SESION = [AutenticacionSesionApi]
_DETALLE_ERROR = inline_serializer(
    name="DetalleErrorAdminExportaciones",
    fields={"detalle": serializers.CharField()},
)


class AdminExportarRespuestasView(APIView):
    """Genera una exportacion de respuestas desde el panel administrativo."""

    permission_classes = [PermisoExportarRespuestas]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Admin Exportaciones"],
        summary="Exportar respuestas (panel)",
        request=ExportacionRespuestasEntradaSerializer,
        responses={status.HTTP_201_CREATED: ExportacionSerializer},
    )
    def post(self, solicitud: Request) -> Response:
        """Crea una exportacion de respuestas segun filtros del panel."""
        entrada = ExportacionRespuestasEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        exportacion = exportar_respuestas(
            formato=datos["formato"],
            parametros=datos.get("parametros"),
            usuario=solicitud.user.get_username(),
        )
        serializador = ExportacionSerializer(exportacion)
        return Response(serializador.data, status=status.HTTP_201_CREATED)


class AdminDescargarExportacionView(APIView):
    """Descarga el archivo generado de una exportacion finalizada."""

    permission_classes = [PermisoExportarRespuestas]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Admin Exportaciones"],
        summary="Descargar exportacion (panel)",
        responses={
            (status.HTTP_200_OK, "application/octet-stream"): bytes,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def get(self, solicitud: Request, uuid_exportacion: UUID) -> HttpResponse:
        """Retorna el contenido binario de la exportacion indicada."""
        try:
            exportacion = obtener_exportacion(uuid_exportacion)
        except ExportacionNoEncontradaError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        if exportacion.estado != EstadoExportacion.FINALIZADA or not exportacion.archivo_id:
            return Response(
                {"detalle": MensajesExportacionApi.EXPORTACION_NO_ENCONTRADA},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            contenido = leer_contenido_archivo(exportacion.archivo)
        except ArchivoNoEncontradoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        mime = MIME_POR_FORMATO[exportacion.formato]
        respuesta = HttpResponse(contenido, content_type=mime)
        nombre_archivo = exportacion.archivo.nombre_original
        respuesta["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'
        return respuesta
