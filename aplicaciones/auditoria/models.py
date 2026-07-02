"""
Modelos de auditoria transversal y registro de acciones.
"""

from django.conf import settings
from django.db import models

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.mixins import AuditoriaMixin, SoftDeleteManager


class AuditoriaModeloAbstracto(AuditoriaMixin, models.Model):
    """Campos y comportamiento base de auditoria para modelos funcionales."""

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    fecha_eliminacion = models.DateTimeField(null=True, blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    eliminado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    esta_eliminado = models.BooleanField(default=False)

    objects = SoftDeleteManager()
    todos = models.Manager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["esta_eliminado"]),
            models.Index(fields=["fecha_creacion"]),
        ]


class RegistroAuditoria(models.Model):
    """Registro central de acciones de auditoria del sistema."""

    entidad = models.CharField(max_length=150)
    entidad_id = models.CharField(max_length=100)
    accion = models.CharField(max_length=30, choices=AccionAuditoria.choices)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    identificador_keycloak = models.CharField(max_length=255, blank=True)
    uuid_sesion_anonima = models.CharField(max_length=100, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    valor_anterior = models.JSONField(null=True, blank=True)
    valor_nuevo = models.JSONField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    fecha_accion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_accion"]
        indexes = [
            models.Index(fields=["entidad", "entidad_id"]),
            models.Index(fields=["accion"]),
            models.Index(fields=["usuario"]),
            models.Index(fields=["identificador_keycloak"]),
            models.Index(fields=["uuid_sesion_anonima"]),
            models.Index(fields=["fecha_accion"]),
        ]
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Registros de auditoria"

    def __str__(self) -> str:
        return f"{self.entidad} ({self.entidad_id}) - {self.accion}"
