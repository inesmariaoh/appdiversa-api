"""
Serializers de la API publica de catalogos.
"""

from typing import Any

from rest_framework import serializers

from aplicaciones.catalogos.models import Catalogo, ItemCatalogo
from aplicaciones.internacionalizacion.api.mixins import TraduccionSerializerMixin


class CatalogoSerializer(
    TraduccionSerializerMixin,
    serializers.ModelSerializer,
):
    """Serializer resumido para catalogos activos."""

    nombre_entidad = "Catalogo"

    class Meta:
        model = Catalogo
        fields = (
            "codigo",
            "nombre",
            "descripcion",
            "tipo_catalogo",
            "orden",
        )

    def to_representation(self, instancia: Catalogo) -> dict[str, Any]:
        """Serializa el catalogo aplicando traducciones si existen."""
        datos = super().to_representation(instancia)
        return self.aplicar_traducciones_campos(
            instancia,
            datos,
            ("nombre", "descripcion"),
        )


class ItemCatalogoSerializer(
    TraduccionSerializerMixin,
    serializers.ModelSerializer,
):
    """Serializer para items de un catalogo."""

    nombre_entidad = "ItemCatalogo"
    codigo_catalogo = serializers.CharField(source="catalogo.codigo", read_only=True)
    codigo_padre = serializers.CharField(
        source="item_padre.codigo",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = ItemCatalogo
        fields = (
            "codigo",
            "codigo_catalogo",
            "nombre",
            "descripcion",
            "valor",
            "codigo_padre",
            "codigo_externo",
            "metadatos",
            "orden",
            "esta_activo",
        )

    def to_representation(self, instancia: ItemCatalogo) -> dict[str, Any]:
        """Serializa el item aplicando traducciones si existen."""
        datos = super().to_representation(instancia)
        datos = self.aplicar_traducciones_campos(
            instancia,
            datos,
            ("nombre", "descripcion"),
        )
        if self.context.get("incluir_accesibilidad"):
            datos["contenido_accesible"] = self.construir_contenido_accesible_campos(
                instancia,
                ("nombre", "descripcion"),
            )
        return datos


class FiltrosItemsCatalogoSerializer(serializers.Serializer):
    """Filtros opcionales para consulta de items de catalogo."""

    codigo_padre = serializers.CharField(required=False, allow_blank=True)
    solo_activos = serializers.BooleanField(required=False, default=True)
    busqueda = serializers.CharField(required=False, allow_blank=True)
    limite = serializers.IntegerField(required=False, min_value=1)
    idioma = serializers.CharField(required=False, allow_blank=True)
    incluir_accesibilidad = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs: dict) -> dict:
        """Normaliza filtros vacios antes de invocar servicios."""
        codigo_padre = attrs.get("codigo_padre")
        if codigo_padre is not None and not codigo_padre.strip():
            attrs["codigo_padre"] = None

        busqueda = attrs.get("busqueda")
        if busqueda is not None and not busqueda.strip():
            attrs["busqueda"] = None

        idioma = attrs.get("idioma")
        if idioma is not None and not idioma.strip():
            attrs["idioma"] = None

        return attrs
