"""
Serializers de finalizacion y resumen de formularios anonimos.
"""

from rest_framework import serializers


class PreguntaPendienteSerializer(serializers.Serializer):
    """Detalle de una pregunta obligatoria pendiente."""

    codigo = serializers.CharField()
    texto = serializers.CharField()
    seccion_codigo = serializers.CharField()
    seccion_titulo = serializers.CharField()
    orden = serializers.IntegerField()
    motivo = serializers.CharField(required=False)
    mensaje = serializers.CharField(required=False)


class ValidacionFinalizacionSerializer(serializers.Serializer):
    """Resultado de la validacion previa a finalizar."""

    es_valido = serializers.BooleanField()
    total_pendientes = serializers.IntegerField()
    preguntas_pendientes = PreguntaPendienteSerializer(many=True)


class ResumenRespuestaSerializer(serializers.Serializer):
    """Item de respuesta dentro del resumen de sesion."""

    seccion_codigo = serializers.CharField()
    seccion_titulo = serializers.CharField()
    pregunta_codigo = serializers.CharField()
    pregunta_texto = serializers.CharField()
    tipo_pregunta = serializers.CharField()
    valor = serializers.JSONField()
    valor_legible = serializers.CharField()
    observacion = serializers.CharField()


class FormularioResumenSerializer(serializers.Serializer):
    """Datos resumidos del formulario en una sesion."""

    uuid = serializers.UUIDField()
    codigo = serializers.CharField()
    nombre = serializers.CharField()


class VersionResumenSerializer(serializers.Serializer):
    """Datos resumidos de la version del formulario."""

    numero_version = serializers.IntegerField()


class ResumenFormularioSesionSerializer(serializers.Serializer):
    """Resumen completo de respuestas de una sesion."""

    uuid_sesion = serializers.UUIDField()
    estado = serializers.CharField()
    formulario = FormularioResumenSerializer()
    version = VersionResumenSerializer()
    respuestas = ResumenRespuestaSerializer(many=True)


class FinalizacionFormularioSerializer(serializers.Serializer):
    """Resultado de finalizacion exitosa de formulario."""

    estado = serializers.CharField()
    mensaje = serializers.CharField()
    resumen = ResumenFormularioSesionSerializer()


class FinalizacionEntradaSerializer(serializers.Serializer):
    """Entrada opcional al finalizar formulario."""

    correo = serializers.EmailField(required=False, allow_blank=True)
