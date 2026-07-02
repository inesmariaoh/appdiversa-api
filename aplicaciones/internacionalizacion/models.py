"""
Modelos de internacionalizacion para contenido parametrizable.
"""

from django.core.exceptions import ValidationError
from django.db import models

from aplicaciones.auditoria.models import AuditoriaModeloAbstracto
from aplicaciones.archivos.constantes import REFERENCIA_MODELO_ARCHIVO_REPOSITORIO
from aplicaciones.internacionalizacion.constantes import DireccionTexto


class MensajesValidacionIdioma:
    """Mensajes de validacion del modelo Idioma."""

    SOLO_UN_IDIOMA_PREDETERMINADO = (
        "Solo puede existir un idioma predeterminado activo."
    )


class Idioma(AuditoriaModeloAbstracto):
    """Idioma soportado por la plataforma."""

    codigo_iso = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    nombre_nativo = models.CharField(max_length=100)
    direccion_texto = models.CharField(
        max_length=3,
        choices=[
            (DireccionTexto.LTR, "LTR"),
            (DireccionTexto.RTL, "RTL"),
        ],
        default=DireccionTexto.LTR,
    )
    esta_activo = models.BooleanField(default=True)
    es_predeterminado = models.BooleanField(default=False)
    icono_bandera = models.CharField(max_length=100, blank=True)
    orden = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["orden", "nombre"]
        indexes = [
            models.Index(fields=["esta_activo"]),
            models.Index(fields=["es_predeterminado"]),
            models.Index(fields=["orden"]),
        ]
        verbose_name = "Idioma"
        verbose_name_plural = "Idiomas"

    def __str__(self) -> str:
        return f"{self.codigo_iso} - {self.nombre}"

    def clean(self) -> None:
        super().clean()
        if self.es_predeterminado:
            existe_otro = Idioma.objects.filter(
                es_predeterminado=True,
                esta_eliminado=False,
            ).exclude(pk=self.pk).exists()
            if existe_otro:
                raise ValidationError(
                    {"es_predeterminado": MensajesValidacionIdioma.SOLO_UN_IDIOMA_PREDETERMINADO},
                )


class TraduccionContenido(AuditoriaModeloAbstracto):
    """Traduccion de un campo de contenido parametrizable."""

    idioma = models.ForeignKey(
        Idioma,
        on_delete=models.CASCADE,
        related_name="traducciones",
    )
    entidad = models.CharField(max_length=100)
    entidad_uuid = models.UUIDField()
    campo = models.CharField(max_length=100)
    valor_traducido = models.TextField()
    lectura_facil = models.TextField(blank=True)
    texto_alternativo = models.TextField(blank=True)
    transcripcion = models.TextField(blank=True)
    repositorio_audio = models.ForeignKey(
        REFERENCIA_MODELO_ARCHIVO_REPOSITORIO,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="traducciones_audio",
    )
    repositorio_video = models.ForeignKey(
        REFERENCIA_MODELO_ARCHIVO_REPOSITORIO,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="traducciones_video",
    )
    repositorio_imagen = models.ForeignKey(
        REFERENCIA_MODELO_ARCHIVO_REPOSITORIO,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="traducciones_imagen",
    )
    repositorio_lengua_senas = models.ForeignKey(
        REFERENCIA_MODELO_ARCHIVO_REPOSITORIO,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="traducciones_lengua_senas",
    )
    metadatos = models.JSONField(null=True, blank=True)
    esta_activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["entidad", "campo"]
        constraints = [
            models.UniqueConstraint(
                fields=["idioma", "entidad", "entidad_uuid", "campo"],
                condition=models.Q(esta_eliminado=False),
                name="uq_traduccion_idioma_entidad_campo_activa",
            ),
        ]
        indexes = [
            models.Index(fields=["idioma"]),
            models.Index(fields=["entidad"]),
            models.Index(fields=["entidad_uuid"]),
            models.Index(fields=["campo"]),
        ]
        verbose_name = "Traducción de contenido"
        verbose_name_plural = "Traducciones de contenido"

    def __str__(self) -> str:
        return f"{self.idioma.codigo_iso} - {self.entidad} - {self.campo}"
