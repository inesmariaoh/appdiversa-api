"""
Permisos DRF para la administracion de catalogos parametrizables.
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from aplicaciones.catalogos.constantes import MensajesCatalogoAdmin
from aplicaciones.usuarios.selectores import usuario_tiene_permiso_gestion_usuarios


class PermisoGestionarCatalogos(BasePermission):
    """Restringe la administracion de catalogos al rol administrador general."""

    message = MensajesCatalogoAdmin.SIN_PERMISO

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Valida que el usuario tenga permiso administrativo."""
        return usuario_tiene_permiso_gestion_usuarios(request.user)
