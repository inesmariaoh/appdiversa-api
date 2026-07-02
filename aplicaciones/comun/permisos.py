"""
Permisos DRF transversales de la API.
"""

from django.conf import settings
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from aplicaciones.comun.auditoria_acceso import registrar_acceso_denegado
from aplicaciones.comun.constantes_seguridad import (
    HEADER_API_INTERNA,
    MensajesAccesoApi,
)
from aplicaciones.sesiones_anonimas.permisos import PermisoSesionAnonimaValida


class PermisoApiInternaTemporal(BasePermission):
    """
    Permite acceso solo con header X-API-INTERNA coincidente con API_INTERNA_TOKEN.
    Mecanismo temporal hasta integrar Keycloak.
    """

    message = MensajesAccesoApi.API_INTERNA_INVALIDA

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Valida el token interno configurado por variable de entorno."""
        token_configurado = getattr(settings, "API_INTERNA_TOKEN", "")
        if not token_configurado:
            self.message = MensajesAccesoApi.API_INTERNA_NO_CONFIGURADA
            registrar_acceso_denegado(
                entidad="ApiInterna",
                entidad_id="configuracion",
                descripcion="API interna sin token configurado.",
            )
            return False

        token_recibido = str(request.META.get(HEADER_API_INTERNA, "")).strip()
        if not token_recibido or token_recibido != token_configurado:
            registrar_acceso_denegado(
                entidad="ApiInterna",
                entidad_id="solicitud",
                descripcion="Token de API interna invalido o ausente.",
            )
            self.message = MensajesAccesoApi.API_INTERNA_INVALIDA
            return False

        return True


class PermisoSesionAnonimaOApiInterna(BasePermission):
    """Permite acceso con sesion anonima valida o token de API interna."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Evalua sesion anonima o API interna temporal."""
        permiso_interna = PermisoApiInternaTemporal()
        if permiso_interna.has_permission(request, view):
            return True

        permiso_sesion = PermisoSesionAnonimaValida()
        if permiso_sesion.has_permission(request, view):
            return True

        self._mensaje = permiso_sesion.message or permiso_interna.message
        return False

    @property
    def message(self) -> str:
        """Retorna el ultimo mensaje de denegacion registrado."""
        return getattr(self, "_mensaje", MensajesAccesoApi.ACCESO_DENEGADO)
