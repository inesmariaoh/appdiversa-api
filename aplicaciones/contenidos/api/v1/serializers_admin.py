"""
Serializers de la API administrativa de configuracion de interfaz.
"""

from rest_framework import serializers

from aplicaciones.contenidos.constantes import TemaInterfaz

_OPCIONES_TEMA = [opcion[0] for opcion in TemaInterfaz.OPCIONES]


class AccesibilidadAdminSerializer(serializers.Serializer):
    """Valida las banderas de accesibilidad editables por administracion."""

    lectura_voz_habilitada = serializers.BooleanField(required=False)
    comandos_voz_habilitada = serializers.BooleanField(required=False)
    lengua_senas_habilitada = serializers.BooleanField(required=False)
    fuente_dislexia_habilitada = serializers.BooleanField(required=False)
    tema_por_defecto = serializers.ChoiceField(
        choices=_OPCIONES_TEMA,
        required=False,
    )
    url_lengua_senas = serializers.URLField(required=False, allow_blank=True)
    texto_lengua_senas = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    centro_relevo_habilitado = serializers.BooleanField(required=False)
    url_centro_relevo = serializers.URLField(required=False, allow_blank=True)


class AccesibilidadAdminEsquemaSerializer(serializers.Serializer):
    """Esquema de respuesta del bloque de accesibilidad para OpenAPI."""

    lectura_voz_habilitada = serializers.BooleanField(default=True)
    comandos_voz_habilitada = serializers.BooleanField(default=False)
    lengua_senas_habilitada = serializers.BooleanField(default=False)
    fuente_dislexia_habilitada = serializers.BooleanField(default=False)
    tema_por_defecto = serializers.ChoiceField(
        choices=_OPCIONES_TEMA,
        default=TemaInterfaz.CLARO,
    )
    url_lengua_senas = serializers.URLField(allow_blank=True, default="")
    texto_lengua_senas = serializers.CharField(allow_blank=True, default="")
    centro_relevo_habilitado = serializers.BooleanField(default=False)
    url_centro_relevo = serializers.URLField(allow_blank=True, default="")
