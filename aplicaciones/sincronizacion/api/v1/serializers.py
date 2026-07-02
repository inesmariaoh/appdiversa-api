"""
Serializers de la API de sincronizacion offline.
"""

from rest_framework import serializers


class OperacionSincronizacionEntradaSerializer(serializers.Serializer):
    """Operacion individual dentro de un lote de sincronizacion."""

    uuid_local = serializers.UUIDField()
    codigo_pregunta = serializers.CharField(max_length=100)
    valor = serializers.JSONField()
    version_cliente = serializers.IntegerField(min_value=0)
    fecha_cliente = serializers.DateTimeField()
    checksum = serializers.CharField(max_length=128, required=False, allow_blank=True, default="")


class SincronizarBatchEntradaSerializer(serializers.Serializer):
    """Entrada del endpoint de sincronizacion por lotes."""

    uuid_sesion = serializers.UUIDField()
    token_cliente = serializers.CharField(max_length=255)
    dispositivo = serializers.CharField(max_length=150)
    version_app = serializers.CharField(max_length=50)
    operaciones = OperacionSincronizacionEntradaSerializer(many=True, min_length=1)


class ResultadoOperacionErrorSerializer(serializers.Serializer):
    """Detalle de error en una operacion del lote."""

    uuid_local = serializers.CharField()
    mensaje = serializers.CharField(allow_null=True)


class ResultadoOperacionConflictoSerializer(serializers.Serializer):
    """Detalle de conflicto en una operacion del lote."""

    uuid_local = serializers.CharField()
    mensaje = serializers.CharField(allow_null=True)
    respuesta_id = serializers.IntegerField(allow_null=True)


class SincronizarBatchSalidaSerializer(serializers.Serializer):
    """Respuesta agregada del procesamiento de un lote."""

    operaciones_procesadas = serializers.IntegerField()
    operaciones_actualizadas = serializers.IntegerField()
    duplicadas = serializers.IntegerField()
    conflictos = ResultadoOperacionConflictoSerializer(many=True)
    errores = ResultadoOperacionErrorSerializer(many=True)
