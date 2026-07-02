"""
Administracion Django del motor de notificaciones.
"""

from django.contrib import admin

from aplicaciones.auditoria.admin_mixins import ModeloAuditableAdminMixin
from aplicaciones.notificaciones.models import Notificacion, PlantillaNotificacion


class ModeloAuditableAdmin(ModeloAuditableAdminMixin, admin.ModelAdmin):
    """Admin base con auditoria y soft delete."""

    actions = ["eliminar_logicamente_seleccionados", "restaurar_seleccionados"]


@admin.register(PlantillaNotificacion)
class PlantillaNotificacionAdmin(ModeloAuditableAdmin):
    """Administracion de plantillas de notificacion."""

    list_display = (
        "codigo",
        "nombre",
        "tipo",
        "esta_activa",
        "usa_variables",
    )
    list_filter = ("tipo", "esta_activa", "usa_variables")
    search_fields = ("codigo", "nombre", "asunto")
    ordering = ("codigo",)


@admin.register(Notificacion)
class NotificacionAdmin(ModeloAuditableAdmin):
    """Administracion de notificaciones registradas."""

    list_display = (
        "uuid",
        "canal",
        "destinatario",
        "estado",
        "fecha_envio",
        "numero_intentos",
    )
    list_filter = ("canal", "estado")
    search_fields = ("destinatario", "asunto_generado", "uuid")
    autocomplete_fields = ("plantilla",)
    ordering = ("-fecha_creacion",)
