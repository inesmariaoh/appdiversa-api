"""
Serializers de la API de sincronizacion offline.
"""

from rest_framework import serializers

from aplicaciones.sincronizacion.models import (
    ConflictoSincronizacion,
    ResolucionConflicto,
)


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


class ConflictoSincronizacionSerializer(serializers.ModelSerializer):
    """Representa un conflicto de sincronizacion para el panel administrativo."""

    resuelto = serializers.SerializerMethodField()

    class Meta:
        model = ConflictoSincronizacion
        fields = (
            "uuid",
            "uuid_local",
            "respuesta",
            "tipo_conflicto",
            "valor_cliente",
            "valor_servidor",
            "resolucion",
            "resuelto",
            "fecha",
        )
        read_only_fields = fields

    def get_resuelto(self, obj: ConflictoSincronizacion) -> bool:
        """Indica si el conflicto ya tiene una resolucion aplicada."""
        return bool(obj.resolucion)


class ResolverConflictoEntradaSerializer(serializers.Serializer):
    """Entrada para la resolucion manual de un conflicto."""

    resolucion = serializers.ChoiceField(choices=ResolucionConflicto.choices)
    valor_manual = serializers.JSONField(required=False)
