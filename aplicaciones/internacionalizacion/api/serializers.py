"""
Serializers compartidos de internacionalizacion.
"""

from typing import Any

from rest_framework import serializers

from aplicaciones.internacionalizacion.models import TraduccionContenido
from aplicaciones.internacionalizacion.servicios import (
    construir_contenido_accesible_vacio,
    construir_url_archivo_campo,
)


class FiltroIdiomaSerializer(serializers.Serializer):
    """Filtro opcional de idioma para endpoints publicos."""

    idioma = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs: dict) -> dict:
        """Normaliza el codigo de idioma vacio."""
        idioma = attrs.get("idioma")
        if idioma is not None and not idioma.strip():
            attrs["idioma"] = None
        return attrs


class FiltroIncluirAccesibilidadSerializer(FiltroIdiomaSerializer):
    """Filtro de idioma con opcion de incluir contenido accesible."""

    incluir_accesibilidad = serializers.BooleanField(required=False, default=False)


class ContenidoAccesibleSerializer(serializers.Serializer):
    """Esquema de contenido accesible multimodal."""

    lectura_facil = serializers.CharField(default="")
    texto_alternativo = serializers.CharField(default="")
    transcripcion = serializers.CharField(default="")
    archivo_audio = serializers.CharField(allow_null=True, default=None)
    archivo_video = serializers.CharField(allow_null=True, default=None)
    archivo_imagen = serializers.CharField(allow_null=True, default=None)
    archivo_lengua_senas = serializers.CharField(allow_null=True, default=None)
    metadatos = serializers.JSONField(default=dict)


class TraduccionContenidoSerializer(serializers.ModelSerializer):
    """Serializer de traducciones con contenido accesible multimodal."""

    archivo_audio = serializers.SerializerMethodField()
    archivo_video = serializers.SerializerMethodField()
    archivo_imagen = serializers.SerializerMethodField()
    archivo_lengua_senas = serializers.SerializerMethodField()
    codigo_idioma = serializers.CharField(source="idioma.codigo_iso", read_only=True)

    class Meta:
        model = TraduccionContenido
        fields = (
            "id",
            "codigo_idioma",
            "entidad",
            "entidad_uuid",
            "campo",
            "valor_traducido",
            "lectura_facil",
            "texto_alternativo",
            "transcripcion",
            "archivo_audio",
            "archivo_video",
            "archivo_imagen",
            "archivo_lengua_senas",
            "metadatos",
            "esta_activa",
        )

    def get_archivo_audio(self, traduccion: TraduccionContenido) -> str | None:
        """Retorna la URL del archivo de audio si existe."""
        return construir_url_archivo_campo(
            traduccion,
            "archivo_audio",
            self.context.get("request"),
        )

    def get_archivo_video(self, traduccion: TraduccionContenido) -> str | None:
        """Retorna la URL del archivo de video si existe."""
        return construir_url_archivo_campo(
            traduccion,
            "archivo_video",
            self.context.get("request"),
        )

    def get_archivo_imagen(self, traduccion: TraduccionContenido) -> str | None:
        """Retorna la URL de la imagen si existe."""
        return construir_url_archivo_campo(
            traduccion,
            "archivo_imagen",
            self.context.get("request"),
        )

    def get_archivo_lengua_senas(self, traduccion: TraduccionContenido) -> str | None:
        """Retorna la URL del archivo de lengua de senas si existe."""
        return construir_url_archivo_campo(
            traduccion,
            "archivo_lengua_senas",
            self.context.get("request"),
        )

    def to_representation(self, instancia: TraduccionContenido) -> dict[str, Any]:
        """Normaliza textos vacios y metadatos en la representacion."""
        datos = super().to_representation(instancia)
        vacio = construir_contenido_accesible_vacio()
        for campo_texto in ("lectura_facil", "texto_alternativo", "transcripcion"):
            valor = datos.get(campo_texto)
            datos[campo_texto] = valor if valor is not None else vacio[campo_texto]
        metadatos = datos.get("metadatos")
        datos["metadatos"] = metadatos if isinstance(metadatos, dict) else {}
        return datos


class FiltrosTraduccionesSerializer(serializers.Serializer):
    """Filtros opcionales para listado de traducciones."""

    idioma = serializers.CharField(required=False, allow_blank=True)
    entidad = serializers.CharField(required=False, allow_blank=True)
    entidad_uuid = serializers.UUIDField(required=False)
    campo = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs: dict) -> dict:
        """Normaliza filtros vacios antes de invocar servicios."""
        for nombre_campo in ("idioma", "entidad", "campo"):
            valor = attrs.get(nombre_campo)
            if valor is not None and not str(valor).strip():
                attrs[nombre_campo] = None
        return attrs
