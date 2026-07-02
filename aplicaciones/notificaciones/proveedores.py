"""
Proveedores de envio de notificaciones.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from aplicaciones.contenidos.servicios_correo import obtener_email_remitente_notificaciones
from aplicaciones.notificaciones.constantes import RespuestaProveedorCorreo
from aplicaciones.notificaciones.models import Notificacion

_logger = logging.getLogger(__name__)

PROVEEDOR_DUMMY = RespuestaProveedorCorreo.PROVEEDOR_DUMMY
PROVEEDOR_SMTP = RespuestaProveedorCorreo.PROVEEDOR_SMTP


class ProveedorNotificacion(ABC):
    """Contrato de proveedor de envio de notificaciones."""

    @abstractmethod
    def enviar(self, notificacion: Notificacion) -> dict[str, Any]:
        """Ejecuta el envio de una notificacion y retorna respuesta del proveedor."""


class ProveedorDummy(ProveedorNotificacion):
    """Proveedor simulado que no envia notificaciones externas."""

    def enviar(self, notificacion: Notificacion) -> dict[str, Any]:
        """Simula el envio registrando metadatos sin contactar proveedores externos."""
        return {
            "proveedor": PROVEEDOR_DUMMY,
            "estado": RespuestaProveedorCorreo.ESTADO_REGISTRADO,
        }


def _obtener_contenido_texto(notificacion: Notificacion) -> str:
    """Retorna el cuerpo de texto plano de la notificacion."""
    if notificacion.contenido_texto_generado:
        return notificacion.contenido_texto_generado
    contenido = notificacion.contenido_generado or ""
    if contenido.strip().startswith("<"):
        return ""
    return contenido


def _obtener_contenido_html(notificacion: Notificacion) -> str:
    """Retorna el cuerpo HTML de la notificacion."""
    if notificacion.contenido_html_generado:
        return notificacion.contenido_html_generado
    contenido = notificacion.contenido_generado or ""
    if contenido.strip().startswith("<"):
        return contenido
    return ""


class ProveedorCorreoSMTP(ProveedorNotificacion):
    """Proveedor de correo usando EmailMultiAlternatives de Django."""

    def enviar(self, notificacion: Notificacion) -> dict[str, Any]:
        """Envia un correo electronico mediante el backend SMTP configurado."""
        remitente = obtener_email_remitente_notificaciones()
        texto_plano = _obtener_contenido_texto(notificacion)
        contenido_html = _obtener_contenido_html(notificacion)
        cuerpo = texto_plano or contenido_html

        mensaje = EmailMultiAlternatives(
            subject=notificacion.asunto_generado,
            body=cuerpo,
            from_email=remitente,
            to=[notificacion.destinatario],
        )
        if contenido_html:
            mensaje.attach_alternative(contenido_html, "text/html")
        if notificacion.reply_to:
            mensaje.reply_to = [notificacion.reply_to]

        mensaje.send(fail_silently=False)
        return {
            "proveedor": PROVEEDOR_SMTP,
            "estado": RespuestaProveedorCorreo.ESTADO_ENVIADO,
        }


def obtener_proveedor_notificacion() -> ProveedorNotificacion:
    """Retorna el proveedor de notificaciones configurado para el entorno."""
    proveedor_configurado = getattr(
        settings,
        "NOTIFICACIONES_PROVEEDOR",
        PROVEEDOR_DUMMY,
    )
    if proveedor_configurado == PROVEEDOR_SMTP:
        return ProveedorCorreoSMTP()
    return ProveedorDummy()
