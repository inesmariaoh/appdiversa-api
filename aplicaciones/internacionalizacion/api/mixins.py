"""
Mixins para serializers con soporte de traduccion.
"""

from typing import Any

from django.db import models

from aplicaciones.internacionalizacion.servicios import (
    aplicar_texto_traducido,
    construir_mapa_contenido_accesible,
    normalizar_codigo_idioma,
    resolver_uuid_entidad,
)


class TraduccionSerializerMixin:
    """Mixin que aplica traducciones desde un mapa precargado en el contexto."""

    nombre_entidad: str = ""

    def obtener_texto_traducido(
        self,
        instancia: models.Model,
        campo: str,
        valor: str,
    ) -> str:
        """Retorna el valor traducido de un campo o el original."""
        mapa_traducciones = self.context.get("mapa_traducciones")
        if not mapa_traducciones:
            return valor if valor is not None else ""

        uuid_entidad = resolver_uuid_entidad(instancia, self.nombre_entidad)
        return aplicar_texto_traducido(
            mapa_traducciones,
            self.nombre_entidad,
            uuid_entidad,
            campo,
            valor,
        )

    def aplicar_traducciones_campos(
        self,
        instancia: models.Model,
        datos: dict[str, Any],
        campos: tuple[str, ...],
    ) -> dict[str, Any]:
        """Aplica traducciones a un conjunto de campos del diccionario serializado."""
        if not self.context.get("mapa_traducciones"):
            return datos

        for campo in campos:
            if campo in datos:
                datos[campo] = self.obtener_texto_traducido(
                    instancia,
                    campo,
                    str(datos[campo]),
                )
        return datos

    def construir_contenido_accesible_campos(
        self,
        instancia: models.Model,
        campos: tuple[str, ...],
    ) -> dict[str, dict[str, Any]]:
        """Construye contenido accesible para los campos indicados de la entidad."""
        codigo_idioma = normalizar_codigo_idioma(self.context.get("idioma"))
        uuid_entidad = resolver_uuid_entidad(instancia, self.nombre_entidad)
        return construir_mapa_contenido_accesible(
            codigo_idioma=codigo_idioma,
            entidad=self.nombre_entidad,
            entidad_id=str(uuid_entidad),
            campos=campos,
            solicitud=self.context.get("request"),
        )
