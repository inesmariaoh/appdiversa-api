"""
Administracion Django del motor de exportaciones.
"""

from django.contrib import admin

from aplicaciones.auditoria.admin_mixins import ModeloAuditableAdminMixin
from aplicaciones.exportaciones.models import Exportacion


class ModeloAuditableAdmin(ModeloAuditableAdminMixin, admin.ModelAdmin):
    """Admin base con auditoria y soft delete."""

    actions = ["eliminar_logicamente_seleccionados", "restaurar_seleccionados"]


@admin.register(Exportacion)
class ExportacionAdmin(ModeloAuditableAdmin):
    """Administracion de exportaciones generadas."""

    list_display = (
        "uuid",
        "tipo",
        "formato",
        "estado",
        "registros_exportados",
        "fecha_inicio",
        "fecha_fin",
    )
    list_filter = ("tipo", "formato", "estado")
    search_fields = ("uuid", "usuario")
    autocomplete_fields = ("archivo",)
    ordering = ("-fecha_creacion",)
