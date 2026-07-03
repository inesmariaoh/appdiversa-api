"""
Serializers de la API administrativa de catalogos parametrizables.
"""

from rest_framework import serializers

from aplicaciones.catalogos.models import Catalogo, ItemCatalogo


class CatalogoAdminSerializer(serializers.ModelSerializer):
    """Representa un catalogo para el panel administrativo."""

    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Catalogo
        fields = (
            "id",
            "codigo",
            "nombre",
            "descripcion",
            "tipo_catalogo",
            "esta_activo",
            "es_sistema",
            "orden",
            "total_items",
            "fecha_creacion",
            "fecha_modificacion",
        )
        read_only_fields = ("id", "es_sistema", "total_items", "fecha_creacion", "fecha_modificacion")

    def get_total_items(self, obj: Catalogo) -> int:
        """Cuenta los items no eliminados del catalogo."""
        return obj.items.filter(esta_eliminado=False).count()


class CatalogoAdminEntradaSerializer(serializers.Serializer):
    """Entrada para crear o actualizar un catalogo."""

    codigo = serializers.CharField(max_length=100)
    nombre = serializers.CharField(max_length=255)
    descripcion = serializers.CharField(required=False, allow_blank=True, default="")
    tipo_catalogo = serializers.CharField(max_length=100)
    esta_activo = serializers.BooleanField(required=False, default=True)
    orden = serializers.IntegerField(required=False, min_value=1, default=1)


class ItemCatalogoAdminSerializer(serializers.ModelSerializer):
    """Representa un item de catalogo para el panel administrativo."""

    codigo_padre = serializers.CharField(
        source="item_padre.codigo",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = ItemCatalogo
        fields = (
            "id",
            "codigo",
            "nombre",
            "descripcion",
            "valor",
            "codigo_padre",
            "codigo_externo",
            "metadatos",
            "orden",
            "esta_activo",
            "fecha_creacion",
            "fecha_modificacion",
        )
        read_only_fields = ("id", "codigo_padre", "fecha_creacion", "fecha_modificacion")


class ItemCatalogoAdminEntradaSerializer(serializers.Serializer):
    """Entrada para crear o actualizar un item de catalogo."""

    codigo = serializers.CharField(max_length=100)
    nombre = serializers.CharField(max_length=255)
    descripcion = serializers.CharField(required=False, allow_blank=True, default="")
    valor = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    codigo_padre = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    codigo_externo = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    metadatos = serializers.JSONField(required=False)
    orden = serializers.IntegerField(required=False, min_value=1, default=1)
    esta_activo = serializers.BooleanField(required=False, default=True)
