"""
Serializers de la API de notificaciones.
"""

from rest_framework import serializers

from aplicaciones.notificaciones.models import Notificacion, PlantillaNotificacion


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer de notificaciones registradas."""

    codigo_plantilla = serializers.CharField(
        source="plantilla.codigo",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Notificacion
        fields = (
            "uuid",
            "codigo_plantilla",
            "canal",
            "destinatario",
            "estado",
            "fecha_programada",
            "fecha_envio",
            "asunto_generado",
            "contenido_generado",
            "variables_utilizadas",
            "respuesta_proveedor",
            "numero_intentos",
            "error_envio",
        )


class ProbarNotificacionEntradaSerializer(serializers.Serializer):
    """Entrada para generar una notificacion de prueba."""

    codigo_plantilla = serializers.CharField(max_length=100)
    destinatario = serializers.CharField(max_length=500)
    variables = serializers.JSONField(required=False, default=dict)
