"""
Servicio de eliminacion (baja logica) de la cuenta del usuario autenticado.
"""

from django.contrib.auth import get_user_model, logout
from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction
from django.http import HttpRequest

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import registrar_auditoria
from aplicaciones.usuarios.excepciones import ContrasenaActualIncorrectaError

User = get_user_model()

_DESCRIPCION_ELIMINACION = "Baja logica de la cuenta solicitada por el usuario."


@transaction.atomic
def eliminar_cuenta_usuario(
    solicitud: HttpRequest,
    usuario: AbstractBaseUser,
    password: str,
) -> None:
    """Desactiva la cuenta del usuario tras validar la contrasena y cierra la sesion."""
    if not usuario.check_password(password):
        raise ContrasenaActualIncorrectaError()

    usuario.is_active = False
    usuario.save(update_fields=["is_active"])
    registrar_auditoria(
        entidad=User.__name__,
        entidad_id=str(usuario.pk),
        accion=AccionAuditoria.ELIMINAR_CUENTA,
        valor_anterior={"is_active": True},
        valor_nuevo={"is_active": False},
        descripcion=_DESCRIPCION_ELIMINACION,
    )
    logout(solicitud)
