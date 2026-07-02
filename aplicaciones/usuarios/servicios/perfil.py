"""
Servicios de perfil de usuario autenticado.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import registrar_auditoria
from aplicaciones.usuarios.excepciones import EmailDuplicadoError
from aplicaciones.usuarios.selectores import existe_email

User = get_user_model()

_CAMPOS_PERFIL_EDITABLES = ("first_name", "last_name", "email")


@transaction.atomic
def actualizar_perfil_usuario(
    usuario: AbstractBaseUser,
    datos: dict,
) -> AbstractBaseUser:
    """Actualiza campos editables del perfil del usuario autenticado."""
    valor_anterior = {
        campo: getattr(usuario, campo) for campo in _CAMPOS_PERFIL_EDITABLES
    }
    if "email" in datos:
        email_nuevo = datos["email"].strip()
        if existe_email(email_nuevo, excluir_id=usuario.pk):
            raise EmailDuplicadoError()
        usuario.email = email_nuevo
    if "first_name" in datos:
        usuario.first_name = datos["first_name"]
    if "last_name" in datos:
        usuario.last_name = datos["last_name"]

    campos_actualizados = [campo for campo in _CAMPOS_PERFIL_EDITABLES if campo in datos]
    if campos_actualizados:
        usuario.save(update_fields=campos_actualizados)
        registrar_auditoria(
            entidad=User.__name__,
            entidad_id=str(usuario.pk),
            accion=AccionAuditoria.EDITAR_PERFIL,
            valor_anterior=valor_anterior,
            valor_nuevo={
                campo: getattr(usuario, campo) for campo in _CAMPOS_PERFIL_EDITABLES
            },
            descripcion="Actualizacion de perfil del usuario autenticado.",
        )
    return usuario
