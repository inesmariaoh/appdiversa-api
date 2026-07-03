"""
Servicios de registro de usuarios.
"""

import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, Group
from django.conf import settings
from django.db import transaction

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import registrar_auditoria
from aplicaciones.notificaciones.constantes import CodigoPlantillaCorreo
from aplicaciones.notificaciones.servicios import despachar_notificacion
from aplicaciones.notificaciones.servicios_correo import obtener_nombre_aplicativo
from aplicaciones.usuarios.constantes import GrupoSistema
from aplicaciones.usuarios.excepciones import (
    ContrasenasNoCoincidenError,
    EmailDuplicadoError,
    UsernameDuplicadoError,
)
from aplicaciones.usuarios.selectores import existe_email, existe_username
from aplicaciones.usuarios.servicios.autenticacion import validar_contrasena_django
from aplicaciones.usuarios.servicios.verificacion_correo import enviar_verificacion_correo

User = get_user_model()

CODIGO_PLANTILLA_CONFIRMACION = CodigoPlantillaCorreo.CONFIRMACION_REGISTRO
LONGITUD_MAXIMA_USERNAME = 150
USERNAME_POR_DEFECTO = "usuario"
_PATRON_CARACTER_INVALIDO_USERNAME = re.compile(r"[^a-zA-Z0-9._-]")


def _asignar_grupo_encuestado(usuario: AbstractBaseUser) -> None:
    """Asigna el grupo encuestado si existe en el sistema."""
    grupo = Group.objects.filter(name=GrupoSistema.ENCUESTADO).first()
    if grupo is not None:
        usuario.groups.add(grupo)


def _enviar_correo_bienvenida(usuario: AbstractBaseUser) -> None:
    """Programa el correo de bienvenida si el usuario tiene email."""
    if not usuario.email:
        return
    url_login = f"{settings.FRONTEND_URL.rstrip('/')}/auth/login"
    despachar_notificacion(
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


def _notificar_registro(usuario: AbstractBaseUser) -> None:
    """Programa los correos de registro sin bloquear ni interrumpir el alta."""
    _enviar_correo_bienvenida(usuario)
    enviar_verificacion_correo(usuario)


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
    _notificar_registro(usuario)
    return usuario


def _generar_username_unico(correo: str) -> str:
    """Deriva un nombre de usuario unico a partir del correo electronico."""
    parte_local = correo.split("@")[0]
    base = _PATRON_CARACTER_INVALIDO_USERNAME.sub("", parte_local).lower()
    base = base[:LONGITUD_MAXIMA_USERNAME] or USERNAME_POR_DEFECTO
    candidato = base
    sufijo = 1
    while existe_username(candidato):
        sufijo_texto = str(sufijo)
        recorte = base[: LONGITUD_MAXIMA_USERNAME - len(sufijo_texto)]
        candidato = f"{recorte}{sufijo_texto}"
        sufijo += 1
    return candidato


def registrar_usuario_por_correo(correo: str, contrasena: str) -> AbstractBaseUser:
    """Registra un usuario normal con rol encuestado a partir del correo."""
    email = correo.strip()
    if existe_email(email):
        raise EmailDuplicadoError()
    username = _generar_username_unico(email)
    return registrar_usuario(
        {
            "username": username,
            "email": email,
            "password": contrasena,
            "password_confirmacion": contrasena,
        },
    )
