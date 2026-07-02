"""
Servicios de vinculacion de sesiones anonimas con usuarios autenticados.
"""

from uuid import UUID

from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction
from django.utils import timezone

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import registrar_auditoria
from aplicaciones.sesiones_anonimas.excepciones import SesionYaVinculadaOtroUsuarioError
from aplicaciones.sesiones_anonimas.models import SesionAnonima
from aplicaciones.sesiones_anonimas.seguridad import validar_acceso_sesion_anonima


@transaction.atomic
def vincular_sesion_anonima_a_usuario(
    uuid_sesion: UUID,
    token_cliente: str,
    usuario: AbstractBaseUser,
) -> SesionAnonima:
    """Asocia una sesion anonima valida al usuario autenticado."""
    sesion = validar_acceso_sesion_anonima(
        uuid_sesion,
        token_cliente,
        requiere_modificacion=False,
    )
    if sesion.usuario_id is not None and sesion.usuario_id != usuario.pk:
        raise SesionYaVinculadaOtroUsuarioError()
    if sesion.usuario_id == usuario.pk:
        return sesion

    sesion.usuario = usuario
    sesion.fecha_ultima_actividad = timezone.now()
    sesion.save(update_fields=["usuario", "fecha_ultima_actividad"])
    registrar_auditoria(
        entidad=SesionAnonima.__name__,
        entidad_id=str(sesion.uuid_sesion),
        accion=AccionAuditoria.EDITAR,
        valor_anterior={"usuario_id": None},
        valor_nuevo={"usuario_id": usuario.pk},
        descripcion="Vinculacion de sesion anonima con usuario autenticado.",
    )
    return sesion
