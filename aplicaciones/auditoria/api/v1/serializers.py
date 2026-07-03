"""
Serializers de la API de consulta de auditoria.
"""

from rest_framework import serializers

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.models import RegistroAuditoria


class RegistroAuditoriaSerializer(serializers.ModelSerializer):
    """Serializer de lectura de registros de auditoria."""

    usuario_username = serializers.CharField(
        source="usuario.username",
        read_only=True,
        default=None,
    )

    class Meta:
        model = RegistroAuditoria
        fields = (
            "id",
            "entidad",
            "entidad_id",
            "accion",
            "usuario",
            "usuario_username",
            "identificador_keycloak",
            "uuid_sesion_anonima",
            "ip",
            "user_agent",
            "valor_anterior",
            "valor_nuevo",
            "descripcion",
            "fecha_accion",
        )
        read_only_fields = fields


class FiltrosAuditoriaSerializer(serializers.Serializer):
    """Valida los parametros de consulta de la API de auditoria."""

    entidad = serializers.CharField(required=False, allow_blank=True, default="")
    entidad_id = serializers.CharField(required=False, allow_blank=True, default="")
    accion = serializers.ChoiceField(
        choices=AccionAuditoria.choices,
        required=False,
        allow_blank=True,
        default="",
    )
    usuario = serializers.IntegerField(required=False, allow_null=True, default=None)
    fecha_inicio = serializers.DateField(required=False, allow_null=True, default=None)
    fecha_fin = serializers.DateField(required=False, allow_null=True, default=None)
    busqueda = serializers.CharField(required=False, allow_blank=True, default="")
