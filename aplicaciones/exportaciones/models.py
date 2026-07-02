"""
Modelo del motor transversal de exportaciones.
"""

import uuid

from django.db import models

from aplicaciones.auditoria.models import AuditoriaModeloAbstracto
from aplicaciones.exportaciones.constantes import (
    EstadoExportacion,
    FormatoExportacion,
    TipoExportacion,
)


class Exportacion(AuditoriaModeloAbstracto):
    """Registro de una exportacion generada por el motor transversal."""

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=30, choices=TipoExportacion.choices)
    estado = models.CharField(
        max_length=20,
        choices=EstadoExportacion.choices,
        default=EstadoExportacion.PENDIENTE,
    )
    usuario = models.CharField(max_length=255, blank=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    archivo = models.ForeignKey(
        "archivos.ArchivoRepositorio",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="exportaciones",
    )
    formato = models.CharField(max_length=10, choices=FormatoExportacion.choices)
    parametros = models.JSONField(null=True, blank=True, default=dict)
    registros_exportados = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["formato"]),
        ]
        verbose_name = "Exportacion"
        verbose_name_plural = "Exportaciones"

    def __str__(self) -> str:
        return f"{self.tipo} - {self.formato} ({self.estado})"
