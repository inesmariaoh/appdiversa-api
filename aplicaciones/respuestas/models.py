"""
Modelos de respuestas de formularios.
"""

from django.db import models

from aplicaciones.auditoria.models import AuditoriaModeloAbstracto
from aplicaciones.formularios.models import Pregunta
from aplicaciones.sesiones_anonimas.models import SesionAnonima


class OrigenRespuesta(models.TextChoices):
    """Origen de captura de una respuesta."""

    WEB = "web", "Web"
    OFFLINE = "offline", "Offline"
    SINCRONIZACION = "sincronizacion", "Sincronizacion"


class Respuesta(AuditoriaModeloAbstracto):
    """Respuesta anonima a una pregunta dentro de una sesion."""

    sesion = models.ForeignKey(
        SesionAnonima,
        on_delete=models.CASCADE,
        related_name="respuestas",
    )
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name="respuestas",
    )
    valor_texto = models.TextField(blank=True)
    valor_numero = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        null=True,
        blank=True,
    )
    valor_booleano = models.BooleanField(null=True, blank=True)
    valor_fecha = models.DateField(null=True, blank=True)
    valor_hora = models.TimeField(null=True, blank=True)
    valor_fecha_hora = models.DateTimeField(null=True, blank=True)
    valor_json = models.JSONField(null=True, blank=True)
    archivo_nombre = models.CharField(max_length=300, blank=True)
    archivo_ruta = models.CharField(max_length=500, blank=True)
    latitud = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
    )
    longitud = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
    )
    precision_metros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    observacion = models.TextField(blank=True)
    origen_respuesta = models.CharField(
        max_length=20,
        choices=OrigenRespuesta.choices,
        default=OrigenRespuesta.WEB,
    )
    fecha_respuesta_cliente = models.DateTimeField(null=True, blank=True)
    fecha_respuesta_servidor = models.DateTimeField(auto_now=True)
    version_respuesta = models.PositiveIntegerField(default=1)
    requiere_sincronizacion = models.BooleanField(default=False)
    uuid_local = models.UUIDField(null=True, blank=True, unique=True)
    version_cliente = models.PositiveIntegerField(default=0)
    fecha_modificacion_cliente = models.DateTimeField(null=True, blank=True)
    dispositivo_origen = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ["sesion", "pregunta"]
        constraints = [
            models.UniqueConstraint(
                fields=["sesion", "pregunta"],
                condition=models.Q(esta_eliminado=False),
                name="uq_respuesta_sesion_pregunta_activa",
            ),
        ]
        indexes = [
            models.Index(fields=["sesion"]),
            models.Index(fields=["pregunta"]),
            models.Index(fields=["origen_respuesta"]),
            models.Index(fields=["requiere_sincronizacion"]),
            models.Index(fields=["fecha_respuesta_servidor"]),
            models.Index(fields=["uuid_local"]),
            models.Index(fields=["version_cliente"]),
        ]
        verbose_name = "Respuesta"
        verbose_name_plural = "Respuestas"

    def __str__(self) -> str:
        return f"Respuesta {self.sesion.uuid_sesion} - {self.pregunta.codigo}"
