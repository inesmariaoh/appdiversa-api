"""
Tareas asincronas del motor de notificaciones.
"""

from typing import Any

from celery import shared_task

from aplicaciones.notificaciones.servicios import enviar_notificacion


@shared_task(name="notificaciones.enviar_notificacion")
def enviar_notificacion_async(
    codigo_plantilla: str,
    destinatario: str,
    variables: dict[str, Any] | None = None,
    reply_to: str | None = None,
) -> int:
    """Envia una notificacion en segundo plano y retorna el id generado."""
    notificacion = enviar_notificacion(
        codigo_plantilla=codigo_plantilla,
        destinatario=destinatario,
        variables=variables,
        reply_to=reply_to,
    )
    return notificacion.pk
