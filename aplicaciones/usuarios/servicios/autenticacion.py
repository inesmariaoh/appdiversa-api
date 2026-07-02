"""
Servicios de autenticacion con usuarios Django.
"""

from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpRequest

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import registrar_auditoria
from aplicaciones.usuarios.constantes import TipoInicioSesion
from aplicaciones.usuarios.excepciones import (
    ContrasenaActualIncorrectaError,
    ContrasenaInvalidaError,
    ContrasenasNoCoincidenError,
    CredencialesInvalidasError,
    UsuarioInactivoError,
)
from aplicaciones.usuarios.selectores import obtener_usuario_por_identificador
from aplicaciones.usuarios.permisos_frontend import construir_permisos_frontend
from aplicaciones.usuarios.validadores_contrasena import validar_contrasena_usuario

User = get_user_model()


def _registrar_auditoria_auth(
    usuario: AbstractBaseUser | None,
    accion: str,
    descripcion: str,
) -> None:
    """Registra una accion de autenticacion en auditoria sin datos sensibles."""
    entidad_id = str(usuario.pk) if usuario is not None else "anonimo"
    registrar_auditoria(
        entidad=User.__name__,
        entidad_id=entidad_id,
        accion=accion,
        valor_nuevo={"username": getattr(usuario, "username", "")},
        descripcion=descripcion,
    )


def validar_contrasena_django(
    contrasena: str,
    usuario: AbstractBaseUser | None = None,
) -> None:
    """Valida una contrasena con los validadores configurados en Django."""
    try:
        validar_contrasena_usuario(contrasena, usuario)
    except DjangoValidationError as error:
        mensaje = "; ".join(error.messages)
        raise ContrasenaInvalidaError(mensaje) from error


def autenticar_usuario(
    solicitud: HttpRequest,
    usuario_identificador: str,
    password: str,
) -> AbstractBaseUser:
    """Autentica un usuario por nombre de usuario o correo y abre sesion."""
    usuario = obtener_usuario_por_identificador(usuario_identificador)
    if usuario is None or not usuario.check_password(password):
        raise CredencialesInvalidasError()

    if not usuario.is_active:
        raise UsuarioInactivoError()

    login(solicitud, usuario)
    _registrar_auditoria_auth(
        usuario,
        AccionAuditoria.INICIAR_SESION,
        "Inicio de sesión exitoso.",
    )
    return usuario


def cerrar_sesion_usuario(solicitud: HttpRequest) -> None:
    """Cierra la sesion autenticada del usuario actual."""
    usuario = solicitud.user if solicitud.user.is_authenticated else None
    logout(solicitud)
    _registrar_auditoria_auth(
        usuario,
        AccionAuditoria.FINALIZAR_SESION,
        "Cierre de sesión exitoso.",
    )


def cambiar_contrasena_usuario(
    usuario: AbstractBaseUser,
    password_actual: str,
    password_nueva: str,
    password_confirmacion: str,
) -> None:
    """Cambia la contrasena del usuario autenticado."""
    if password_nueva != password_confirmacion:
        raise ContrasenasNoCoincidenError()
    if not usuario.check_password(password_actual):
        raise ContrasenaActualIncorrectaError()

    validar_contrasena_django(password_nueva, usuario)
    usuario.set_password(password_nueva)
    usuario.save(update_fields=["password"])
    _registrar_auditoria_auth(
        usuario,
        AccionAuditoria.CAMBIAR_PASSWORD,
        "Actualización de contraseña del usuario.",
    )


def construir_datos_usuario_autenticado(usuario: AbstractBaseUser) -> dict:
    """Construye la respuesta del perfil autenticado para la API."""
    grupos = list(usuario.groups.values_list("name", flat=True))
    permisos = sorted(usuario.get_all_permissions())
    return {
        "id": usuario.pk,
        "username": usuario.username,
        "email": usuario.email,
        "first_name": usuario.first_name,
        "last_name": usuario.last_name,
        "is_staff": usuario.is_staff,
        "is_superuser": usuario.is_superuser,
        "grupos": grupos,
        "permisos": permisos,
    }


def construir_respuesta_perfil_autenticado(usuario: AbstractBaseUser) -> dict:
    """Construye respuesta compatible con el perfil autenticado del frontend."""
    datos = construir_datos_usuario_autenticado(usuario)
    nombre_completo = f"{usuario.first_name} {usuario.last_name}".strip()
    return {
        "usuario": {
            "id": datos["id"],
            "username": datos["username"],
            "email": datos["email"],
            "nombre_completo": nombre_completo or datos["username"],
            "esta_activo": usuario.is_active,
        },
        "grupos": datos["grupos"],
        "permisos": construir_permisos_frontend(usuario),
    }


def construir_datos_perfil_editable(usuario: AbstractBaseUser) -> dict:
    """Construye datos editables del perfil de usuario."""
    fecha_ultimo_inicio = usuario.last_login.isoformat() if usuario.last_login else None
    return {
        "id": usuario.pk,
        "username": usuario.username,
        "email": usuario.email,
        "first_name": usuario.first_name,
        "last_name": usuario.last_name,
        "fecha_ultimo_inicio_sesion": fecha_ultimo_inicio,
        "tipo_inicio_sesion": TipoInicioSesion.CORREO_ELECTRONICO,
        "tipo_inicio_sesion_etiqueta": TipoInicioSesion.ETIQUETA_CORREO_ELECTRONICO,
    }
