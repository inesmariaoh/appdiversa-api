"""
Vistas de la API publica de configuracion de interfaz.
"""

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.contenidos.api.v1.serializers import (
    ConfiguracionInterfazPublicaEsquemaSerializer,
    ConfiguracionInterfazPublicaSerializer,
)
from aplicaciones.contenidos.servicios import (
    construir_configuracion_por_defecto,
    obtener_configuracion_interfaz_publica,
)
from aplicaciones.contenidos.selectores import (
    obtener_configuracion_flujo_formulario_activa,
)
from aplicaciones.internacionalizacion.api.serializers import FiltroIncluirAccesibilidadSerializer
from aplicaciones.internacionalizacion.servicios import (
    construir_mapa_traducciones,
    normalizar_codigo_idioma,
    resolver_uuid_entidad,
)

_PARAMETRO_IDIOMA = OpenApiParameter(
    name="idioma",
    type=str,
    required=False,
    description="Código ISO del idioma para traducciones de contenido.",
)

_PARAMETRO_INCLUIR_ACCESIBILIDAD = OpenApiParameter(
    name="incluir_accesibilidad",
    type=bool,
    required=False,
    description=(
        "Si es verdadero, incluye contenido accesible multimodal en la respuesta."
    ),
)


class ConfiguracionInterfazView(APIView):
    """Consulta la configuracion visual activa del aplicativo."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Interfaz"],
        summary="Obtener configuración de interfaz",
        description=(
            "Retorna la parametrización visual activa del aplicativo "
            "para renderización dinámica en el frontend."
        ),
        parameters=[_PARAMETRO_IDIOMA, _PARAMETRO_INCLUIR_ACCESIBILIDAD],
        responses={
            status.HTTP_200_OK: ConfiguracionInterfazPublicaEsquemaSerializer,
        },
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna la configuracion de interfaz activa o valores por defecto."""
        filtros = FiltroIncluirAccesibilidadSerializer(data=solicitud.query_params)
        filtros.is_valid(raise_exception=True)
        datos_filtros = filtros.validated_data
        codigo_idioma = normalizar_codigo_idioma(datos_filtros.get("idioma"))

        configuracion = obtener_configuracion_interfaz_publica()
        if configuracion is None:
            return Response(
                construir_configuracion_por_defecto(),
                status=status.HTTP_200_OK,
            )

        uuid_entidad = resolver_uuid_entidad(configuracion, "ConfiguracionInterfaz")
        uuids_traduccion = [uuid_entidad]
        flujo_activo = obtener_configuracion_flujo_formulario_activa()
        if flujo_activo is not None:
            uuids_traduccion.append(flujo_activo.uuid)
        mapa_traducciones = construir_mapa_traducciones(
            codigo_idioma,
            uuids_traduccion,
        )

        serializador = ConfiguracionInterfazPublicaSerializer(
            configuracion,
            context={
                "request": solicitud,
                "mapa_traducciones": mapa_traducciones,
                "idioma": codigo_idioma,
                "incluir_accesibilidad": datos_filtros.get(
                    "incluir_accesibilidad",
                    False,
                ),
            },
        )
        return Response(serializador.data, status=status.HTTP_200_OK)
