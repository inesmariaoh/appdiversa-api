"""
Vistas de la API del repositorio documental.
"""

from io import BytesIO
from uuid import UUID

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from django.http import FileResponse
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.archivos.api.v1.serializers import (
    ArchivoRepositorioSerializer,
    SubirArchivoEntradaSerializer,
)
from aplicaciones.archivos.excepciones import (
    ArchivoNoEncontradoError,
    ArchivoValidacionError,
)
from aplicaciones.archivos.permisos import PermisoArchivoPublicoOApiInterna
from aplicaciones.archivos.servicios import (
    eliminar_archivo,
    guardar_archivo,
    leer_contenido_archivo,
    obtener_archivo,
)
from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import crear_snapshot_modelo, registrar_auditoria
from aplicaciones.archivos.models import ArchivoRepositorio
from aplicaciones.comun.permisos import (
    PermisoApiInternaTemporal,
    PermisoSesionAnonimaOApiInterna,
)
from aplicaciones.comun.spectacular_parametros import (
    PARAMETROS_API_INTERNA,
    PARAMETROS_SESION_ANONIMA,
)

_DETALLE_ERROR_SERIALIZER = inline_serializer(
    name="DetalleErrorArchivo",
    fields={"detalle": serializers.CharField()},
)


class SubirArchivoView(APIView):
    """Sube un archivo al repositorio documental."""

    permission_classes = [PermisoSesionAnonimaOApiInterna]

    @extend_schema(
        tags=["Archivos"],
        summary="Subir archivo al repositorio",
        description=(
            "Registra un archivo en el repositorio documental transversal. "
            "Requiere sesion anonima valida o token de API interna temporal."
        ),
        parameters=PARAMETROS_SESION_ANONIMA + PARAMETROS_API_INTERNA,
        request=SubirArchivoEntradaSerializer,
        responses={
            status.HTTP_201_CREATED: ArchivoRepositorioSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Sube y registra un archivo en el repositorio."""
        entrada = SubirArchivoEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        archivo_subido = datos["archivo"]
        contenido = archivo_subido.read()

        try:
            archivo = guardar_archivo(
                contenido=contenido,
                nombre_original=archivo_subido.name,
                mime_type=archivo_subido.content_type or "application/octet-stream",
                tipo_archivo=datos["tipo_archivo"],
                origen=datos["origen"],
                descripcion=datos.get("descripcion", ""),
                es_publico=datos.get("es_publico", False),
                metadatos=datos.get("metadatos"),
                usuario_keycloak=datos.get("usuario_keycloak", ""),
                uuid_sesion=datos.get("uuid_sesion"),
            )
        except ArchivoValidacionError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )

        registrar_auditoria(
            entidad=ArchivoRepositorio.__name__,
            entidad_id=str(archivo.pk),
            accion=AccionAuditoria.CREAR,
            valor_nuevo=crear_snapshot_modelo(archivo),
            descripcion="Subida de archivo con sesion o API interna valida.",
        )

        serializador = ArchivoRepositorioSerializer(
            archivo,
            context={"request": solicitud},
        )
        return Response(serializador.data, status=status.HTTP_201_CREATED)


class ArchivoDetalleView(APIView):
    """Consulta y elimina archivos del repositorio."""

    def get_permissions(self) -> list:
        """Asigna permisos segun el metodo HTTP."""
        if self.request.method == "DELETE":
            return [PermisoApiInternaTemporal()]
        return [PermisoArchivoPublicoOApiInterna()]

    @extend_schema(
        tags=["Archivos"],
        summary="Consultar metadatos de archivo",
        parameters=PARAMETROS_API_INTERNA,
        responses={
            status.HTTP_200_OK: ArchivoRepositorioSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def get(self, solicitud: Request, uuid_archivo: UUID) -> Response:
        """Retorna metadatos del archivo solicitado."""
        try:
            archivo = obtener_archivo(uuid_archivo)
        except ArchivoNoEncontradoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializador = ArchivoRepositorioSerializer(
            archivo,
            context={"request": solicitud},
        )
        return Response(serializador.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Archivos"],
        summary="Eliminar archivo del repositorio",
        description="Realiza soft delete del archivo en el repositorio documental.",
        parameters=PARAMETROS_API_INTERNA,
        responses={
            status.HTTP_200_OK: ArchivoRepositorioSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def delete(self, solicitud: Request, uuid_archivo: UUID) -> Response:
        """Elimina logicamente el archivo solicitado."""
        try:
            archivo = eliminar_archivo(uuid_archivo)
        except ArchivoNoEncontradoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializador = ArchivoRepositorioSerializer(
            archivo,
            context={"request": solicitud},
        )
        return Response(serializador.data, status=status.HTTP_200_OK)


class DescargarArchivoView(APIView):
    """Descarga el contenido de un archivo del repositorio."""

    permission_classes = [PermisoArchivoPublicoOApiInterna]

    @extend_schema(
        tags=["Archivos"],
        summary="Descargar archivo del repositorio",
        parameters=PARAMETROS_API_INTERNA,
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Contenido binario del archivo."),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def get(self, solicitud: Request, uuid_archivo: UUID) -> FileResponse | Response:
        """Retorna el contenido binario del archivo solicitado."""
        try:
            archivo = obtener_archivo(uuid_archivo)
            contenido = leer_contenido_archivo(archivo)
        except ArchivoNoEncontradoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not archivo.es_publico:
            registrar_auditoria(
                entidad=ArchivoRepositorio.__name__,
                entidad_id=str(archivo.pk),
                accion=AccionAuditoria.CONSULTAR,
                descripcion="Descarga de archivo privado mediante API interna.",
            )

        return FileResponse(
            BytesIO(contenido),
            content_type=archivo.mime_type,
            as_attachment=True,
            filename=archivo.nombre_original,
        )
