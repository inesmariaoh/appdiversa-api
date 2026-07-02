"""
Administracion de contenidos y parametrizacion de interfaz.
"""

from django.contrib import admin

from aplicaciones.auditoria.admin_mixins import ModeloAuditableAdminMixin
from aplicaciones.contenidos.admin_utilidades import (
    ALTURA_VISTA_PREVIA_LISTA,
    construir_vista_previa_logo,
)
from aplicaciones.contenidos.models import (
    ConfiguracionFlujoFormulario,
    ConfiguracionInterfaz,
    LogoInterfaz,
)
from aplicaciones.contenidos.servicios import activar_configuracion_interfaz
from aplicaciones.contenidos.servicios_flujo_formulario import (
    activar_configuracion_flujo_formulario,
)


class ModeloAuditableAdmin(ModeloAuditableAdminMixin, admin.ModelAdmin):
    """Admin base con auditoria y soft delete."""

    actions = ["eliminar_logicamente_seleccionados", "restaurar_seleccionados"]


class LogoInterfazInline(admin.TabularInline):
    """Inline para administrar logos dentro de la configuracion de interfaz."""

    model = LogoInterfaz
    extra = 0
    fields = (
        "vista_previa_mini",
        "codigo",
        "nombre",
        "texto_alternativo",
        "imagen",
        "archivo_repositorio",
        "orden",
        "esta_activo",
    )
    readonly_fields = ("vista_previa_mini",)
    ordering = ("orden", "codigo")
    autocomplete_fields = ("archivo_repositorio",)

    @admin.display(description="Vista previa")
    def vista_previa_mini(self, obj: LogoInterfaz) -> str:
        """Muestra una miniatura del logo en la tabla inline."""
        return construir_vista_previa_logo(
            obj,
            altura_maxima=ALTURA_VISTA_PREVIA_LISTA,
        )


@admin.register(LogoInterfaz)
class LogoInterfazAdmin(ModeloAuditableAdmin):
    """Administracion dedicada de logos e imagenes de interfaz."""

    list_display = (
        "vista_previa_lista",
        "codigo",
        "nombre",
        "configuracion_interfaz",
        "texto_alternativo",
        "orden",
        "esta_activo",
        "esta_eliminado",
        "fecha_modificacion",
    )
    list_filter = (
        "configuracion_interfaz",
        "esta_activo",
        "esta_eliminado",
    )
    search_fields = (
        "codigo",
        "nombre",
        "texto_alternativo",
        "configuracion_interfaz__nombre_aplicativo",
    )
    ordering = ("configuracion_interfaz", "orden", "codigo")
    autocomplete_fields = ("configuracion_interfaz", "archivo_repositorio")
    readonly_fields = ("vista_previa_detalle",)
    fieldsets = (
        (
            "Identificacion",
            {
                "fields": (
                    "configuracion_interfaz",
                    "codigo",
                    "nombre",
                    "orden",
                    "esta_activo",
                ),
            },
        ),
        (
            "Imagen y accesibilidad",
            {
                "fields": (
                    "vista_previa_detalle",
                    "imagen",
                    "archivo_repositorio",
                    "texto_alternativo",
                ),
            },
        ),
    )

    @admin.display(description="Vista previa")
    def vista_previa_lista(self, obj: LogoInterfaz) -> str:
        """Muestra la miniatura del logo en el listado del admin."""
        return construir_vista_previa_logo(
            obj,
            altura_maxima=ALTURA_VISTA_PREVIA_LISTA,
        )

    @admin.display(description="Vista previa")
    def vista_previa_detalle(self, obj: LogoInterfaz) -> str:
        """Muestra la imagen ampliada en el formulario de edicion."""
        return construir_vista_previa_logo(obj)


@admin.register(ConfiguracionInterfaz)
class ConfiguracionInterfazAdmin(ModeloAuditableAdmin):
    """Administracion de la configuracion visual del aplicativo."""

    list_display = (
        "nombre_aplicativo",
        "nombre_corto",
        "esta_activa",
        "esta_eliminado",
        "fecha_modificacion",
    )
    list_filter = ("esta_activa", "esta_eliminado", "accion_lengua_senas_habilitada")
    search_fields = (
        "nombre_aplicativo",
        "nombre_corto",
        "email_soporte",
        "email_remitente_notificaciones",
    )
    inlines = [LogoInterfazInline]
    fieldsets = (
        (
            "Identidad",
            {
                "fields": (
                    "nombre_aplicativo",
                    "nombre_corto",
                    "descripcion_aplicativo",
                    "texto_pie_pagina",
                    "esta_activa",
                ),
            },
        ),
        (
            "Correos",
            {
                "fields": (
                    "email_soporte",
                    "email_remitente_notificaciones",
                ),
            },
        ),
        (
            "Home y encuestas",
            {
                "fields": (
                    "texto_titulo_seccion_encuestas",
                    "texto_descripcion_seccion_encuestas",
                ),
            },
        ),
        (
            "Flujos y textos legales",
            {
                "fields": (
                    "texto_terminos_condiciones",
                    "texto_autorizacion_datos",
                    "texto_verificacion_exitosa_titulo",
                    "texto_verificacion_exitosa_cuerpo",
                    "texto_confirmacion_envio_titulo",
                    "texto_confirmacion_envio_subtitulo",
                ),
            },
        ),
        (
            "SEO",
            {
                "fields": (
                    "meta_titulo_seo",
                    "meta_descripcion_seo",
                ),
            },
        ),
        (
            "Accesibilidad",
            {
                "fields": (
                    "accion_lengua_senas_habilitada",
                    "url_lengua_senas",
                    "texto_lengua_senas",
                ),
            },
        ),
        (
            "Colores",
            {
                "fields": (
                    "color_primario",
                    "color_secundario",
                    "color_acento",
                ),
            },
        ),
        (
            "Recursos visuales legacy",
            {
                "classes": ("collapse",),
                "description": (
                    "Campos heredados. Se recomienda administrar logos "
                    "desde la seccion Logos de interfaz o el inline inferior."
                ),
                "fields": (
                    "logo_principal",
                    "logo_secundario",
                    "logo_institucional",
                    "favicon",
                    "logo_principal_repositorio",
                    "logo_secundario_repositorio",
                    "logo_institucional_repositorio",
                    "favicon_repositorio",
                ),
            },
        ),
    )

    def save_model(
        self,
        request,
        obj: ConfiguracionInterfaz,
        form,
        change: bool,
    ) -> None:
        """Persiste la configuracion aplicando auditoria y regla de una sola activa."""
        super().save_model(request, obj, form, change)
        if obj.esta_activa:
            activar_configuracion_interfaz(obj)


@admin.register(ConfiguracionFlujoFormulario)
class ConfiguracionFlujoFormularioAdmin(ModeloAuditableAdmin):
    """Administracion de textos de modales y terminos del flujo de formularios."""

    list_display = (
        "uuid",
        "configuracion_interfaz",
        "esta_activa",
        "esta_eliminado",
        "fecha_modificacion",
    )
    list_filter = ("esta_activa", "esta_eliminado")
    search_fields = ("uuid", "modal_salir_titulo", "terminos_titulo")
    autocomplete_fields = ("configuracion_interfaz",)
    readonly_fields = ("uuid",)
    fieldsets = (
        (
            "General",
            {
                "fields": (
                    "uuid",
                    "configuracion_interfaz",
                    "esta_activa",
                ),
            },
        ),
        (
            "Modal salir sin guardar",
            {
                "fields": (
                    "modal_salir_titulo",
                    "modal_salir_p1",
                    "modal_salir_p2",
                    "modal_salir_btn_volver",
                    "modal_salir_btn_salir",
                    "modal_salir_link_sesion",
                ),
            },
        ),
        (
            "Modal iniciar sesión o registro",
            {
                "fields": (
                    "modal_sesion_titulo",
                    "modal_sesion_parrafo",
                    "modal_sesion_btn_login",
                    "modal_sesion_btn_registro",
                    "modal_sesion_link_cancelar",
                ),
            },
        ),
        (
            "Modal encuesta guardada",
            {
                "fields": (
                    "modal_guardado_titulo",
                    "modal_guardado_parrafo",
                    "modal_guardado_btn_seguir",
                    "modal_guardado_btn_otras",
                ),
            },
        ),
        (
            "Términos y condiciones",
            {
                "description": (
                    "Si completa contenido, el frontend lo usa como texto completo. "
                    "Si no, utiliza los párrafos p1, p2 y p3."
                ),
                "fields": (
                    "terminos_titulo",
                    "terminos_contenido",
                    "terminos_p1",
                    "terminos_p2",
                    "terminos_p3",
                    "terminos_url_ley",
                    "terminos_enlace_ley",
                    "terminos_url_politica_datos",
                    "terminos_enlace_politica_datos",
                    "terminos_email_soporte",
                    "terminos_boton_aceptar",
                    "terminos_boton_cerrar",
                    "terminos_enlace",
                ),
            },
        ),
    )

    def save_model(
        self,
        request,
        obj: ConfiguracionFlujoFormulario,
        form,
        change: bool,
    ) -> None:
        """Persiste la configuracion aplicando regla de una sola activa."""
        super().save_model(request, obj, form, change)
        if obj.esta_activa:
            activar_configuracion_flujo_formulario(obj)
