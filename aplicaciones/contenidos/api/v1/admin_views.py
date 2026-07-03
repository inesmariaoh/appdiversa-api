"""
Vistas de la API administrativa de configuracion de interfaz.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.comun.autenticacion_sesion import AutenticacionSesionApi
from aplicaciones.contenidos.api.v1.serializers_admin import (
    AccesibilidadAdminEsquemaSerializer,
    AccesibilidadAdminSerializer,
)
from aplicaciones.contenidos.selectores import obtener_configuracion_interfaz_activa
from aplicaciones.contenidos.servicios import (
    actualizar_banderas_accesibilidad,
    construir_configuracion_accesibilidad_admin,
)
from aplicaciones.usuarios.permisos import PermisoGestionarConfiguracionInterfaz


class ConfiguracionAccesibilidadAdminView(APIView):
    """Consulta y actualiza las banderas de accesibilidad de la interfaz."""

    authentication_classes = [AutenticacionSesionApi]
    permission_classes = [PermisoGestionarConfiguracionInterfaz]

    @extend_schema(
        tags=["Admin Interfaz"],
        summary="Obtener banderas de accesibilidad",
        responses={status.HTTP_200_OK: AccesibilidadAdminEsquemaSerializer},
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna las banderas de accesibilidad activas o sus valores por defecto."""
        configuracion = obtener_configuracion_interfaz_activa()
        return Response(
            construir_configuracion_accesibilidad_admin(configuracion),
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Admin Interfaz"],
        summary="Actualizar banderas de accesibilidad",
        request=AccesibilidadAdminSerializer,
        responses={status.HTTP_200_OK: AccesibilidadAdminEsquemaSerializer},
    )
    def patch(self, solicitud: Request) -> Response:
        """Actualiza las banderas de accesibilidad de la configuracion activa."""
        entrada = AccesibilidadAdminSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        bloque = actualizar_banderas_accesibilidad(entrada.validated_data)
        return Response(bloque, status=status.HTTP_200_OK)
