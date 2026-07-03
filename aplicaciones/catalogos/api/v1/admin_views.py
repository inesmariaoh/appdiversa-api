"""
Vistas de la API administrativa de catalogos parametrizables.
"""

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.catalogos.admin_servicios import (
    actualizar_catalogo_admin,
    actualizar_item_admin,
    crear_catalogo_admin,
    crear_item_admin,
    eliminar_catalogo_admin,
    eliminar_item_admin,
)
from aplicaciones.catalogos.api.v1.admin_serializers import (
    CatalogoAdminEntradaSerializer,
    CatalogoAdminSerializer,
    ItemCatalogoAdminEntradaSerializer,
    ItemCatalogoAdminSerializer,
)
from aplicaciones.catalogos.constantes import MensajesCatalogoApi
from aplicaciones.catalogos.excepciones import (
    CatalogoDuplicadoError,
    CatalogoProtegidoError,
    ItemCatalogoDuplicadoError,
    ItemCatalogoNoEncontradoError,
)
from aplicaciones.catalogos.permisos import PermisoGestionarCatalogos
from aplicaciones.catalogos.selectores import (
    listar_catalogos_admin,
    listar_items_admin,
    obtener_catalogo_admin_por_id,
    obtener_item_admin_por_id,
)
from aplicaciones.comun.autenticacion_sesion import AutenticacionSesionApi
from aplicaciones.comun.paginacion import construir_respuesta_paginada

_AUTENTICACION_SESION = [AutenticacionSesionApi]
_DETALLE_ERROR = inline_serializer(
    name="DetalleErrorCatalogoAdmin",
    fields={"detalle": serializers.CharField()},
)


def _respuesta_no_encontrado(mensaje: str) -> Response:
    """Construye una respuesta 404 con el mensaje indicado."""
    return Response({"detalle": mensaje}, status=status.HTTP_404_NOT_FOUND)


def _error_catalogo_no_encontrado() -> Response:
    """Construye la respuesta 404 estandar de catalogo no encontrado."""
    return _respuesta_no_encontrado(MensajesCatalogoApi.CATALOGO_NO_ENCONTRADO)


def _respuesta_error(mensaje: str) -> Response:
    """Construye una respuesta 400 con el mensaje indicado."""
    return Response({"detalle": mensaje}, status=status.HTTP_400_BAD_REQUEST)


class CatalogosAdminListCreateView(APIView):
    """Lista y crea catalogos parametrizables."""

    permission_classes = [PermisoGestionarCatalogos]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Catalogos"],
        summary="Listar catálogos (admin)",
        responses={status.HTTP_200_OK: CatalogoAdminSerializer(many=True)},
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna catalogos paginados con filtros opcionales."""
        filtros = {
            clave: solicitud.query_params[clave]
            for clave in ("tipo_catalogo", "busqueda")
            if clave in solicitud.query_params
        }
        catalogos = listar_catalogos_admin(filtros)
        return construir_respuesta_paginada(
            self,
            catalogos,
            CatalogoAdminSerializer,
            solicitud,
        )

    @extend_schema(
        tags=["Catalogos"],
        summary="Crear catálogo (admin)",
        request=CatalogoAdminEntradaSerializer,
        responses={
            status.HTTP_201_CREATED: CatalogoAdminSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Crea un catalogo parametrizable."""
        entrada = CatalogoAdminEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        try:
            catalogo = crear_catalogo_admin(entrada.validated_data)
        except CatalogoDuplicadoError as error:
            return _respuesta_error(error.mensaje)
        salida = CatalogoAdminSerializer(catalogo)
        return Response(salida.data, status=status.HTTP_201_CREATED)


class CatalogoAdminDetalleView(APIView):
    """Consulta, actualiza y elimina un catalogo parametrizable."""

    permission_classes = [PermisoGestionarCatalogos]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Catalogos"],
        summary="Detalle de catálogo (admin)",
        responses={
            status.HTTP_200_OK: CatalogoAdminSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def get(self, solicitud: Request, catalogo_id: int) -> Response:
        """Retorna el detalle de un catalogo."""
        catalogo = obtener_catalogo_admin_por_id(catalogo_id)
        if catalogo is None:
            return _error_catalogo_no_encontrado()
        return Response(CatalogoAdminSerializer(catalogo).data)

    @extend_schema(
        tags=["Catalogos"],
        summary="Actualizar catálogo (admin)",
        request=CatalogoAdminEntradaSerializer,
        responses={
            status.HTTP_200_OK: CatalogoAdminSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def patch(self, solicitud: Request, catalogo_id: int) -> Response:
        """Actualiza campos editables de un catalogo."""
        catalogo = obtener_catalogo_admin_por_id(catalogo_id)
        if catalogo is None:
            return _error_catalogo_no_encontrado()
        entrada = CatalogoAdminEntradaSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        try:
            catalogo = actualizar_catalogo_admin(catalogo, entrada.validated_data)
        except CatalogoDuplicadoError as error:
            return _respuesta_error(error.mensaje)
        return Response(CatalogoAdminSerializer(catalogo).data)

    @extend_schema(
        tags=["Catalogos"],
        summary="Eliminar catálogo (admin)",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Eliminado"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def delete(self, solicitud: Request, catalogo_id: int) -> Response:
        """Elimina logicamente un catalogo que no sea del sistema."""
        catalogo = obtener_catalogo_admin_por_id(catalogo_id)
        if catalogo is None:
            return _error_catalogo_no_encontrado()
        try:
            eliminar_catalogo_admin(catalogo)
        except CatalogoProtegidoError as error:
            return _respuesta_error(error.mensaje)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ItemsCatalogoAdminListCreateView(APIView):
    """Lista y crea items de un catalogo."""

    permission_classes = [PermisoGestionarCatalogos]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Catalogos"],
        summary="Listar items de catálogo (admin)",
        responses={
            status.HTTP_200_OK: ItemCatalogoAdminSerializer(many=True),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def get(self, solicitud: Request, catalogo_id: int) -> Response:
        """Retorna items paginados de un catalogo."""
        catalogo = obtener_catalogo_admin_por_id(catalogo_id)
        if catalogo is None:
            return _error_catalogo_no_encontrado()
        busqueda = solicitud.query_params.get("busqueda")
        items = listar_items_admin(catalogo, busqueda)
        return construir_respuesta_paginada(
            self,
            items,
            ItemCatalogoAdminSerializer,
            solicitud,
        )

    @extend_schema(
        tags=["Catalogos"],
        summary="Crear item de catálogo (admin)",
        request=ItemCatalogoAdminEntradaSerializer,
        responses={
            status.HTTP_201_CREATED: ItemCatalogoAdminSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def post(self, solicitud: Request, catalogo_id: int) -> Response:
        """Crea un item dentro de un catalogo."""
        catalogo = obtener_catalogo_admin_por_id(catalogo_id)
        if catalogo is None:
            return _error_catalogo_no_encontrado()
        entrada = ItemCatalogoAdminEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        try:
            item = crear_item_admin(catalogo, entrada.validated_data)
        except ItemCatalogoDuplicadoError as error:
            return _respuesta_error(error.mensaje)
        except ItemCatalogoNoEncontradoError as error:
            return _respuesta_no_encontrado(error.mensaje)
        return Response(ItemCatalogoAdminSerializer(item).data, status=status.HTTP_201_CREATED)


class ItemCatalogoAdminDetalleView(APIView):
    """Consulta, actualiza y elimina un item de catalogo."""

    permission_classes = [PermisoGestionarCatalogos]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Catalogos"],
        summary="Actualizar item de catálogo (admin)",
        request=ItemCatalogoAdminEntradaSerializer,
        responses={
            status.HTTP_200_OK: ItemCatalogoAdminSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def patch(self, solicitud: Request, item_id: int) -> Response:
        """Actualiza campos editables de un item."""
        item = obtener_item_admin_por_id(item_id)
        if item is None:
            return _respuesta_no_encontrado(MensajesCatalogoApi.ITEM_NO_ENCONTRADO)
        entrada = ItemCatalogoAdminEntradaSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        try:
            item = actualizar_item_admin(item, entrada.validated_data)
        except ItemCatalogoDuplicadoError as error:
            return _respuesta_error(error.mensaje)
        except ItemCatalogoNoEncontradoError as error:
            return _respuesta_no_encontrado(error.mensaje)
        return Response(ItemCatalogoAdminSerializer(item).data)

    @extend_schema(
        tags=["Catalogos"],
        summary="Eliminar item de catálogo (admin)",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Eliminado"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def delete(self, solicitud: Request, item_id: int) -> Response:
        """Elimina logicamente un item de catalogo."""
        item = obtener_item_admin_por_id(item_id)
        if item is None:
            return _respuesta_no_encontrado(MensajesCatalogoApi.ITEM_NO_ENCONTRADO)
        eliminar_item_admin(item)
        return Response(status=status.HTTP_204_NO_CONTENT)
