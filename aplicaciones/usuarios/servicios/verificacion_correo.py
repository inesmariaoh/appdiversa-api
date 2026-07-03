"""
Servicios de verificacion de correo electronico de usuarios.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import registrar_auditoria
from aplicaciones.notificaciones.constantes import CodigoPlantillaCorreo
from aplicaciones.notificaciones.servicios import enviar_notificacion
from aplicaciones.notificaciones.servicios_correo import obtener_nombre_aplicativo
from aplicaciones.usuarios.excepciones import TokenVerificacionInvalidoError
from aplicaciones.usuarios.models import VerificacionCorreo
from aplicaciones.usuarios.selectores import obtener_usuario_por_email

User = get_user_model()
_generador_token = PasswordResetTokenGenerator()
CODIGO_PLANTILLA_VERIFICACION = CodigoPlantillaCorreo.VERIFICACION_CORREO


def obtener_o_crear_verificacion(usuario: AbstractBaseUser) -> VerificacionCorreo:
    """Obtiene o crea el registro de verificacion de correo del usuario."""
    verificacion, _ = VerificacionCorreo.objects.get_or_create(usuario=usuario)
    return verificacion


def _construir_url_verificacion(usuario: AbstractBaseUser) -> str:
    """Construye la URL de verificacion de correo para el frontend."""
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = _generador_token.make_token(usuario)
    base = settings.FRONTEND_URL.rstrip("/")
    return f"{base}/auth/verificar-correo?uid={uid}&token={token}"


def enviar_verificacion_correo(usuario: AbstractBaseUser) -> None:
    """Genera el token y envia el correo con el enlace de verificacion."""
    if not usuario.email:
        return
    obtener_o_crear_verificacion(usuario)
    url_verificar = _construir_url_verificacion(usuario)
    enviar_notificacion(
        codigo_plantilla=CODIGO_PLANTILLA_VERIFICACION,
        destinatario=usuario.email,
        variables={
            "nombre": usuario.first_name or usuario.username,
            "correo": usuario.email,
            "username": usuario.username,
            "url_verificar_correo": url_verificar,
            "url_login": f"{settings.FRONTEND_URL.rstrip('/')}/auth/login",
            "nombre_aplicativo": obtener_nombre_aplicativo(),
        },
    )


def _obtener_usuario_desde_uid(uid: str) -> AbstractBaseUser:
    """Decodifica el uid y retorna el usuario asociado."""
    try:
        usuario_id = force_str(urlsafe_base64_decode(uid))
        return User.objects.get(pk=usuario_id)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError) as error:
        raise TokenVerificacionInvalidoError() from error


def verificar_correo(uid: str, token: str) -> None:
    """Valida el token de verificacion y marca el correo como verificado."""
    usuario = _obtener_usuario_desde_uid(uid)
    if not _generador_token.check_token(usuario, token):
        raise TokenVerificacionInvalidoError()

    verificacion = obtener_o_crear_verificacion(usuario)
    if not verificacion.verificado:
        verificacion.verificado = True
        verificacion.fecha_verificacion = timezone.now()
        verificacion.save(update_fields=["verificado", "fecha_verificacion"])
        registrar_auditoria(
            entidad=User.__name__,
            entidad_id=str(usuario.pk),
            accion=AccionAuditoria.VERIFICAR_CORREO,
            valor_nuevo={"username": usuario.username},
            descripcion="Verificacion de correo completada.",
        )


def reenviar_verificacion_correo(email: str) -> None:
    """Reenvia el correo de verificacion sin revelar la existencia del correo."""
    usuario = obtener_usuario_por_email(email)
    if usuario is None or not usuario.is_active or not usuario.email:
        return
    verificacion = obtener_o_crear_verificacion(usuario)
    if verificacion.verificado:
        return
    enviar_verificacion_correo(usuario)
