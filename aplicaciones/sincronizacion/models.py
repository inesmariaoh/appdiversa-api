"""
Modelos del motor de sincronizacion offline.
"""

import uuid

from django.db import models

from aplicaciones.respuestas.models import Respuesta


class EstadoSincronizacion(models.TextChoices):
    """Estados de una operacion de sincronizacion."""

    PENDIENTE = "pendiente", "Pendiente"
    PROCESANDO = "procesando", "Procesando"
    SINCRONIZADA = "sincronizada", "Sincronizada"
    CONFLICTO = "conflicto", "Conflicto"
    ERROR = "error", "Error"
    CANCELADA = "cancelada", "Cancelada"


class TipoConflicto(models.TextChoices):
    """Tipos de conflicto detectados en sincronizacion."""

    VERSION = "version", "Version"
    DUPLICADO = "duplicado", "Duplicado"
    ELIMINADO = "eliminado", "Eliminado"
    MODIFICACION = "modificacion", "Modificacion"
    OTRO = "otro", "Otro"


class ResolucionConflicto(models.TextChoices):
    """Resolucion aplicada a un conflicto de sincronizacion."""

    CLIENTE = "cliente", "Cliente"
    SERVIDOR = "servidor", "Servidor"
    MANUAL = "manual", "Manual"


class OperacionSincronizacion(models.Model):
    """Registro de una operacion enviada por un dispositivo offline."""

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    uuid_local = models.UUIDField(db_index=True)
    uuid_sesion = models.UUIDField(db_index=True)
    dispositivo = models.CharField(max_length=150)
    version_cliente = models.PositiveIntegerField(default=1)
    estado = models.CharField(
        max_length=20,
        choices=EstadoSincronizacion.choices,
        default=EstadoSincronizacion.PENDIENTE,
        db_index=True,
    )
    fecha_cliente = models.DateTimeField()
    fecha_servidor = models.DateTimeField(auto_now_add=True)
    numero_reintentos = models.PositiveIntegerField(default=0)
    ultimo_error = models.TextField(blank=True)
    checksum = models.CharField(max_length=128, blank=True)
    origen = models.CharField(max_length=50, blank=True)
    payload = models.JSONField(default=dict)
    resultado = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha_servidor"]
        indexes = [
            models.Index(fields=["dispositivo"]),
            models.Index(fields=["fecha_servidor"]),
            models.Index(fields=["uuid_sesion", "uuid_local"]),
        ]
        verbose_name = "Operación de sincronización"
        verbose_name_plural = "Operaciones de sincronizacion"

    def __str__(self) -> str:
        return f"Sync {self.uuid_local} ({self.estado})"


class ConflictoSincronizacion(models.Model):
    """Conflicto detectado al sincronizar una respuesta offline."""

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    uuid_local = models.UUIDField(db_index=True)
    respuesta = models.ForeignKey(
        Respuesta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conflictos_sincronizacion",
    )
    tipo_conflicto = models.CharField(
        max_length=20,
        choices=TipoConflicto.choices,
        db_index=True,
    )
    valor_cliente = models.JSONField(null=True, blank=True)
    valor_servidor = models.JSONField(null=True, blank=True)
    resolucion = models.CharField(
        max_length=20,
        choices=ResolucionConflicto.choices,
        blank=True,
    )
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Conflicto de sincronización"
        verbose_name_plural = "Conflictos de sincronizacion"

    def __str__(self) -> str:
        return f"Conflicto {self.uuid_local} ({self.tipo_conflicto})"
