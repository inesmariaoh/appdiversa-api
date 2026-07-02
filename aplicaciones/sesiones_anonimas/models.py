"""
Modelos de sesiones anonimas.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from aplicaciones.auditoria.models import AuditoriaModeloAbstracto
from aplicaciones.formularios.models import Formulario, FormularioVersion


class EstadoSesionAnonima(models.TextChoices):
    """Estados posibles de una sesion anonima."""

    INICIADA = "iniciada", "Iniciada"
    EN_PROCESO = "en_proceso", "En proceso"
    FINALIZADA = "finalizada", "Finalizada"
    ABANDONADA = "abandonada", "Abandonada"
    SINCRONIZADA = "sincronizada", "Sincronizada"


class SesionAnonima(AuditoriaModeloAbstracto):
    """Sesion anonima asociada a un formulario publicado."""

    uuid_sesion = models.UUIDField(unique=True, default=uuid.uuid4)
    formulario = models.ForeignKey(
        Formulario,
        on_delete=models.CASCADE,
        related_name="sesiones_anonimas",
    )
    version_formulario = models.ForeignKey(
        FormularioVersion,
        on_delete=models.CASCADE,
        related_name="sesiones_anonimas",
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actividad = models.DateTimeField(default=timezone.now)
    direccion_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    idioma = models.CharField(max_length=20, blank=True)
    zona_horaria = models.CharField(max_length=80, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoSesionAnonima.choices,
        default=EstadoSesionAnonima.INICIADA,
    )
    token_cliente = models.CharField(max_length=255, blank=True)
    es_offline = models.BooleanField(default=False)
    fecha_sincronizacion = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sesiones_anonimas_vinculadas",
    )

    class Meta:
        ordering = ["-fecha_inicio"]
        indexes = [
            models.Index(fields=["uuid_sesion"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["formulario"]),
            models.Index(fields=["version_formulario"]),
            models.Index(fields=["usuario"], name="sesiones_an_usuario_idx"),
        ]
        verbose_name = "Sesión anónima"
        verbose_name_plural = "Sesiones anónimas"

    def __str__(self) -> str:
        return f"Sesión {self.uuid_sesion}"
