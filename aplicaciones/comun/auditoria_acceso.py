"""
Registro de auditoria para eventos de acceso a la API.
"""

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import registrar_auditoria


def registrar_acceso_denegado(
    entidad: str,
    entidad_id: str,
    descripcion: str,
) -> None:
    """Registra un intento de acceso denegado sin exponer credenciales."""
    registrar_auditoria(
        entidad=entidad,
        entidad_id=entidad_id,
        accion=AccionAuditoria.ACCESO_DENEGADO,
        descripcion=descripcion,
    )
