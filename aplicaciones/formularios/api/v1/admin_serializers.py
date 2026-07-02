"""
Serializers de la API administrativa de formularios.
"""

from rest_framework import serializers

from aplicaciones.formularios.models import (
    Formulario,
    FormularioVersion,
    OpcionRespuesta,
    Pregunta,
    ReglaPregunta,
    SeccionFormulario,
    TextoFormulario,
)


class FormularioAdminSerializer(serializers.ModelSerializer):
    """Serializer de formularios para administracion."""

    class Meta:
        model = Formulario
        fields = (
            "id",
            "uuid",
            "codigo",
            "nombre",
            "descripcion",
            "introduccion",
            "objetivo",
            "tipo_formulario",
            "tiempo_estimado_minutos",
            "estado",
            "version_actual",
            "permite_anonimo",
            "permite_registro_final",
            "permite_multiples_respuestas",
            "permite_offline",
            "fecha_inicio",
            "fecha_fin",
            "orden",
            "esta_eliminado",
            "fecha_creacion",
            "fecha_modificacion",
        )
        read_only_fields = ("id", "uuid", "esta_eliminado", "fecha_creacion", "fecha_modificacion")


class FormularioVersionAdminSerializer(serializers.ModelSerializer):
    """Serializer de versiones de formulario."""

    class Meta:
        model = FormularioVersion
        fields = (
            "id",
            "formulario",
            "numero_version",
            "estado",
            "descripcion_cambio",
            "es_publicada",
            "fecha_publicacion",
            "fecha_creacion",
            "fecha_modificacion",
        )
        read_only_fields = fields


class SeccionFormularioAdminSerializer(serializers.ModelSerializer):
    """Serializer de secciones para administracion."""

    class Meta:
        model = SeccionFormulario
        fields = (
            "id",
            "formulario_version",
            "codigo",
            "titulo",
            "descripcion",
            "texto_ayuda",
            "orden",
            "es_visible",
            "esta_activo",
            "esta_eliminado",
        )
        read_only_fields = ("id", "formulario_version", "esta_eliminado")


class PreguntaAdminSerializer(serializers.ModelSerializer):
    """Serializer de preguntas para administracion."""

    class Meta:
        model = Pregunta
        fields = (
            "id",
            "seccion",
            "codigo",
            "texto",
            "descripcion",
            "tooltip",
            "tiene_tooltip",
            "tipo_pregunta",
            "es_obligatoria",
            "es_pregunta_filtro",
            "tipo_validacion_filtro",
            "valor_filtro_esperado",
            "bloquea_continuacion_si_no_cumple",
            "mensaje_no_cumple",
            "permite_otro",
            "permite_observacion",
            "orden",
            "longitud_minima",
            "longitud_maxima",
            "valor_minimo",
            "valor_maximo",
            "expresion_regular",
            "mensaje_error",
            "esta_activa",
            "usa_catalogo",
            "catalogo_asociado",
            "pregunta_padre_catalogo",
            "campo_codigo_padre_catalogo",
            "permite_busqueda_catalogo",
            "limite_items_catalogo",
            "esta_eliminado",
        )
        read_only_fields = ("id", "seccion", "esta_eliminado")


class OpcionRespuestaAdminSerializer(serializers.ModelSerializer):
    """Serializer de opciones para administracion."""

    class Meta:
        model = OpcionRespuesta
        fields = (
            "id",
            "pregunta",
            "codigo",
            "etiqueta",
            "valor",
            "tooltip",
            "tiene_tooltip",
            "orden",
            "es_excluyente",
            "activa_otro",
            "esta_activa",
            "esta_eliminado",
        )
        read_only_fields = ("id", "pregunta", "esta_eliminado")


class TextoFormularioAdminSerializer(serializers.ModelSerializer):
    """Serializer de textos para administracion."""

    class Meta:
        model = TextoFormulario
        fields = (
            "id",
            "formulario_version",
            "tipo",
            "titulo",
            "contenido",
            "orden",
            "esta_activo",
            "esta_eliminado",
        )
        read_only_fields = ("id", "formulario_version", "esta_eliminado")


class ReglaPreguntaAdminSerializer(serializers.ModelSerializer):
    """Serializer de reglas para administracion."""

    class Meta:
        model = ReglaPregunta
        fields = (
            "id",
            "pregunta_origen",
            "operador",
            "valor_esperado",
            "pregunta_destino",
            "seccion_destino",
            "accion",
            "mensaje",
            "esta_activa",
            "esta_eliminado",
        )
        read_only_fields = ("id", "pregunta_origen", "esta_eliminado")


class ReordenarPreguntasEntradaSerializer(serializers.Serializer):
    """Entrada para reordenamiento masivo de preguntas."""

    preguntas = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False,
    )

    def validate_preguntas(self, valor: list) -> list:
        """Valida estructura de items de reordenamiento."""
        for item in valor:
            if "id" not in item or "orden" not in item:
                raise serializers.ValidationError(
                    "Cada ítem debe incluir id y orden.",
                )
        return valor


class VersionCreacionEntradaSerializer(serializers.Serializer):
    """Entrada opcional para creacion de version."""

    descripcion_cambio = serializers.CharField(required=False, allow_blank=True, default="")


class ReordenarCodigosEntradaSerializer(serializers.Serializer):
    """Entrada de reordenamiento por codigos para el panel administrativo."""

    codigos = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=False,
    )


class TextosBulkEntradaSerializer(serializers.Serializer):
    """Entrada masiva de textos del formulario para el panel."""

    textos = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=True,
    )


class ReglaFormularioEntradaSerializer(serializers.Serializer):
    """Entrada de reglas con codigos de preguntas y secciones."""

    pregunta_origen = serializers.CharField(max_length=100, required=False)
    operador = serializers.CharField(max_length=50)
    valor_esperado = serializers.JSONField()
    accion = serializers.CharField(max_length=50)
    pregunta_destino = serializers.CharField(
        max_length=100,
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    seccion_destino = serializers.CharField(
        max_length=100,
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    mensaje = serializers.CharField(required=False, allow_blank=True, default="")
    esta_activa = serializers.BooleanField(required=False, default=True)
