"""
Servicios del formulario de contacto publico.
"""

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import registrar_auditoria
from aplicaciones.contenidos.servicios_correo import obtener_email_soporte_configurado
from aplicaciones.notificaciones.constantes import CodigoPlantillaCorreo
from aplicaciones.notificaciones.servicios import enviar_notificacion
from aplicaciones.notificaciones.servicios_correo import obtener_nombre_aplicativo
from aplicaciones.usuarios.constantes import MensajesContacto

CODIGO_PLANTILLA_CONTACTO = CodigoPlantillaCorreo.CONTACTO_RECIBIDO


class ContactoSinEmailSoporteError(Exception):
    """Indica que no hay correo de soporte configurado."""

    def __init__(self) -> None:
        super().__init__(MensajesContacto.SIN_EMAIL_SOPORTE)
        self.mensaje = MensajesContacto.SIN_EMAIL_SOPORTE


def enviar_contacto(datos: dict) -> None:
    """Envia mensaje de contacto al correo de soporte configurado."""
    email_soporte = obtener_email_soporte_configurado()
    nombre_aplicativo = obtener_nombre_aplicativo()

    if not email_soporte:
        raise ContactoSinEmailSoporteError()

    variables = {
        "nombre": datos["nombre"],
        "correo": datos["correo"],
        "asunto": datos["asunto"],
        "mensaje": datos["mensaje"],
        "nombre_aplicativo": nombre_aplicativo,
    }
    enviar_notificacion(
        codigo_plantilla=CODIGO_PLANTILLA_CONTACTO,
        destinatario=email_soporte,
        variables=variables,
        reply_to=datos["correo"],
    )
    registrar_auditoria(
        entidad="Contacto",
        entidad_id=datos["correo"],
        accion=AccionAuditoria.CONTACTO_ENVIADO,
        valor_nuevo={
            "nombre": datos["nombre"],
            "asunto": datos["asunto"],
        },
        descripcion="Mensaje de contacto recibido desde formulario publico.",
    )
