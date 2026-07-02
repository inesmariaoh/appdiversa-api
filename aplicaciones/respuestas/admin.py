"""
Administracion de respuestas.
"""

from django.contrib import admin

from aplicaciones.auditoria.admin_mixins import ModeloAuditableAdminMixin
from aplicaciones.respuestas.models import Respuesta


@admin.register(Respuesta)
class RespuestaAdmin(ModeloAuditableAdminMixin, admin.ModelAdmin):
    """Administracion de respuestas anonimas."""

    list_display = (
        "sesion",
        "pregunta",
        "origen_respuesta",
        "uuid_local",
        "version_cliente",
        "version_respuesta",
        "requiere_sincronizacion",
        "esta_eliminado",
        "fecha_respuesta_servidor",
    )
    list_filter = (
        "origen_respuesta",
        "requiere_sincronizacion",
        "esta_eliminado",
        "dispositivo_origen",
    )
    search_fields = (
        "sesion__uuid_sesion",
        "pregunta__codigo",
        "pregunta__texto",
        "uuid_local",
    )
    readonly_fields = ("fecha_respuesta_servidor",)
    raw_id_fields = ("sesion", "pregunta")
    actions = ["eliminar_logicamente_seleccionados", "restaurar_seleccionados"]
