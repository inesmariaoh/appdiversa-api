"""
Permisos DRF para la consulta de registros de auditoria.
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from aplicaciones.auditoria.constantes import MensajesAuditoriaApi
from aplicaciones.usuarios.selectores import usuario_tiene_permiso_gestion_usuarios


class PermisoConsultarAuditoria(BasePermission):
    """Restringe la consulta de auditoria al rol administrador general."""

    message = MensajesAuditoriaApi.SIN_PERMISO

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Valida que el usuario tenga permiso administrativo de auditoria."""
        return usuario_tiene_permiso_gestion_usuarios(request.user)
