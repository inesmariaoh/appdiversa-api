"""
Serializers de la API de analitica.
"""

from rest_framework import serializers


class FiltrosRespuestasAnaliticasSerializer(serializers.Serializer):
    """Filtros opcionales para consulta de respuestas analiticas."""

    formulario_codigo = serializers.CharField(required=False, allow_blank=True)
    fecha_inicio = serializers.CharField(required=False, allow_blank=True)
    fecha_fin = serializers.CharField(required=False, allow_blank=True)
    estado_sesion = serializers.CharField(required=False, allow_blank=True)


class RespuestaAnaliticaSerializer(serializers.Serializer):
    """Formato plano de una respuesta para consumo analitico."""

    uuid_sesion = serializers.UUIDField()
    estado_sesion = serializers.CharField()
    fecha_inicio_sesion = serializers.CharField(allow_null=True)
    fecha_ultima_actividad = serializers.CharField(allow_null=True)
    formulario_uuid = serializers.UUIDField()
    formulario_codigo = serializers.CharField()
    formulario_nombre = serializers.CharField()
    tipo_formulario = serializers.CharField()
    numero_version = serializers.IntegerField()
    seccion_codigo = serializers.CharField()
    seccion_titulo = serializers.CharField()
    pregunta_codigo = serializers.CharField()
    pregunta_texto = serializers.CharField()
    tipo_pregunta = serializers.CharField()
    usa_catalogo = serializers.BooleanField()
    catalogo_codigo = serializers.CharField(allow_null=True)
    catalogo_nombre = serializers.CharField(allow_null=True)
    respuesta_valor = serializers.JSONField(allow_null=True)
    respuesta_texto = serializers.CharField()
    respuesta_numero = serializers.CharField()
    respuesta_json = serializers.JSONField(allow_null=True)
    observacion = serializers.CharField()
    origen_respuesta = serializers.CharField()
    version_respuesta = serializers.IntegerField()
    fecha_respuesta_cliente = serializers.CharField(allow_null=True)
    fecha_respuesta_servidor = serializers.CharField(allow_null=True)
    es_anonima = serializers.BooleanField()
    es_offline = serializers.BooleanField()
