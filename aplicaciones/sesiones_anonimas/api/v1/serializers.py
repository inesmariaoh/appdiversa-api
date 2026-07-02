"""
Serializers de la API de sesiones anonimas.
"""

from rest_framework import serializers

from aplicaciones.sesiones_anonimas.models import SesionAnonima


class CrearSesionAnonimaEntradaSerializer(serializers.Serializer):
    """Entrada para crear o reutilizar una sesion anonima."""

    uuid_sesion = serializers.UUIDField()
    uuid_formulario = serializers.UUIDField()
    token_cliente = serializers.CharField(required=False, allow_blank=True, default="")
    idioma = serializers.CharField(required=False, allow_blank=True, default="")
    zona_horaria = serializers.CharField(required=False, allow_blank=True, default="")
    es_offline = serializers.BooleanField(required=False, default=False)


class SesionAnonimaSerializer(serializers.ModelSerializer):
    """Serializer de respuesta para sesion anonima."""

    class Meta:
        model = SesionAnonima
        fields = ("uuid_sesion", "estado", "token_cliente")
