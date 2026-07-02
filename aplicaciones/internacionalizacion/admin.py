"""
Administracion Django de internacionalizacion.
"""

from django.contrib import admin

from aplicaciones.auditoria.admin_mixins import ModeloAuditableAdminMixin
from aplicaciones.internacionalizacion.models import Idioma, TraduccionContenido


class ModeloAuditableAdmin(ModeloAuditableAdminMixin, admin.ModelAdmin):
    """Admin base con auditoria y soft delete."""

    actions = ["eliminar_logicamente_seleccionados", "restaurar_seleccionados"]


@admin.register(Idioma)
class IdiomaAdmin(ModeloAuditableAdmin):
    """Administracion de idiomas soportados."""

    list_display = (
        "codigo_iso",
        "nombre",
        "nombre_nativo",
        "direccion_texto",
        "esta_activo",
        "es_predeterminado",
        "orden",
    )
    list_filter = ("esta_activo", "es_predeterminado", "direccion_texto")
    search_fields = ("codigo_iso", "nombre", "nombre_nativo")
    ordering = ("orden", "nombre")


@admin.register(TraduccionContenido)
class TraduccionContenidoAdmin(ModeloAuditableAdmin):
    """Administracion de traducciones de contenido."""

    list_display = (
        "idioma",
        "entidad",
        "entidad_uuid",
        "campo",
        "valor_traducido",
        "esta_activa",
    )
    list_filter = ("idioma", "entidad", "campo", "esta_activa")
    search_fields = (
        "entidad",
        "entidad_uuid",
        "campo",
        "valor_traducido",
        "lectura_facil",
        "texto_alternativo",
    )
    autocomplete_fields = (
        "idioma",
        "repositorio_audio",
        "repositorio_video",
        "repositorio_imagen",
        "repositorio_lengua_senas",
    )
    ordering = ("idioma", "entidad", "campo")
    fieldsets = (
        (
            "Informacion base",
            {
                "fields": (
                    "idioma",
                    "entidad",
                    "entidad_uuid",
                    "campo",
                    "esta_activa",
                ),
            },
        ),
        (
            "Traduccion textual",
            {
                "fields": ("valor_traducido",),
            },
        ),
        (
            "Contenido accesible",
            {
                "fields": (
                    "lectura_facil",
                    "texto_alternativo",
                    "transcripcion",
                    "metadatos",
                ),
            },
        ),
        (
            "Recursos multimedia",
            {
                "fields": (
                    "repositorio_audio",
                    "repositorio_video",
                    "repositorio_imagen",
                    "repositorio_lengua_senas",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "fields": (
                    "fecha_creacion",
                    "fecha_modificacion",
                    "fecha_eliminacion",
                    "creado_por",
                    "modificado_por",
                    "eliminado_por",
                    "esta_eliminado",
                ),
            },
        ),
    )
