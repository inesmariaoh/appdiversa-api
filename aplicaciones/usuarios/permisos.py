"""
Permisos DRF para autenticacion y roles del sistema.
"""

from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from aplicaciones.usuarios.constantes import MensajesAuth, MensajesUsuariosAdmin
from aplicaciones.usuarios.selectores import (
    usuario_tiene_permiso_consulta_formularios_admin,
    usuario_tiene_permiso_editar_formularios,
    usuario_tiene_permiso_exportar_respuestas,
    usuario_tiene_permiso_gestion_usuarios,
    usuario_tiene_permiso_publicar_formularios,
)


class PermisoUsuarioAutenticado(BasePermission):
    """Permite acceso solo a usuarios autenticados con sesion Django."""

    message = MensajesAuth.NO_AUTENTICADO

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Valida que la solicitud tenga un usuario autenticado."""
        return bool(
            request.user and request.user.is_authenticated,
        )


class PermisoUsuarioAutenticado401(BasePermission):
    """Retorna 401 cuando el usuario no esta autenticado."""

    message = MensajesAuth.NO_AUTENTICADO

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Valida autenticacion lanzando NotAuthenticated si no hay sesion."""
        if request.user and request.user.is_authenticated:
            return True
        raise NotAuthenticated(detail=self.message)


class PermisoGestionarUsuarios(BasePermission):
    """Permite acceso solo al rol administrador_general."""

    message = MensajesUsuariosAdmin.SIN_PERMISO

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Valida permiso de gestion de usuarios."""
        return usuario_tiene_permiso_gestion_usuarios(request.user)


class PermisoConsultarFormulariosAdmin(BasePermission):
    """Permite consulta administrativa de formularios a roles autorizados."""

    message = MensajesAuth.NO_AUTENTICADO

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Valida permiso de consulta administrativa."""
        return usuario_tiene_permiso_consulta_formularios_admin(request.user)


class PermisoEditarFormulariosAdmin(BasePermission):
    """Permite edicion de formularios en borrador a gestores y editores."""

    message = MensajesAuth.NO_AUTENTICADO

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Valida permiso de edicion de formularios."""
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return usuario_tiene_permiso_consulta_formularios_admin(request.user)
        return usuario_tiene_permiso_editar_formularios(request.user)


class PermisoPublicarFormulariosAdmin(BasePermission):
    """Permite publicacion, cierre y versionamiento a roles autorizados."""

    message = MensajesAuth.NO_AUTENTICADO

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Valida permiso de publicacion o versionamiento."""
        return usuario_tiene_permiso_publicar_formularios(request.user)


class PermisoExportarRespuestas(BasePermission):
    """Permite exportar respuestas a roles con permiso de exportacion."""

    message = MensajesAuth.NO_AUTENTICADO

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Valida permiso de exportacion de respuestas."""
        return usuario_tiene_permiso_exportar_respuestas(request.user)
