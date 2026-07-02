"""
Serializers de la API de exportaciones.
"""

from rest_framework import serializers

from aplicaciones.exportaciones.constantes import FormatoExportacion
from aplicaciones.exportaciones.models import Exportacion


class ExportacionSerializer(serializers.ModelSerializer):
    """Serializer de exportaciones registradas."""

    archivo_uuid = serializers.UUIDField(
        source="archivo.uuid",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Exportacion
        fields = (
            "uuid",
            "tipo",
            "estado",
            "usuario",
            "fecha_inicio",
            "fecha_fin",
            "archivo_uuid",
            "formato",
            "parametros",
            "registros_exportados",
            "error",
        )


class ExportacionEntradaSerializer(serializers.Serializer):
    """Entrada base para solicitudes de exportacion."""

    formato = serializers.ChoiceField(choices=FormatoExportacion.choices)
    parametros = serializers.JSONField(required=False, default=dict)
    usuario = serializers.CharField(required=False, allow_blank=True, default="")


class ExportacionRespuestasEntradaSerializer(ExportacionEntradaSerializer):
    """Entrada para exportacion de respuestas."""

    parametros = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Filtros: formulario_codigo, version, fecha_inicio, fecha_fin, estado_sesion, idioma.",
    )


class ExportacionCatalogosEntradaSerializer(ExportacionEntradaSerializer):
    """Entrada para exportacion de catalogos."""

    parametros = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Filtros: catalogo_codigo.",
    )


class ExportacionAnaliticaEntradaSerializer(ExportacionEntradaSerializer):
    """Entrada para exportacion de analitica."""

    parametros = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Filtros: formulario_codigo, fecha_inicio, fecha_fin, estado_sesion.",
    )
