"""
Permisos DRF del repositorio documental.
"""

from uuid import UUID

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from aplicaciones.archivos.excepciones import ArchivoNoEncontradoError
from aplicaciones.archivos.models import ArchivoRepositorio
from aplicaciones.archivos.servicios import obtener_archivo
from aplicaciones.comun.auditoria_acceso import registrar_acceso_denegado
from aplicaciones.comun.constantes_seguridad import MensajesAccesoApi
from aplicaciones.comun.permisos import PermisoApiInternaTemporal


class PermisoArchivoPublicoOApiInterna(BasePermission):
    """Permite consulta de archivos publicos o acceso con API interna."""

    message = MensajesAccesoApi.API_INTERNA_INVALIDA

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Evalua visibilidad del archivo solicitado."""
        uuid_archivo = view.kwargs.get("uuid_archivo")
        if uuid_archivo is None:
            return False

        try:
            archivo = obtener_archivo(UUID(str(uuid_archivo)))
        except ArchivoNoEncontradoError:
            return True

        if archivo.es_publico:
            return True

        permiso_interna = PermisoApiInternaTemporal()
        if permiso_interna.has_permission(request, view):
            return True

        registrar_acceso_denegado(
            entidad=ArchivoRepositorio.__name__,
            entidad_id=str(archivo.pk),
            descripcion="Acceso denegado a archivo privado.",
        )
        self.message = permiso_interna.message
        return False
