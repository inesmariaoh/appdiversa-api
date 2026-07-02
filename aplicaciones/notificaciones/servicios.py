"""
Servicios del motor transversal de notificaciones.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from django.core.mail import BadHeaderError
from django.db import transaction
from django.utils import timezone
from smtplib import SMTPException

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import crear_snapshot_modelo, registrar_auditoria
from aplicaciones.notificaciones.constantes import EstadoNotificacion
from aplicaciones.notificaciones.excepciones import PlantillaNotificacionNoEncontradaError
from aplicaciones.notificaciones.models import Notificacion, PlantillaNotificacion
from aplicaciones.notificaciones.plantillas import renderizar_plantilla
from aplicaciones.notificaciones.proveedores import obtener_proveedor_notificacion
from aplicaciones.notificaciones.selectores import obtener_plantilla_por_codigo

_logger = logging.getLogger(__name__)


def _renderizar_contenidos_plantilla(
    plantilla: PlantillaNotificacion,
    variables: dict[str, Any],
) -> tuple[str, str, str]:
    """Renderiza asunto, HTML y texto de una plantilla con variables."""
    asunto = renderizar_plantilla(plantilla.asunto, variables)
    contenido_html = renderizar_plantilla(plantilla.contenido_html, variables)
    contenido_texto = renderizar_plantilla(plantilla.contenido_texto, variables)
    return asunto, contenido_html, contenido_texto


def generar_notificacion(
    codigo_plantilla: str,
    destinatario: str,
    variables: dict[str, Any] | None = None,
    fecha_programada: datetime | None = None,
    reply_to: str | None = None,
) -> Notificacion:
    """Genera el contenido de una notificacion desde una plantilla activa."""
    plantilla = obtener_plantilla_por_codigo(codigo_plantilla)
    if plantilla is None:
        raise PlantillaNotificacionNoEncontradaError()

    variables_utilizadas = variables or {}
    asunto, contenido_html, contenido_texto = _renderizar_contenidos_plantilla(
        plantilla,
        variables_utilizadas,
    )
    contenido_generado = contenido_html or contenido_texto

    return Notificacion(
        plantilla=plantilla,
        canal=plantilla.tipo,
        destinatario=destinatario,
        estado=EstadoNotificacion.PENDIENTE,
        fecha_programada=fecha_programada,
        asunto_generado=asunto,
        contenido_generado=contenido_generado,
        contenido_texto_generado=contenido_texto,
        contenido_html_generado=contenido_html,
        reply_to=reply_to or "",
        variables_utilizadas=variables_utilizadas,
    )


def registrar_notificacion(notificacion: Notificacion) -> Notificacion:
    """Persiste una notificacion generada en el repositorio transversal."""
    with transaction.atomic():
        notificacion.save()
        registrar_auditoria(
            entidad=Notificacion.__name__,
            entidad_id=str(notificacion.pk),
            accion=AccionAuditoria.CREAR,
            valor_nuevo=crear_snapshot_modelo(notificacion),
        )
    return notificacion


def marcar_enviada(
    notificacion: Notificacion,
    respuesta_proveedor: dict[str, Any] | None = None,
) -> Notificacion:
    """Marca una notificacion como enviada."""
    notificacion.estado = EstadoNotificacion.ENVIADA
    notificacion.fecha_envio = timezone.now()
    notificacion.numero_intentos += 1
    if respuesta_proveedor is not None:
        notificacion.respuesta_proveedor = respuesta_proveedor
    notificacion.error_envio = ""
    notificacion.save(
        update_fields=[
            "estado",
            "fecha_envio",
            "numero_intentos",
            "respuesta_proveedor",
            "error_envio",
            "fecha_modificacion",
        ],
    )
    return notificacion


def marcar_fallida(
    notificacion: Notificacion,
    error_envio: str,
    respuesta_proveedor: dict[str, Any] | None = None,
) -> Notificacion:
    """Marca una notificacion como fallida."""
    notificacion.estado = EstadoNotificacion.FALLIDA
    notificacion.numero_intentos += 1
    notificacion.error_envio = error_envio
    if respuesta_proveedor is not None:
        notificacion.respuesta_proveedor = respuesta_proveedor
    notificacion.save(
        update_fields=[
            "estado",
            "numero_intentos",
            "error_envio",
            "respuesta_proveedor",
            "fecha_modificacion",
        ],
    )
    registrar_auditoria(
        entidad=Notificacion.__name__,
        entidad_id=str(notificacion.pk),
        accion=AccionAuditoria.CORREO_FALLIDO,
        valor_nuevo={
            "destinatario": notificacion.destinatario,
            "plantilla": notificacion.plantilla.codigo if notificacion.plantilla else "",
        },
        descripcion="Fallo en el envio de notificacion por correo.",
    )
    return notificacion


def _registrar_auditoria_correo_enviado(notificacion: Notificacion) -> None:
    """Registra auditoria de envio exitoso de correo."""
    registrar_auditoria(
        entidad=Notificacion.__name__,
        entidad_id=str(notificacion.pk),
        accion=AccionAuditoria.CORREO_ENVIADO,
        valor_nuevo={
            "destinatario": notificacion.destinatario,
            "plantilla": notificacion.plantilla.codigo if notificacion.plantilla else "",
        },
        descripcion="Envio exitoso de notificacion por correo.",
    )


def enviar_notificacion(
    codigo_plantilla: str,
    destinatario: str,
    variables: dict[str, Any] | None = None,
    reply_to: str | None = None,
) -> Notificacion:
    """Genera, registra y envia una notificacion usando el proveedor configurado."""
    notificacion = generar_notificacion(
        codigo_plantilla=codigo_plantilla,
        destinatario=destinatario,
        variables=variables,
        reply_to=reply_to,
    )
    notificacion = registrar_notificacion(notificacion)
    proveedor = obtener_proveedor_notificacion()
    try:
        respuesta = proveedor.enviar(notificacion)
        marcar_enviada(notificacion, respuesta_proveedor=respuesta)
        _registrar_auditoria_correo_enviado(notificacion)
    except (SMTPException, BadHeaderError, OSError, ValueError) as error:
        _logger.exception(
            "Error al enviar notificacion %s a %s",
            codigo_plantilla,
            destinatario,
        )
        marcar_fallida(notificacion, error_envio=str(error))
    return notificacion


def probar_notificacion(
    codigo_plantilla: str,
    destinatario: str,
    variables: dict[str, Any] | None = None,
) -> Notificacion:
    """Genera y registra una notificacion de prueba sin envio externo."""
    notificacion = generar_notificacion(
        codigo_plantilla=codigo_plantilla,
        destinatario=destinatario,
        variables=variables,
    )
    notificacion = registrar_notificacion(notificacion)
    proveedor = obtener_proveedor_notificacion()
    respuesta = proveedor.enviar(notificacion)
    return marcar_enviada(notificacion, respuesta_proveedor=respuesta)


def obtener_notificacion(uuid_notificacion: UUID) -> Notificacion:
    """Retorna una notificacion por UUID o lanza error funcional."""
    from aplicaciones.notificaciones.excepciones import NotificacionNoEncontradaError
    from aplicaciones.notificaciones.selectores import obtener_notificacion_por_uuid

    notificacion = obtener_notificacion_por_uuid(uuid_notificacion)
    if notificacion is None:
        raise NotificacionNoEncontradaError()
    return notificacion
