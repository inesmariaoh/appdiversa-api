"""
Serializers del motor de reglas del form engine.
"""

from rest_framework import serializers


class ResultadoReglasSerializer(serializers.Serializer):
    """Serializer del resultado de evaluacion de reglas."""

    preguntas_ocultas = serializers.ListField(
        child=serializers.CharField(),
        default=list,
    )
    preguntas_visibles = serializers.ListField(
        child=serializers.CharField(),
        default=list,
    )
    preguntas_deshabilitadas = serializers.ListField(
        child=serializers.CharField(),
        default=list,
    )
    preguntas_habilitadas = serializers.ListField(
        child=serializers.CharField(),
        default=list,
    )
    preguntas_obligatorias = serializers.ListField(
        child=serializers.CharField(),
        default=list,
    )
    preguntas_opcionales = serializers.ListField(
        child=serializers.CharField(),
        default=list,
    )
    saltar_a_pregunta = serializers.CharField(allow_null=True, default=None)
    saltar_a_seccion = serializers.CharField(allow_null=True, default=None)
    finalizar_formulario = serializers.BooleanField(default=False)
    no_aplica_formulario = serializers.BooleanField(default=False)
    mensajes = serializers.ListField(
        child=serializers.CharField(),
        default=list,
    )
