"""
Admin del motor de sincronizacion offline.
"""

from django.contrib import admin

from aplicaciones.sincronizacion.models import ConflictoSincronizacion, OperacionSincronizacion


@admin.register(OperacionSincronizacion)
class OperacionSincronizacionAdmin(admin.ModelAdmin):
    """Administracion de operaciones de sincronizacion."""

    list_display = (
        "uuid_local",
        "uuid_sesion",
        "dispositivo",
        "estado",
        "version_cliente",
        "fecha_cliente",
        "fecha_servidor",
        "numero_reintentos",
    )
    list_filter = ("estado", "dispositivo", "fecha_servidor")
    search_fields = ("uuid_local", "uuid_sesion", "dispositivo")
    readonly_fields = ("uuid", "fecha_servidor")
    ordering = ("-fecha_servidor",)


@admin.register(ConflictoSincronizacion)
class ConflictoSincronizacionAdmin(admin.ModelAdmin):
    """Administracion de conflictos de sincronizacion."""

    list_display = (
        "uuid_local",
        "tipo_conflicto",
        "resolucion",
        "respuesta",
        "fecha",
    )
    list_filter = ("tipo_conflicto", "resolucion", "fecha")
    search_fields = ("uuid_local",)
    readonly_fields = ("uuid", "fecha")
    ordering = ("-fecha",)
