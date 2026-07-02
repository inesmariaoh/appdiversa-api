"""
Serializers de la API de respuestas.
"""

from rest_framework import serializers

from aplicaciones.respuestas.models import OrigenRespuesta, Respuesta


class GuardarRespuestaEntradaSerializer(serializers.Serializer):
    """Entrada para guardar o actualizar una respuesta."""

    uuid_sesion = serializers.UUIDField()
    codigo_pregunta = serializers.CharField(max_length=50)
    valor = serializers.JSONField()
    observacion = serializers.CharField(required=False, allow_blank=True, default="")
    origen_respuesta = serializers.ChoiceField(
        choices=OrigenRespuesta.choices,
        required=False,
        default=OrigenRespuesta.WEB,
    )
    fecha_respuesta_cliente = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
    )
    token_cliente = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


class GuardarRespuestaSalidaSerializer(serializers.Serializer):
    """Salida tras guardar o actualizar una respuesta."""

    uuid_sesion = serializers.UUIDField()
    codigo_pregunta = serializers.CharField()
    version_respuesta = serializers.IntegerField()
    origen_respuesta = serializers.CharField()
    requiere_sincronizacion = serializers.BooleanField()
    esta_eliminado = serializers.BooleanField()
    reglas = serializers.DictField(required=False)


class RespuestaSerializer(serializers.ModelSerializer):
    """Serializer de una respuesta almacenada."""

    codigo_pregunta = serializers.CharField(source="pregunta.codigo", read_only=True)
    tipo_pregunta = serializers.CharField(
        source="pregunta.tipo_pregunta",
        read_only=True,
    )

    class Meta:
        model = Respuesta
        fields = (
            "codigo_pregunta",
            "tipo_pregunta",
            "valor_numero",
            "valor_texto",
            "valor_json",
            "valor_booleano",
            "valor_fecha",
            "valor_hora",
            "valor_fecha_hora",
            "observacion",
            "origen_respuesta",
            "version_respuesta",
            "fecha_respuesta_cliente",
            "fecha_respuesta_servidor",
        )


class RespuestasSesionSerializer(serializers.Serializer):
    """Serializer de respuestas agrupadas por sesion."""

    uuid_sesion = serializers.UUIDField()
    estado = serializers.CharField()
    respuestas = RespuestaSerializer(many=True)
