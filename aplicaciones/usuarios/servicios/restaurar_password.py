"""
Servicios de restauracion de contrasena por correo electronico.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import registrar_auditoria
from aplicaciones.notificaciones.constantes import CodigoPlantillaCorreo
from aplicaciones.notificaciones.servicios import enviar_notificacion
from aplicaciones.notificaciones.servicios_correo import obtener_nombre_aplicativo
from aplicaciones.usuarios.excepciones import (
    ContrasenasNoCoincidenError,
    TokenRestaurarInvalidoError,
)
from aplicaciones.usuarios.selectores import obtener_usuario_por_email
from aplicaciones.usuarios.servicios.autenticacion import validar_contrasena_django

User = get_user_model()
_generador_token = PasswordResetTokenGenerator()
CODIGO_PLANTILLA_RESTAURAR = CodigoPlantillaCorreo.RESTAURAR_PASSWORD


def _construir_url_restaurar_password(usuario: AbstractBaseUser) -> str:
    """Construye la URL de restauracion de contrasena para el frontend."""
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = _generador_token.make_token(usuario)
    base = settings.FRONTEND_URL.rstrip("/")
    return f"{base}/auth/restaurar-password?uid={uid}&token={token}"


def _enviar_correo_restaurar_password(usuario: AbstractBaseUser) -> None:
    """Envia correo con enlace de restauracion de contrasena."""
    url_restaurar = _construir_url_restaurar_password(usuario)
    enviar_notificacion(
        codigo_plantilla=CODIGO_PLANTILLA_RESTAURAR,
        destinatario=usuario.email,
        variables={
            "nombre": usuario.first_name or usuario.username,
            "correo": usuario.email,
            "username": usuario.username,
            "url_restaurar_password": url_restaurar,
            "url_login": f"{settings.FRONTEND_URL.rstrip('/')}/auth/login",
            "nombre_aplicativo": obtener_nombre_aplicativo(),
        },
    )


def solicitar_restaurar_password(email: str) -> None:
    """Procesa solicitud de restauracion sin revelar existencia del correo."""
    usuario = obtener_usuario_por_email(email)
    if usuario is not None and usuario.is_active and usuario.email:
        _enviar_correo_restaurar_password(usuario)
        registrar_auditoria(
            entidad=User.__name__,
            entidad_id=str(usuario.pk),
            accion=AccionAuditoria.SOLICITAR_RESTAURAR_PASSWORD,
            valor_nuevo={"username": usuario.username},
            descripcion="Solicitud de restauracion de contrasena.",
        )


def restaurar_password(
    uid: str,
    token: str,
    password_nueva: str,
    password_confirmacion: str,
) -> None:
    """Restaura la contrasena usando uid y token de enlace."""
    if password_nueva != password_confirmacion:
        raise ContrasenasNoCoincidenError()

    try:
        usuario_id = force_str(urlsafe_base64_decode(uid))
        usuario = User.objects.get(pk=usuario_id)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError) as error:
        raise TokenRestaurarInvalidoError() from error

    if not _generador_token.check_token(usuario, token):
        raise TokenRestaurarInvalidoError()

    validar_contrasena_django(password_nueva, usuario)
    usuario.set_password(password_nueva)
    usuario.save(update_fields=["password"])
    registrar_auditoria(
        entidad=User.__name__,
        entidad_id=str(usuario.pk),
        accion=AccionAuditoria.PASSWORD_RESTAURADO,
        valor_nuevo={"username": usuario.username},
        descripcion="Restauracion de contrasena completada.",
    )
