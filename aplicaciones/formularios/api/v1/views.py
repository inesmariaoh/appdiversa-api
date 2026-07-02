"""
Vistas de la API publica de formularios.
"""

from uuid import UUID

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter, OpenApiResponse
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.formularios.api.v1.serializers import (
    FormularioDisponibleSerializer,
    FormularioEstructuraSerializer,
)
from aplicaciones.formularios.excepciones import (
    FormularioNoDisponibleError,
    VersionPublicadaNoDisponibleError,
)
from aplicaciones.formularios.servicios import (
    listar_formularios_disponibles,
    obtener_estructura_formulario_publica,
)
from aplicaciones.internacionalizacion.api.serializers import FiltroIdiomaSerializer
from aplicaciones.internacionalizacion.servicios import (
    construir_mapa_traducciones,
    normalizar_codigo_idioma,
    resolver_uuid_entidad,
)

_DETALLE_ERROR_SERIALIZER = inline_serializer(
    name="DetalleErrorFormulario",
    fields={"detalle": serializers.CharField()},
)

_PARAMETRO_IDIOMA = OpenApiParameter(
    name="idioma",
    type=str,
    required=False,
    description="Código ISO del idioma para traducciones de contenido.",
)


class FormulariosDisponiblesView(APIView):
    """Lista formularios publicados no vencidos, incluidos los de inicio futuro."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Formularios"],
        summary="Listar formularios disponibles",
        description=(
            "Retorna formularios publicados no vencidos para renderización dinámica. "
            "Incluye encuestas con fecha de inicio futura marcadas como Próximamente "
            "(puede_iniciar=false). No incluye borradores, cerrados, archivados, "
            "inactivos ni formularios vencidos."
        ),
        parameters=[_PARAMETRO_IDIOMA],
        responses={
            status.HTTP_200_OK: FormularioDisponibleSerializer(many=True),
        },
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna formularios publicados no vencidos con metadatos de disponibilidad."""
        filtros = FiltroIdiomaSerializer(data=solicitud.query_params)
        filtros.is_valid(raise_exception=True)
        codigo_idioma = normalizar_codigo_idioma(
            filtros.validated_data.get("idioma"),
        )

        formularios = listar_formularios_disponibles()
        uuids = [resolver_uuid_entidad(formulario, "Formulario") for formulario in formularios]
        mapa_traducciones = construir_mapa_traducciones(codigo_idioma, uuids)

        serializador = FormularioDisponibleSerializer(
            formularios,
            many=True,
            context={
                "mapa_traducciones": mapa_traducciones,
                "request": solicitud,
            },
        )
        return Response(serializador.data, status=status.HTTP_200_OK)


class FormularioEstructuraView(APIView):
    """Consulta la estructura completa de un formulario publicado."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Formularios"],
        summary="Obtener estructura de formulario",
        description=(
            "Retorna la estructura completa del formulario publicado iniciable, "
            "incluyendo textos, secciones, preguntas, opciones y reglas. "
            "Formularios con fecha de inicio futura no exponen estructura."
        ),
        parameters=[_PARAMETRO_IDIOMA],
        responses={
            status.HTTP_200_OK: FormularioEstructuraSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
                description="Formulario no disponible o sin versión publicada.",
            ),
        },
    )
    def get(self, solicitud: Request, uuid_formulario: UUID) -> Response:
        """Retorna la estructura completa del formulario solicitado."""
        filtros = FiltroIdiomaSerializer(data=solicitud.query_params)
        filtros.is_valid(raise_exception=True)
        codigo_idioma = normalizar_codigo_idioma(
            filtros.validated_data.get("idioma"),
        )

        try:
            estructura = obtener_estructura_formulario_publica(uuid_formulario)
        except FormularioNoDisponibleError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        except VersionPublicadaNoDisponibleError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializador = FormularioEstructuraSerializer(
            estructura,
            context={
                "idioma": codigo_idioma,
                "request": solicitud,
            },
        )
        return Response(serializador.data, status=status.HTTP_200_OK)
