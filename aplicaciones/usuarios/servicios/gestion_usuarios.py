"""
Servicios de gestion administrativa de usuarios Django.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import crear_snapshot_modelo, registrar_auditoria
from aplicaciones.notificaciones.servicios_correo import enviar_correo_usuario_creado
from aplicaciones.usuarios.excepciones import GruposInvalidosError, UsuarioNoEncontradoError
from aplicaciones.usuarios.selectores import (
    listar_usuarios_admin,
    obtener_grupos_por_nombres,
    obtener_usuario_por_id,
)

User = get_user_model()

_CAMPOS_USUARIO_SEGUROS = (
    "username",
    "email",
    "first_name",
    "last_name",
    "is_staff",
    "is_active",
)


def _snapshot_usuario_seguro(usuario: AbstractBaseUser) -> dict:
    """Genera snapshot del usuario sin incluir contrasena."""
    return {campo: getattr(usuario, campo) for campo in _CAMPOS_USUARIO_SEGUROS}


def _registrar_auditoria_usuario(
    usuario: AbstractBaseUser,
    accion: str,
    valor_anterior: dict | None = None,
    valor_nuevo: dict | None = None,
    descripcion: str = "",
) -> None:
    """Registra auditoria de operaciones sobre usuarios."""
    registrar_auditoria(
        entidad=User.__name__,
        entidad_id=str(usuario.pk),
        accion=accion,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        descripcion=descripcion,
    )


@transaction.atomic
def crear_usuario_admin(
    datos: dict,
    contrasena: str,
) -> AbstractBaseUser:
    """Crea un usuario del sistema desde la API administrativa."""
    usuario = User.objects.create_user(
        username=datos["username"],
        email=datos.get("email", ""),
        password=contrasena,
        first_name=datos.get("first_name", ""),
        last_name=datos.get("last_name", ""),
    )
    if "is_staff" in datos:
        usuario.is_staff = datos["is_staff"]
        usuario.save(update_fields=["is_staff"])
    _registrar_auditoria_usuario(
        usuario,
        AccionAuditoria.CREAR,
        valor_nuevo=_snapshot_usuario_seguro(usuario),
        descripcion="Creacion de usuario desde administracion.",
    )
    enviar_correo_usuario_creado(usuario)
    return usuario


@transaction.atomic
def actualizar_usuario_admin(usuario_id: int, datos: dict) -> AbstractBaseUser:
    """Actualiza campos permitidos de un usuario existente."""
    usuario = obtener_usuario_por_id(usuario_id)
    if usuario is None:
        raise UsuarioNoEncontradoError()

    valor_anterior = _snapshot_usuario_seguro(usuario)
    campos_actualizados: list[str] = []
    for campo in _CAMPOS_USUARIO_SEGUROS:
        if campo in datos and campo != "username":
            setattr(usuario, campo, datos[campo])
            campos_actualizados.append(campo)

    if campos_actualizados:
        usuario.save(update_fields=campos_actualizados)
        _registrar_auditoria_usuario(
            usuario,
            AccionAuditoria.EDITAR,
            valor_anterior=valor_anterior,
            valor_nuevo=_snapshot_usuario_seguro(usuario),
            descripcion="Actualizacion de usuario desde administracion.",
        )
    return usuario


@transaction.atomic
def activar_usuario_admin(usuario_id: int) -> AbstractBaseUser:
    """Activa un usuario inactivo."""
    usuario = obtener_usuario_por_id(usuario_id)
    if usuario is None:
        raise UsuarioNoEncontradoError()

    valor_anterior = _snapshot_usuario_seguro(usuario)
    usuario.is_active = True
    usuario.save(update_fields=["is_active"])
    _registrar_auditoria_usuario(
        usuario,
        AccionAuditoria.EDITAR,
        valor_anterior=valor_anterior,
        valor_nuevo=_snapshot_usuario_seguro(usuario),
        descripcion="Activacion de usuario.",
    )
    return usuario


@transaction.atomic
def desactivar_usuario_admin(usuario_id: int) -> AbstractBaseUser:
    """Desactiva un usuario activo."""
    usuario = obtener_usuario_por_id(usuario_id)
    if usuario is None:
        raise UsuarioNoEncontradoError()

    valor_anterior = _snapshot_usuario_seguro(usuario)
    usuario.is_active = False
    usuario.save(update_fields=["is_active"])
    _registrar_auditoria_usuario(
        usuario,
        AccionAuditoria.EDITAR,
        valor_anterior=valor_anterior,
        valor_nuevo=_snapshot_usuario_seguro(usuario),
        descripcion="Desactivacion de usuario.",
    )
    return usuario


@transaction.atomic
def asignar_grupos_usuario_admin(
    usuario_id: int,
    nombres_grupos: list[str],
) -> AbstractBaseUser:
    """Reemplaza los grupos asignados a un usuario."""
    usuario = obtener_usuario_por_id(usuario_id)
    if usuario is None:
        raise UsuarioNoEncontradoError()

    grupos = list(obtener_grupos_por_nombres(nombres_grupos))
    if len(grupos) != len(set(nombres_grupos)):
        raise GruposInvalidosError()

    valor_anterior = {
        "grupos": list(usuario.groups.values_list("name", flat=True)),
    }
    usuario.groups.set(grupos)
    valor_nuevo = {
        "grupos": list(usuario.groups.values_list("name", flat=True)),
    }
    _registrar_auditoria_usuario(
        usuario,
        AccionAuditoria.EDITAR,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        descripcion="Asignacion de grupos al usuario.",
    )
    return usuario


def listar_usuarios() -> list:
    """Retorna el queryset de usuarios para listado administrativo."""
    return listar_usuarios_admin()
