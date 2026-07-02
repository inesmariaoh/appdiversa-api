"""
Servicio de exportacion del historial de respuestas del usuario autenticado.
"""

from uuid import UUID

from django.contrib.auth.models import AbstractBaseUser

from aplicaciones.exportaciones.servicios import generar_contenido_respuestas
from aplicaciones.sesiones_anonimas.selectores import obtener_sesion_por_uuid

TITULO_EXPORTACION_HISTORIAL = "Mis respuestas"


class SesionNoPerteneceUsuarioError(Exception):
    """Indica que la sesion no existe o no pertenece al usuario autenticado."""

    def __init__(self) -> None:
        self.mensaje = "La sesión indicada no existe o no pertenece al usuario."
        super().__init__(self.mensaje)


def exportar_respuestas_sesion_usuario(
    usuario: AbstractBaseUser,
    uuid_sesion: UUID,
    formato: str,
) -> tuple[bytes, str, str]:
    """Genera el contenido de exportacion de una sesion propia del usuario."""
    sesion = obtener_sesion_por_uuid(uuid_sesion)
    if sesion is None or sesion.usuario_id != usuario.pk:
        raise SesionNoPerteneceUsuarioError()

    parametros = {
        "uuid_sesion": str(uuid_sesion),
        "titulo": TITULO_EXPORTACION_HISTORIAL,
    }
    return generar_contenido_respuestas(formato, parametros)
