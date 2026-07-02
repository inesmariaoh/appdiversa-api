"""
Administracion de registros de auditoria.
"""

from django.contrib import admin

from aplicaciones.auditoria.admin_mixins import ModeloAuditableAdminMixin
from aplicaciones.auditoria.models import RegistroAuditoria


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    """Administracion de registros de auditoria."""

    list_display = (
        "entidad",
        "entidad_id",
        "accion",
        "usuario",
        "uuid_sesion_anonima",
        "fecha_accion",
    )
    list_filter = ("entidad", "accion", "usuario")
    search_fields = (
        "entidad",
        "entidad_id",
        "identificador_keycloak",
        "uuid_sesion_anonima",
        "descripcion",
    )
    readonly_fields = (
        "entidad",
        "entidad_id",
        "accion",
        "usuario",
        "identificador_keycloak",
        "uuid_sesion_anonima",
        "ip",
        "user_agent",
        "valor_anterior",
        "valor_nuevo",
        "descripcion",
        "fecha_accion",
    )
    ordering = ("-fecha_accion",)

    def has_add_permission(self, request) -> bool:
        """Impide crear registros manualmente desde el admin."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Impide modificar registros de auditoria."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Impide eliminar registros de auditoria."""
        return False


__all__ = ["ModeloAuditableAdminMixin", "RegistroAuditoriaAdmin"]
