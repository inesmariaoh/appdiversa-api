"""
Permisos DRF basados en sesion anonima.
"""

from uuid import UUID

from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from aplicaciones.comun.auditoria_acceso import registrar_acceso_denegado
from aplicaciones.sesiones_anonimas.excepciones import (
    SesionFinalizadaAccesoError,
    SesionNoExisteError,
    TokenSesionInvalidoError,
)
from aplicaciones.sesiones_anonimas.models import SesionAnonima
from aplicaciones.sesiones_anonimas.selectores import obtener_sesion_por_uuid
from aplicaciones.sesiones_anonimas.seguridad import (
    extraer_credenciales_sesion,
    obtener_mensaje_error_acceso_sesion,
    validar_acceso_sesion_anonima,
)


class PermisoSesionAnonimaValida(BasePermission):
    """Valida uuid de sesion y token_cliente para operaciones de sesion anonima."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Evalua credenciales de sesion anonima en la solicitud."""
        uuid_url = view.kwargs.get("uuid_sesion")
        uuid_sesion_url = UUID(str(uuid_url)) if uuid_url else None
        credenciales = extraer_credenciales_sesion(request, uuid_sesion_url)
        requiere_modificacion = getattr(view, "requiere_sesion_modificable", True)

        try:
            validar_acceso_sesion_anonima(
                credenciales.uuid_sesion,
                credenciales.token_cliente,
                requiere_modificacion=requiere_modificacion,
            )
            return True
        except SesionNoExisteError as error:
            if getattr(view, "responder_404_sesion_inexistente", False):
                raise NotFound(detail=obtener_mensaje_error_acceso_sesion(error))
            self._mensaje = obtener_mensaje_error_acceso_sesion(error)
            entidad_id = (
                str(credenciales.uuid_sesion)
                if credenciales.uuid_sesion is not None
                else "desconocida"
            )
            registrar_acceso_denegado(
                entidad=SesionAnonima.__name__,
                entidad_id=entidad_id,
                descripcion=self._mensaje,
            )
            return False
        except (
            TokenSesionInvalidoError,
            SesionFinalizadaAccesoError,
        ) as error:
            self._mensaje = obtener_mensaje_error_acceso_sesion(error)
            entidad_id = (
                str(credenciales.uuid_sesion)
                if credenciales.uuid_sesion is not None
                else "desconocida"
            )
            registrar_acceso_denegado(
                entidad=SesionAnonima.__name__,
                entidad_id=entidad_id,
                descripcion=self._mensaje,
            )
            return False

    @property
    def message(self) -> str:
        """Retorna el mensaje funcional de denegacion."""
        return getattr(self, "_mensaje", "")


class PermisoSesionAnonimaOUsuarioVinculado(BasePermission):
    """Permite acceso con sesion anonima valida o usuario vinculado a la sesion."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Evalua credenciales anonimas o propiedad de la sesion por usuario autenticado."""
        permiso_sesion = PermisoSesionAnonimaValida()
        if permiso_sesion.has_permission(request, view):
            return True

        usuario = getattr(request, "user", None)
        uuid_url = view.kwargs.get("uuid_sesion")
        if (
            usuario is None
            or not usuario.is_authenticated
            or uuid_url is None
        ):
            self._mensaje = permiso_sesion.message
            return False

        sesion = obtener_sesion_por_uuid(UUID(str(uuid_url)))
        if sesion is None or sesion.usuario_id != usuario.pk:
            self._mensaje = permiso_sesion.message
            return False
        return True

    @property
    def message(self) -> str:
        """Retorna el mensaje funcional de denegacion."""
        return getattr(self, "_mensaje", "")
