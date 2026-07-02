"""
Vistas de la API publica de catalogos parametrizables.
"""

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter, OpenApiResponse
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.catalogos.api.v1.serializers import (
    CatalogoSerializer,
    FiltrosItemsCatalogoSerializer,
    ItemCatalogoSerializer,
)
from aplicaciones.catalogos.excepciones import (
    CatalogoNoEncontradoError,
    ItemCatalogoNoEncontradoError,
)
from aplicaciones.catalogos.servicios import (
    listar_catalogos_activos,
    listar_hijos_item_catalogo,
    listar_items_catalogo_publico,
)
from aplicaciones.internacionalizacion.api.serializers import FiltroIdiomaSerializer
from aplicaciones.internacionalizacion.servicios import (
    construir_mapa_traducciones,
    normalizar_codigo_idioma,
    resolver_uuid_entidad,
)

_DETALLE_ERROR_SERIALIZER = inline_serializer(
    name="DetalleErrorCatalogo",
    fields={"detalle": serializers.CharField()},
)

_PARAMETRO_IDIOMA = OpenApiParameter(
    name="idioma",
    type=str,
    required=False,
    description="Codigo ISO del idioma para traducciones de contenido.",
)

_PARAMETRO_INCLUIR_ACCESIBILIDAD = OpenApiParameter(
    name="incluir_accesibilidad",
    type=bool,
    required=False,
    description=(
        "Si es verdadero, incluye contenido accesible multimodal en la respuesta."
    ),
)


class ListarCatalogosView(APIView):
    """Lista catalogos activos disponibles para el frontend."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Catalogos"],
        summary="Listar catalogos activos",
        description=(
            "Retorna la lista de catalogos parametrizables activos "
            "para consumo del frontend."
        ),
        parameters=[_PARAMETRO_IDIOMA],
        responses={
            status.HTTP_200_OK: CatalogoSerializer(many=True),
        },
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna catalogos activos y no eliminados."""
        filtros = FiltroIdiomaSerializer(data=solicitud.query_params)
        filtros.is_valid(raise_exception=True)
        codigo_idioma = normalizar_codigo_idioma(
            filtros.validated_data.get("idioma"),
        )

        catalogos = listar_catalogos_activos()
        uuids = [
            resolver_uuid_entidad(catalogo, "Catalogo")
            for catalogo in catalogos
        ]
        mapa_traducciones = construir_mapa_traducciones(codigo_idioma, uuids)

        serializador = CatalogoSerializer(
            catalogos,
            many=True,
            context={"mapa_traducciones": mapa_traducciones},
        )
        return Response(serializador.data, status=status.HTTP_200_OK)


class ListarItemsCatalogoView(APIView):
    """Lista items de un catalogo con filtros opcionales."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Catalogos"],
        summary="Listar items de un catalogo",
        description=(
            "Retorna los items de un catalogo parametrizable. "
            "Permite filtrar por item padre para jerarquias como "
            "pais, departamento y municipio."
        ),
        parameters=[
            OpenApiParameter(
                name="codigo_padre",
                type=str,
                required=False,
                description="Codigo del item padre para filtrar hijos.",
            ),
            OpenApiParameter(
                name="solo_activos",
                type=bool,
                required=False,
                description="Si es verdadero, solo retorna items activos.",
            ),
            OpenApiParameter(
                name="busqueda",
                type=str,
                required=False,
                description="Filtra items por nombre o codigo.",
            ),
            OpenApiParameter(
                name="limite",
                type=int,
                required=False,
                description="Limita la cantidad de items retornados (maximo 1000).",
            ),
            _PARAMETRO_IDIOMA,
            _PARAMETRO_INCLUIR_ACCESIBILIDAD,
        ],
        responses={
            status.HTTP_200_OK: ItemCatalogoSerializer(many=True),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def get(self, solicitud: Request, codigo_catalogo: str) -> Response:
        """Retorna items del catalogo solicitado."""
        filtros = FiltrosItemsCatalogoSerializer(data=solicitud.query_params)
        filtros.is_valid(raise_exception=True)
        datos = filtros.validated_data
        codigo_idioma = normalizar_codigo_idioma(datos.get("idioma"))

        try:
            items = listar_items_catalogo_publico(
                codigo_catalogo=codigo_catalogo,
                codigo_padre=datos.get("codigo_padre") or None,
                solo_activos=datos.get("solo_activos", True),
                busqueda=datos.get("busqueda") or None,
                limite=datos.get("limite"),
            )
        except CatalogoNoEncontradoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        lista_items = list(items)
        uuids = [
            resolver_uuid_entidad(item, "ItemCatalogo")
            for item in lista_items
        ]
        mapa_traducciones = construir_mapa_traducciones(codigo_idioma, uuids)

        serializador = ItemCatalogoSerializer(
            lista_items,
            many=True,
            context={
                "mapa_traducciones": mapa_traducciones,
                "incluir_accesibilidad": datos.get("incluir_accesibilidad", False),
                "idioma": codigo_idioma,
                "request": solicitud,
            },
        )
        return Response(serializador.data, status=status.HTTP_200_OK)


class ListarHijosItemCatalogoView(APIView):
    """Lista hijos directos de un item de catalogo."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Catalogos"],
        summary="Listar hijos de un item de catalogo",
        description="Retorna los items hijos directos de un item dentro de su catalogo.",
        parameters=[
            OpenApiParameter(
                name="solo_activos",
                type=bool,
                required=False,
                description="Si es verdadero, solo retorna items activos.",
            ),
            _PARAMETRO_IDIOMA,
            _PARAMETRO_INCLUIR_ACCESIBILIDAD,
        ],
        responses={
            status.HTTP_200_OK: ItemCatalogoSerializer(many=True),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def get(
        self,
        solicitud: Request,
        codigo_catalogo: str,
        codigo_item: str,
    ) -> Response:
        """Retorna hijos del item solicitado."""
        filtros = FiltroIdiomaSerializer(data=solicitud.query_params)
        filtros.is_valid(raise_exception=True)
        codigo_idioma = normalizar_codigo_idioma(
            filtros.validated_data.get("idioma"),
        )
        solo_activos = solicitud.query_params.get("solo_activos", "true").lower() != "false"
        incluir_accesibilidad = (
            solicitud.query_params.get("incluir_accesibilidad", "").lower() == "true"
        )

        try:
            hijos = listar_hijos_item_catalogo(
                codigo_catalogo=codigo_catalogo,
                codigo_item=codigo_item,
                solo_activos=solo_activos,
            )
        except ItemCatalogoNoEncontradoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        lista_hijos = list(hijos)
        uuids = [
            resolver_uuid_entidad(item, "ItemCatalogo")
            for item in lista_hijos
        ]
        mapa_traducciones = construir_mapa_traducciones(codigo_idioma, uuids)

        serializador = ItemCatalogoSerializer(
            lista_hijos,
            many=True,
            context={
                "mapa_traducciones": mapa_traducciones,
                "incluir_accesibilidad": incluir_accesibilidad,
                "idioma": codigo_idioma,
                "request": solicitud,
            },
        )
        return Response(serializador.data, status=status.HTTP_200_OK)
