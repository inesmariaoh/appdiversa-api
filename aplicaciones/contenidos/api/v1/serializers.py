"""
Serializers de la API publica de configuracion de interfaz.
"""

from typing import Any

from rest_framework import serializers

from aplicaciones.contenidos.constantes import ValoresPorDefectoInterfaz
from aplicaciones.contenidos.models import ConfiguracionInterfaz
from aplicaciones.contenidos.selectores import obtener_mapa_logos_interfaz
from aplicaciones.contenidos.servicios import (
    construir_configuracion_por_defecto,
    construir_lista_logos_publica,
    resolver_texto_alternativo_logo,
    resolver_url_imagen_configuracion,
)
from aplicaciones.contenidos.servicios_flujo_formulario import (
    construir_bloque_flujo_formulario_publico,
)
from aplicaciones.internacionalizacion.api.serializers import (
    ContenidoAccesibleSerializer,
    FiltroIncluirAccesibilidadSerializer,
)
from aplicaciones.internacionalizacion.servicios import (
    aplicar_texto_traducido,
    construir_mapa_contenido_accesible,
    normalizar_codigo_idioma,
    resolver_uuid_entidad,
)

CAMPOS_IMAGEN = (
    "logo_principal",
    "logo_secundario",
    "logo_institucional",
    "favicon",
)

CAMPOS_TEXTO_TRADUCIBLES = (
    "nombre_aplicativo",
    "nombre_corto",
    "descripcion_aplicativo",
    "texto_pie_pagina",
    "texto_titulo_seccion_encuestas",
    "texto_descripcion_seccion_encuestas",
    "texto_terminos_condiciones",
    "texto_autorizacion_datos",
    "texto_verificacion_exitosa_titulo",
    "texto_verificacion_exitosa_cuerpo",
    "texto_confirmacion_envio_titulo",
    "texto_confirmacion_envio_subtitulo",
    "texto_lengua_senas",
    "meta_titulo_seo",
    "meta_descripcion_seo",
)


class ConfiguracionInterfazPublicaSerializer(serializers.Serializer):
    """Serializer de la configuracion visual expuesta al frontend."""

    nombre_aplicativo = serializers.CharField()
    nombre_corto = serializers.CharField()
    descripcion_aplicativo = serializers.CharField()
    texto_pie_pagina = serializers.CharField()
    texto_titulo_seccion_encuestas = serializers.CharField()
    texto_descripcion_seccion_encuestas = serializers.CharField()
    email_soporte = serializers.EmailField(allow_blank=True)
    texto_terminos_condiciones = serializers.CharField()
    texto_autorizacion_datos = serializers.CharField()
    texto_verificacion_exitosa_titulo = serializers.CharField()
    texto_verificacion_exitosa_cuerpo = serializers.CharField()
    texto_confirmacion_envio_titulo = serializers.CharField()
    texto_confirmacion_envio_subtitulo = serializers.CharField()
    meta_titulo_seo = serializers.CharField()
    meta_descripcion_seo = serializers.CharField()
    accion_lengua_senas_habilitada = serializers.BooleanField()
    url_lengua_senas = serializers.URLField(allow_blank=True)
    texto_lengua_senas = serializers.CharField()
    logo_principal = serializers.CharField(allow_null=True)
    logo_secundario = serializers.CharField(allow_null=True)
    logo_institucional = serializers.CharField(allow_null=True)
    favicon = serializers.CharField(allow_null=True)
    logo_principal_alt = serializers.CharField(allow_blank=True)
    logo_secundario_alt = serializers.CharField(allow_blank=True)
    logo_institucional_alt = serializers.CharField(allow_blank=True)
    favicon_alt = serializers.CharField(allow_blank=True)
    logos = serializers.ListField(
        child=serializers.DictField(),
        required=False,
    )
    color_primario = serializers.CharField()
    color_secundario = serializers.CharField()
    color_acento = serializers.CharField()
    flujo_formulario = serializers.DictField()

    def to_representation(
        self,
        instancia: ConfiguracionInterfaz | None,
    ) -> dict[str, Any]:
        """Serializa la configuracion activa o valores por defecto."""
        if instancia is None:
            return construir_configuracion_por_defecto()

        solicitud = self.context.get("request")
        mapa_traducciones = self.context.get("mapa_traducciones", {})
        uuid_entidad = resolver_uuid_entidad(instancia, "ConfiguracionInterfaz")
        mapa_logos = obtener_mapa_logos_interfaz(instancia)

        datos: dict[str, Any] = {
            "nombre_aplicativo": instancia.nombre_aplicativo,
            "nombre_corto": instancia.nombre_corto,
            "descripcion_aplicativo": instancia.descripcion_aplicativo,
            "texto_pie_pagina": instancia.texto_pie_pagina,
            "texto_titulo_seccion_encuestas": instancia.texto_titulo_seccion_encuestas,
            "texto_descripcion_seccion_encuestas": (
                instancia.texto_descripcion_seccion_encuestas
            ),
            "email_soporte": instancia.email_soporte,
            "texto_terminos_condiciones": instancia.texto_terminos_condiciones,
            "texto_autorizacion_datos": instancia.texto_autorizacion_datos,
            "texto_verificacion_exitosa_titulo": (
                instancia.texto_verificacion_exitosa_titulo
            ),
            "texto_verificacion_exitosa_cuerpo": (
                instancia.texto_verificacion_exitosa_cuerpo
            ),
            "texto_confirmacion_envio_titulo": instancia.texto_confirmacion_envio_titulo,
            "texto_confirmacion_envio_subtitulo": (
                instancia.texto_confirmacion_envio_subtitulo
            ),
            "meta_titulo_seo": instancia.meta_titulo_seo,
            "meta_descripcion_seo": instancia.meta_descripcion_seo,
            "accion_lengua_senas_habilitada": instancia.accion_lengua_senas_habilitada,
            "url_lengua_senas": instancia.url_lengua_senas,
            "texto_lengua_senas": instancia.texto_lengua_senas,
            "color_primario": instancia.color_primario,
            "color_secundario": instancia.color_secundario,
            "color_acento": instancia.color_acento,
        }

        for campo in CAMPOS_TEXTO_TRADUCIBLES:
            datos[campo] = aplicar_texto_traducido(
                mapa_traducciones,
                "ConfiguracionInterfaz",
                uuid_entidad,
                campo,
                str(datos.get(campo, "")),
            )

        for campo_imagen in CAMPOS_IMAGEN:
            datos[campo_imagen] = resolver_url_imagen_configuracion(
                instancia,
                campo_imagen,
                solicitud,
                mapa_logos=mapa_logos,
            )
            datos[f"{campo_imagen}_alt"] = resolver_texto_alternativo_logo(
                instancia,
                campo_imagen,
                mapa_logos=mapa_logos,
            )

        datos["logos"] = construir_lista_logos_publica(instancia, solicitud)

        if self.context.get("incluir_accesibilidad"):
            codigo_idioma = normalizar_codigo_idioma(self.context.get("idioma"))
            datos["contenido_accesible"] = construir_mapa_contenido_accesible(
                codigo_idioma=codigo_idioma,
                entidad="ConfiguracionInterfaz",
                entidad_id=str(uuid_entidad),
                campos=("nombre_aplicativo", "texto_pie_pagina"),
                solicitud=solicitud,
            )
        datos["flujo_formulario"] = construir_bloque_flujo_formulario_publico(
            interfaz=instancia,
            mapa_traducciones=mapa_traducciones,
        )
        return datos


class ConfiguracionInterfazPublicaEsquemaSerializer(serializers.Serializer):
    """Esquema de respuesta para documentacion OpenAPI."""

    nombre_aplicativo = serializers.CharField(
        default=ValoresPorDefectoInterfaz.NOMBRE_APLICATIVO,
    )
    nombre_corto = serializers.CharField(
        default=ValoresPorDefectoInterfaz.NOMBRE_CORTO,
    )
    descripcion_aplicativo = serializers.CharField(default="")
    texto_pie_pagina = serializers.CharField(default="")
    texto_titulo_seccion_encuestas = serializers.CharField(default="")
    texto_descripcion_seccion_encuestas = serializers.CharField(default="")
    email_soporte = serializers.EmailField(allow_blank=True, default="")
    texto_terminos_condiciones = serializers.CharField(default="")
    texto_autorizacion_datos = serializers.CharField(default="")
    texto_verificacion_exitosa_titulo = serializers.CharField(default="")
    texto_verificacion_exitosa_cuerpo = serializers.CharField(default="")
    texto_confirmacion_envio_titulo = serializers.CharField(default="")
    texto_confirmacion_envio_subtitulo = serializers.CharField(default="")
    meta_titulo_seo = serializers.CharField(default="")
    meta_descripcion_seo = serializers.CharField(default="")
    accion_lengua_senas_habilitada = serializers.BooleanField(default=False)
    url_lengua_senas = serializers.URLField(allow_blank=True, default="")
    texto_lengua_senas = serializers.CharField(default="")
    logo_principal = serializers.CharField(allow_null=True, default=None)
    logo_secundario = serializers.CharField(allow_null=True, default=None)
    logo_institucional = serializers.CharField(allow_null=True, default=None)
    favicon = serializers.CharField(allow_null=True, default=None)
    logo_principal_alt = serializers.CharField(allow_blank=True, default="")
    logo_secundario_alt = serializers.CharField(allow_blank=True, default="")
    logo_institucional_alt = serializers.CharField(allow_blank=True, default="")
    favicon_alt = serializers.CharField(allow_blank=True, default="")
    logos = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )
    color_primario = serializers.CharField(default="")
    color_secundario = serializers.CharField(default="")
    color_acento = serializers.CharField(default="")
    flujo_formulario = serializers.DictField(default=dict)
    contenido_accesible = serializers.DictField(
        child=ContenidoAccesibleSerializer(),
        required=False,
    )
