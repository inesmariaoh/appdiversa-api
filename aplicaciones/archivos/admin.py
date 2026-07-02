"""
Administracion Django del repositorio documental.
"""

from django.contrib import admin

from aplicaciones.auditoria.admin_mixins import ModeloAuditableAdminMixin
from aplicaciones.archivos.models import ArchivoRepositorio


class ModeloAuditableAdmin(ModeloAuditableAdminMixin, admin.ModelAdmin):
    """Admin base con auditoria y soft delete."""

    actions = ["eliminar_logicamente_seleccionados", "restaurar_seleccionados"]


@admin.register(ArchivoRepositorio)
class ArchivoRepositorioAdmin(ModeloAuditableAdmin):
    """Administracion de archivos del repositorio documental."""

    list_display = (
        "uuid",
        "nombre_original",
        "tipo_archivo",
        "tamano_bytes",
        "estado",
        "origen",
        "fecha_carga",
    )
    list_filter = ("tipo_archivo", "estado", "origen")
    search_fields = ("nombre_original", "checksum_sha256", "uuid")
    readonly_fields = ("uuid", "checksum_sha256", "fecha_carga", "ruta_relativa")
    ordering = ("-fecha_carga",)
