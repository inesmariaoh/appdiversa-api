"""
Servicios de envio de correos transversales del motor de formularios.
"""

from uuid import UUID

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import registrar_auditoria
from aplicaciones.contenidos.selectores import obtener_configuracion_interfaz_activa
from aplicaciones.notificaciones.constantes import CodigoPlantillaCorreo
from aplicaciones.notificaciones.servicios import enviar_notificacion
from aplicaciones.respuestas.servicios import resumen_respuestas_sesion
from aplicaciones.sesiones_anonimas.models import SesionAnonima


def obtener_nombre_aplicativo() -> str:
    """Retorna el nombre del aplicativo desde la configuracion activa de interfaz."""
    configuracion = obtener_configuracion_interfaz_activa()
    if configuracion is not None and configuracion.nombre_aplicativo:
        return configuracion.nombre_aplicativo
    return "AppDiversa"


def _formatear_resumen_texto(resumen: dict) -> str:
    """Convierte el resumen de respuestas a texto plano para plantillas de correo."""
    lineas: list[str] = []
    for item in resumen.get("respuestas", []):
        codigo = item.get("pregunta_codigo", "")
        texto = item.get("pregunta_texto", "")
        valor_legible = item.get("valor_legible")
        valor = valor_legible if valor_legible else item.get("valor", "")
        lineas.append(f"- {codigo}: {texto} = {valor}")
    return "\n".join(lineas)


def _variables_correo_base() -> dict[str, str]:
    """Retorna variables comunes para plantillas de correo."""
    return {
        "url_login": f"{settings.FRONTEND_URL.rstrip('/')}/auth/login",
        "nombre_aplicativo": obtener_nombre_aplicativo(),
    }


def enviar_correo_usuario_creado(usuario: AbstractBaseUser) -> None:
    """Envia correo de bienvenida cuando un administrador crea un usuario con email."""
    if not usuario.email:
        return
    variables = {
        **_variables_correo_base(),
        "nombre": usuario.first_name or usuario.username,
        "correo": usuario.email,
        "username": usuario.username,
    }
    enviar_notificacion(
        codigo_plantilla=CodigoPlantillaCorreo.USUARIO_CREADO,
        destinatario=usuario.email,
        variables=variables,
    )


def enviar_copia_respuestas_formulario(uuid_sesion: UUID, correo_destino: str) -> None:
    """Envia copia del resumen de respuestas al correo indicado."""
    try:
        validate_email(correo_destino)
    except DjangoValidationError as error:
        raise ValueError("Correo inválido") from error

    resumen = resumen_respuestas_sesion(uuid_sesion)

    formulario = resumen.get("formulario", {})
    variables = {
        **_variables_correo_base(),
        "correo": correo_destino,
        "formulario": formulario.get("nombre", ""),
        "uuid_sesion": str(uuid_sesion),
        "fecha": timezone.now().strftime("%Y-%m-%d %H:%M"),
        "resumen_respuestas": _formatear_resumen_texto(resumen),
    }
    enviar_notificacion(
        codigo_plantilla=CodigoPlantillaCorreo.COPIA_RESPUESTAS,
        destinatario=correo_destino,
        variables=variables,
    )
    registrar_auditoria(
        entidad=SesionAnonima.__name__,
        entidad_id=str(uuid_sesion),
        accion=AccionAuditoria.COPIA_RESPUESTAS_ENVIADA,
        valor_nuevo={
            "correo_destino": correo_destino,
            "total_respuestas": len(resumen.get("respuestas", [])),
        },
        descripcion="Envío de copia de respuestas por correo electrónico.",
    )


def enviar_notificacion_formulario_finalizado(
    uuid_sesion: UUID,
    correo_destino: str,
    resumen: dict,
) -> None:
    """Envia notificacion de formulario finalizado si hay correo destino."""
    if not correo_destino:
        return
    try:
        validate_email(correo_destino)
    except DjangoValidationError:
        return

    formulario = resumen.get("formulario", {})
    variables = {
        **_variables_correo_base(),
        "correo": correo_destino,
        "formulario": formulario.get("nombre", ""),
        "uuid_sesion": str(uuid_sesion),
        "fecha": timezone.now().strftime("%Y-%m-%d %H:%M"),
        "resumen_respuestas": _formatear_resumen_texto(resumen),
    }
    enviar_notificacion(
        codigo_plantilla=CodigoPlantillaCorreo.FORMULARIO_FINALIZADO,
        destinatario=correo_destino,
        variables=variables,
    )
