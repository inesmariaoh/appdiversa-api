"""
Permisos DRF para la administracion de conflictos de sincronizacion.
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from aplicaciones.sincronizacion.constantes import MensajesConflictoApi
from aplicaciones.usuarios.selectores import usuario_tiene_permiso_gestion_usuarios


class PermisoAdministrarSincronizacion(BasePermission):
    """Restringe la gestion de conflictos al rol administrador general."""

    message = MensajesConflictoApi.SIN_PERMISO

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Valida que el usuario tenga permiso administrativo."""
        return usuario_tiene_permiso_gestion_usuarios(request.user)
