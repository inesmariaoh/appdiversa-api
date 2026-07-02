"""
Servicios de registro de usuarios.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, Group
from django.conf import settings
from django.db import transaction

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import registrar_auditoria
from aplicaciones.notificaciones.constantes import CodigoPlantillaCorreo
from aplicaciones.notificaciones.servicios import enviar_notificacion
from aplicaciones.notificaciones.servicios_correo import obtener_nombre_aplicativo
from aplicaciones.usuarios.constantes import GrupoSistema
from aplicaciones.usuarios.excepciones import (
    ContrasenasNoCoincidenError,
    EmailDuplicadoError,
    UsernameDuplicadoError,
)
from aplicaciones.usuarios.selectores import existe_email, existe_username
from aplicaciones.usuarios.servicios.autenticacion import validar_contrasena_django

User = get_user_model()

CODIGO_PLANTILLA_CONFIRMACION = CodigoPlantillaCorreo.CONFIRMACION_REGISTRO


def _asignar_grupo_encuestado(usuario: AbstractBaseUser) -> None:
    """Asigna el grupo encuestado si existe en el sistema."""
    grupo = Group.objects.filter(name=GrupoSistema.ENCUESTADO).first()
    if grupo is not None:
        usuario.groups.add(grupo)


def _enviar_correo_bienvenida(usuario: AbstractBaseUser) -> None:
    """Envia correo de confirmacion o bienvenida si el usuario tiene email."""
    if not usuario.email:
        return
    url_login = f"{settings.FRONTEND_URL.rstrip('/')}/auth/login"
    enviar_notificacion(
        codigo_plantilla=CODIGO_PLANTILLA_CONFIRMACION,
        destinatario=usuario.email,
        variables={
            "nombre": usuario.first_name or usuario.username,
            "correo": usuario.email,
            "username": usuario.username,
            "url_login": url_login,
            "nombre_aplicativo": obtener_nombre_aplicativo(),
        },
    )


@transaction.atomic
def registrar_usuario(datos: dict) -> AbstractBaseUser:
    """Registra un nuevo usuario activo en el sistema."""
    username = datos["username"].strip()
    email = datos.get("email", "").strip()
    password = datos["password"]
    password_confirmacion = datos["password_confirmacion"]

    if password != password_confirmacion:
        raise ContrasenasNoCoincidenError()
    if existe_username(username):
        raise UsernameDuplicadoError()
    if email and existe_email(email):
        raise EmailDuplicadoError()

    usuario = User(
        username=username,
        email=email,
        first_name=datos.get("first_name", ""),
        last_name=datos.get("last_name", ""),
        is_active=True,
    )
    validar_contrasena_django(password, usuario)
    usuario.set_password(password)
    usuario.save()
    _asignar_grupo_encuestado(usuario)
    registrar_auditoria(
        entidad=User.__name__,
        entidad_id=str(usuario.pk),
        accion=AccionAuditoria.REGISTRAR_USUARIO,
        valor_nuevo={"username": usuario.username, "email": usuario.email},
        descripcion="Registro de usuario desde la API publica.",
    )
    _enviar_correo_bienvenida(usuario)
    return usuario
