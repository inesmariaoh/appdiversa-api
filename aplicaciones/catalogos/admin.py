"""
Administracion Django de catalogos parametrizables.
"""

from django.contrib import admin

from aplicaciones.auditoria.admin_mixins import ModeloAuditableAdminMixin
from aplicaciones.catalogos.models import Catalogo, ItemCatalogo


class ModeloAuditableAdmin(ModeloAuditableAdminMixin, admin.ModelAdmin):
    """Admin base con auditoria y soft delete."""

    actions = ["eliminar_logicamente_seleccionados", "restaurar_seleccionados"]


class ItemCatalogoInline(admin.TabularInline):
    """Inline para items dentro de un catalogo."""

    model = ItemCatalogo
    extra = 0
    fields = (
        "codigo",
        "nombre",
        "valor",
        "item_padre",
        "codigo_externo",
        "orden",
        "esta_activo",
    )
    ordering = ("orden",)
    autocomplete_fields = ("item_padre",)


@admin.register(Catalogo)
class CatalogoAdmin(ModeloAuditableAdmin):
    """Administracion de catalogos parametrizables."""

    list_display = (
        "codigo",
        "nombre",
        "tipo_catalogo",
        "esta_activo",
        "es_sistema",
        "orden",
    )
    list_filter = ("tipo_catalogo", "esta_activo", "es_sistema")
    search_fields = ("codigo", "nombre")
    ordering = ("orden", "nombre")
    inlines = [ItemCatalogoInline]


@admin.register(ItemCatalogo)
class ItemCatalogoAdmin(ModeloAuditableAdmin):
    """Administracion de items de catalogo."""

    list_display = (
        "catalogo",
        "codigo",
        "nombre",
        "item_padre",
        "codigo_externo",
        "esta_activo",
        "orden",
    )
    list_filter = ("catalogo", "esta_activo")
    search_fields = ("codigo", "nombre", "codigo_externo")
    autocomplete_fields = ("catalogo", "item_padre")
    ordering = ("catalogo", "orden", "nombre")
