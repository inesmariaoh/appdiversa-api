"""
Modelos del motor transversal de notificaciones.
"""

import uuid

from django.db import models

from aplicaciones.auditoria.models import AuditoriaModeloAbstracto
from aplicaciones.notificaciones.constantes import (
    EstadoNotificacion,
    TipoNotificacion,
)


class PlantillaNotificacion(AuditoriaModeloAbstracto):
    """Plantilla reutilizable para generacion de notificaciones."""

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TipoNotificacion.choices)
    asunto = models.CharField(max_length=300, blank=True)
    contenido_html = models.TextField(blank=True)
    contenido_texto = models.TextField(blank=True)
    usa_variables = models.BooleanField(default=True)
    variables_disponibles = models.JSONField(null=True, blank=True, default=list)
    esta_activa = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["codigo"]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["esta_activa"]),
        ]
        verbose_name = "Plantilla de notificación"
        verbose_name_plural = "Plantillas de notificación"

    def __str__(self) -> str:
        return f"{self.codigo} - {self.nombre}"


class Notificacion(AuditoriaModeloAbstracto):
    """Registro de una notificacion generada o programada."""

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    plantilla = models.ForeignKey(
        PlantillaNotificacion,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="notificaciones",
    )
    canal = models.CharField(max_length=20, choices=TipoNotificacion.choices)
    destinatario = models.CharField(max_length=500)
    estado = models.CharField(
        max_length=20,
        choices=EstadoNotificacion.choices,
        default=EstadoNotificacion.PENDIENTE,
    )
    fecha_programada = models.DateTimeField(null=True, blank=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    asunto_generado = models.CharField(max_length=300, blank=True)
    contenido_generado = models.TextField(blank=True)
    contenido_texto_generado = models.TextField(blank=True)
    contenido_html_generado = models.TextField(blank=True)
    reply_to = models.CharField(max_length=500, blank=True)
    variables_utilizadas = models.JSONField(null=True, blank=True, default=dict)
    respuesta_proveedor = models.JSONField(null=True, blank=True, default=dict)
    numero_intentos = models.PositiveIntegerField(default=0)
    error_envio = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["canal"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["destinatario"]),
        ]
        verbose_name = "Notificacion"
        verbose_name_plural = "Notificaciones"

    def __str__(self) -> str:
        return f"{self.canal} - {self.destinatario} ({self.estado})"
