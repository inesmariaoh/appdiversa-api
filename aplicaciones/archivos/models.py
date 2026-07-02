"""
Modelo del repositorio documental transversal.
"""

import uuid

from django.db import models

from aplicaciones.auditoria.models import AuditoriaModeloAbstracto
from aplicaciones.archivos.constantes import (
    EstadoArchivo,
    OrigenArchivo,
    TipoArchivo,
)


class ArchivoRepositorio(AuditoriaModeloAbstracto):
    """Entidad independiente de archivo gestionada por el repositorio documental."""

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    nombre_original = models.CharField(max_length=300)
    nombre_fisico = models.CharField(max_length=300)
    extension = models.CharField(max_length=20)
    mime_type = models.CharField(max_length=150)
    tamano_bytes = models.PositiveBigIntegerField()
    checksum_sha256 = models.CharField(max_length=64)
    tipo_archivo = models.CharField(max_length=30, choices=TipoArchivo.choices)
    ruta_relativa = models.CharField(max_length=500)
    url_publica = models.CharField(max_length=500, blank=True)
    es_publico = models.BooleanField(default=False)
    origen = models.CharField(max_length=30, choices=OrigenArchivo.choices)
    estado = models.CharField(
        max_length=20,
        choices=EstadoArchivo.choices,
        default=EstadoArchivo.ACTIVO,
    )
    descripcion = models.TextField(blank=True)
    metadatos = models.JSONField(null=True, blank=True)
    fecha_carga = models.DateTimeField(auto_now_add=True)
    usuario_keycloak = models.CharField(max_length=255, blank=True)
    uuid_sesion = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha_carga"]
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["tipo_archivo"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["origen"]),
            models.Index(fields=["checksum_sha256"]),
            models.Index(fields=["fecha_carga"]),
        ]
        verbose_name = "Archivo de repositorio"
        verbose_name_plural = "Archivos de repositorio"

    def __str__(self) -> str:
        return f"{self.nombre_original} ({self.uuid})"
