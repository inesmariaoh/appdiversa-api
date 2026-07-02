"""
Administracion de sesiones anonimas.
"""

from django.contrib import admin

from aplicaciones.auditoria.admin_mixins import ModeloAuditableAdminMixin
from aplicaciones.sesiones_anonimas.models import SesionAnonima


@admin.register(SesionAnonima)
class SesionAnonimaAdmin(ModeloAuditableAdminMixin, admin.ModelAdmin):
    """Administracion de sesiones anonimas."""

    list_display = (
        "uuid_sesion",
        "formulario",
        "version_formulario",
        "estado",
        "es_offline",
        "esta_eliminado",
        "fecha_inicio",
        "fecha_ultima_actividad",
    )
    list_filter = ("estado", "es_offline", "formulario", "esta_eliminado")
    search_fields = ("uuid_sesion", "token_cliente")
    readonly_fields = ("fecha_inicio",)
    raw_id_fields = ("formulario", "version_formulario")
    actions = ["eliminar_logicamente_seleccionados", "restaurar_seleccionados"]
