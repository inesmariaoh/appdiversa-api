"""
Administracion Django del motor de formularios parametrizables.
"""

from django.contrib import admin

from aplicaciones.auditoria.admin_mixins import ModeloAuditableAdminMixin
from aplicaciones.formularios.models import (
    Formulario,
    FormularioVersion,
    OpcionRespuesta,
    Pregunta,
    PreguntaMatrizColumna,
    PreguntaMatrizFila,
    ReglaPregunta,
    SeccionFormulario,
    TextoFormulario,
)


class ModeloAuditableAdmin(ModeloAuditableAdminMixin, admin.ModelAdmin):
    """Admin base con auditoria y soft delete."""

    actions = ["eliminar_logicamente_seleccionados", "restaurar_seleccionados"]


class FormularioVersionInline(admin.TabularInline):
    """Inline para versiones dentro del formulario."""

    model = FormularioVersion
    extra = 0
    fields = (
        "numero_version",
        "estado",
        "es_publicada",
        "descripcion_cambio",
        "fecha_publicacion",
    )
    ordering = ("numero_version",)


@admin.register(Formulario)
class FormularioAdmin(ModeloAuditableAdmin):
    """Administracion de formularios parametrizables."""

    list_display = (
        "orden",
        "codigo",
        "nombre",
        "tipo_formulario",
        "estado",
        "version_actual",
        "permite_anonimo",
        "esta_eliminado",
        "fecha_creacion",
    )
    search_fields = ("codigo", "nombre", "descripcion")
    list_filter = (
        "estado",
        "tipo_formulario",
        "permite_anonimo",
        "permite_offline",
        "esta_eliminado",
    )
    ordering = ("orden", "nombre")
    readonly_fields = ("uuid",)
    raw_id_fields = (
        "creado_por",
        "imagen_portada_repositorio",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "orden",
                    "codigo",
                    "nombre",
                    "descripcion",
                    "introduccion",
                    "objetivo",
                    "tipo_formulario",
                    "estado",
                    "version_actual",
                ),
            },
        ),
        (
            "Portada",
            {
                "fields": (
                    "imagen_portada",
                    "imagen_portada_repositorio",
                ),
            },
        ),
        (
            "Disponibilidad y flujo",
            {
                "fields": (
                    "tiempo_estimado_minutos",
                    "fecha_inicio",
                    "fecha_fin",
                    "permite_anonimo",
                    "permite_registro_final",
                    "permite_multiples_respuestas",
                    "permite_offline",
                ),
            },
        ),
    )
    inlines = [FormularioVersionInline]


class TextoFormularioInline(admin.TabularInline):
    """Inline para textos dentro de una version."""

    model = TextoFormulario
    extra = 0
    fields = ("tipo", "titulo", "contenido", "orden", "esta_activo")
    ordering = ("orden",)


class SeccionFormularioInline(admin.TabularInline):
    """Inline para secciones dentro de una version."""

    model = SeccionFormulario
    extra = 0
    fields = ("codigo", "titulo", "orden", "es_visible", "esta_activo")
    ordering = ("orden",)


@admin.register(FormularioVersion)
class FormularioVersionAdmin(ModeloAuditableAdmin):
    """Administracion de versiones de formulario."""

    list_display = (
        "formulario",
        "numero_version",
        "estado",
        "es_publicada",
        "fecha_publicacion",
        "fecha_creacion",
    )
    search_fields = ("formulario__codigo", "formulario__nombre", "descripcion_cambio")
    list_filter = ("estado", "es_publicada")
    ordering = ("formulario", "numero_version")
    autocomplete_fields = ("formulario",)
    inlines = [TextoFormularioInline, SeccionFormularioInline]


@admin.register(TextoFormulario)
class TextoFormularioAdmin(ModeloAuditableAdmin):
    """Administracion de textos de formulario."""

    list_display = ("formulario_version", "tipo", "titulo", "orden", "esta_activo")
    search_fields = ("titulo", "contenido", "formulario_version__formulario__codigo")
    list_filter = ("tipo", "esta_activo")
    ordering = ("formulario_version", "orden")
    autocomplete_fields = ("formulario_version",)


class PreguntaInline(admin.TabularInline):
    """Inline para preguntas dentro de una seccion."""

    model = Pregunta
    extra = 0
    fields = (
        "codigo",
        "texto",
        "tipo_pregunta",
        "es_obligatoria",
        "orden",
        "esta_activa",
    )
    ordering = ("orden",)


@admin.register(SeccionFormulario)
class SeccionFormularioAdmin(ModeloAuditableAdmin):
    """Administracion de secciones de formulario."""

    list_display = (
        "formulario_version",
        "codigo",
        "titulo",
        "orden",
        "es_visible",
        "esta_activo",
    )
    search_fields = ("codigo", "titulo", "formulario_version__formulario__codigo")
    list_filter = ("es_visible", "esta_activo")
    ordering = ("formulario_version", "orden")
    autocomplete_fields = ("formulario_version",)
    inlines = [PreguntaInline]


class OpcionRespuestaInline(admin.TabularInline):
    """Inline para opciones de respuesta."""

    model = OpcionRespuesta
    extra = 0
    fields = ("codigo", "etiqueta", "valor", "tiene_tooltip", "tooltip", "orden", "esta_activa")
    ordering = ("orden",)


class PreguntaMatrizFilaInline(admin.TabularInline):
    """Inline para filas de matriz."""

    model = PreguntaMatrizFila
    extra = 0
    fields = ("codigo", "etiqueta", "orden", "esta_activa")
    ordering = ("orden",)


class PreguntaMatrizColumnaInline(admin.TabularInline):
    """Inline para columnas de matriz."""

    model = PreguntaMatrizColumna
    extra = 0
    fields = ("codigo", "etiqueta", "valor", "orden", "esta_activa")
    ordering = ("orden",)


@admin.register(Pregunta)
class PreguntaAdmin(ModeloAuditableAdmin):
    """Administracion de preguntas."""

    list_display = (
        "codigo",
        "texto",
        "tipo_pregunta",
        "seccion",
        "usa_catalogo",
        "catalogo_asociado",
        "esta_activa",
        "orden",
    )
    search_fields = ("codigo", "texto", "seccion__codigo")
    list_filter = (
        "tipo_pregunta",
        "usa_catalogo",
        "catalogo_asociado",
        "es_obligatoria",
        "es_pregunta_filtro",
        "esta_activa",
    )
    ordering = ("seccion", "orden")
    autocomplete_fields = (
        "seccion",
        "catalogo_asociado",
        "pregunta_padre_catalogo",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "seccion",
                    "codigo",
                    "texto",
                    "descripcion",
                    "tiene_tooltip",
                    "tooltip",
                    "tipo_pregunta",
                    "orden",
                    "esta_activa",
                ),
            },
        ),
        (
            "Configuracion de respuesta",
            {
                "fields": (
                    "es_obligatoria",
                    "es_pregunta_filtro",
                    "tipo_validacion_filtro",
                    "valor_filtro_esperado",
                    "bloquea_continuacion_si_no_cumple",
                    "mensaje_no_cumple",
                    "permite_otro",
                    "texto_otro_obligatorio",
                    "permite_observacion",
                    "longitud_minima",
                    "longitud_maxima",
                    "valor_minimo",
                    "valor_maximo",
                    "expresion_regular",
                    "mensaje_error",
                ),
            },
        ),
        (
            "Catalogo parametrizable",
            {
                "fields": (
                    "usa_catalogo",
                    "catalogo_asociado",
                    "pregunta_padre_catalogo",
                    "campo_codigo_padre_catalogo",
                    "permite_busqueda_catalogo",
                    "limite_items_catalogo",
                ),
            },
        ),
    )
    inlines = [
        OpcionRespuestaInline,
        PreguntaMatrizFilaInline,
        PreguntaMatrizColumnaInline,
    ]


@admin.register(OpcionRespuesta)
class OpcionRespuestaAdmin(ModeloAuditableAdmin):
    """Administracion de opciones de respuesta."""

    list_display = (
        "pregunta",
        "codigo",
        "etiqueta",
        "orden",
        "esta_activa",
    )
    search_fields = ("codigo", "etiqueta", "pregunta__codigo")
    list_filter = ("esta_activa", "es_excluyente", "activa_otro")
    ordering = ("pregunta", "orden")
    autocomplete_fields = ("pregunta",)


@admin.register(PreguntaMatrizFila)
class PreguntaMatrizFilaAdmin(ModeloAuditableAdmin):
    """Administracion de filas de matriz."""

    list_display = ("pregunta", "codigo", "etiqueta", "orden", "esta_activa")
    search_fields = ("codigo", "etiqueta", "pregunta__codigo")
    list_filter = ("esta_activa",)
    ordering = ("pregunta", "orden")
    autocomplete_fields = ("pregunta",)


@admin.register(PreguntaMatrizColumna)
class PreguntaMatrizColumnaAdmin(ModeloAuditableAdmin):
    """Administracion de columnas de matriz."""

    list_display = ("pregunta", "codigo", "etiqueta", "valor", "orden", "esta_activa")
    search_fields = ("codigo", "etiqueta", "pregunta__codigo")
    list_filter = ("esta_activa",)
    ordering = ("pregunta", "orden")
    autocomplete_fields = ("pregunta",)


@admin.register(ReglaPregunta)
class ReglaPreguntaAdmin(ModeloAuditableAdmin):
    """Administracion de reglas condicionales."""

    list_display = (
        "pregunta_origen",
        "operador",
        "accion",
        "pregunta_destino",
        "seccion_destino",
        "esta_activa",
    )
    search_fields = ("pregunta_origen__codigo", "pregunta_origen__texto", "mensaje")
    list_filter = ("operador", "accion", "esta_activa")
    ordering = ("pregunta_origen",)
    autocomplete_fields = (
        "pregunta_origen",
        "pregunta_destino",
        "seccion_destino",
    )
