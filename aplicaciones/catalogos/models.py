"""
Modelos de catalogos parametrizables empresariales.

Los catalogos reutilizables (paises, departamentos, ocupaciones, estratos, etc.)
se administran desde Django Admin y se exponen por API.

El modelo CatalogoGeografico en formularios permanece como especializacion geografica
compatible; en una fase posterior puede migrarse o sincronizarse con esta app.

Las preguntas tipo select, autocomplete, radio o checkbox del motor de formularios
podran consumir estos catalogos mediante parametrizacion en una fase posterior.
"""

from django.db import models

from aplicaciones.auditoria.models import AuditoriaModeloAbstracto


class Catalogo(AuditoriaModeloAbstracto):
    """Catalogo parametrizable reutilizable en formularios y servicios."""

    codigo = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    tipo_catalogo = models.CharField(max_length=100)
    esta_activo = models.BooleanField(default=True)
    es_sistema = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["orden", "nombre"]
        indexes = [
            models.Index(fields=["esta_activo"]),
            models.Index(fields=["tipo_catalogo"]),
            models.Index(fields=["orden"]),
        ]
        verbose_name = "Catálogo"
        verbose_name_plural = "Catalogos"

    def __str__(self) -> str:
        return f"{self.codigo} - {self.nombre}"


class ItemCatalogo(AuditoriaModeloAbstracto):
    """Item individual dentro de un catalogo parametrizable."""

    catalogo = models.ForeignKey(
        Catalogo,
        on_delete=models.CASCADE,
        related_name="items",
    )
    codigo = models.CharField(max_length=100)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    valor = models.CharField(max_length=255, blank=True)
    item_padre = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="items_hijos",
        on_delete=models.SET_NULL,
    )
    codigo_externo = models.CharField(max_length=100, blank=True)
    metadatos = models.JSONField(null=True, blank=True)
    orden = models.PositiveIntegerField(default=1)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["catalogo", "orden", "nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["catalogo", "codigo"],
                condition=models.Q(esta_eliminado=False),
                name="uq_item_catalogo_catalogo_codigo_activo",
            ),
        ]
        indexes = [
            models.Index(fields=["catalogo"]),
            models.Index(fields=["codigo"]),
            models.Index(fields=["esta_activo"]),
            models.Index(fields=["item_padre"]),
            models.Index(fields=["codigo_externo"]),
            models.Index(fields=["orden"]),
        ]
        verbose_name = "Ítem de catálogo"
        verbose_name_plural = "Items de catalogo"

    def __str__(self) -> str:
        return f"{self.catalogo.codigo} - {self.codigo} - {self.nombre}"
