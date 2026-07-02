"""
Serializers de la API del repositorio documental.
"""

from rest_framework import serializers

from aplicaciones.archivos.constantes import OrigenArchivo, TipoArchivo
from aplicaciones.archivos.models import ArchivoRepositorio


class SubirArchivoEntradaSerializer(serializers.Serializer):
    """Entrada para subir un archivo al repositorio."""

    archivo = serializers.FileField()
    tipo_archivo = serializers.ChoiceField(choices=TipoArchivo.choices)
    origen = serializers.ChoiceField(choices=OrigenArchivo.choices)
    descripcion = serializers.CharField(required=False, allow_blank=True, default="")
    es_publico = serializers.BooleanField(required=False, default=False)
    metadatos = serializers.JSONField(required=False, default=dict)
    usuario_keycloak = serializers.CharField(required=False, allow_blank=True, default="")
    uuid_sesion = serializers.UUIDField(required=False, allow_null=True, default=None)
    token_cliente = serializers.CharField(required=False, allow_blank=True, default="")


class ArchivoRepositorioSerializer(serializers.ModelSerializer):
    """Serializer de metadatos de un archivo del repositorio."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = ArchivoRepositorio
        fields = (
            "uuid",
            "nombre_original",
            "extension",
            "mime_type",
            "tamano_bytes",
            "checksum_sha256",
            "tipo_archivo",
            "es_publico",
            "origen",
            "estado",
            "descripcion",
            "metadatos",
            "fecha_carga",
            "usuario_keycloak",
            "uuid_sesion",
            "url",
        )

    def get_url(self, archivo: ArchivoRepositorio) -> str | None:
        """Retorna la URL de acceso al archivo si esta activo."""
        from aplicaciones.archivos.servicios import construir_url

        return construir_url(archivo, self.context.get("request"))
