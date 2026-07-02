"""
Servicios de internacionalizacion de contenido parametrizable.
"""

import uuid
from typing import Any
from uuid import UUID

from django.db import models, transaction

from aplicaciones.internacionalizacion.constantes import (
    IDIOMA_PREDETERMINADO_CODIGO,
    NAMESPACE_UUID_ENTIDAD,
)
from aplicaciones.internacionalizacion.models import Idioma, TraduccionContenido
from aplicaciones.internacionalizacion.selectores import (
    listar_traducciones_por_entidades,
    listar_traducciones_registros,
    obtener_idioma_por_codigo,
    obtener_idioma_predeterminado,
    obtener_traduccion_contenido_accesible,
    obtener_traduccion_registro,
)

CAMPOS_ARCHIVO_ACCESIBLE = (
    "archivo_audio",
    "archivo_video",
    "archivo_imagen",
    "archivo_lengua_senas",
)

MAPEO_CAMPO_REPOSITORIO = {
    "archivo_audio": "repositorio_audio",
    "archivo_video": "repositorio_video",
    "archivo_imagen": "repositorio_imagen",
    "archivo_lengua_senas": "repositorio_lengua_senas",
}


def construir_contenido_accesible_vacio() -> dict[str, Any]:
    """Retorna la estructura vacia de contenido accesible."""
    return {
        "lectura_facil": "",
        "texto_alternativo": "",
        "transcripcion": "",
        "archivo_audio": None,
        "archivo_video": None,
        "archivo_imagen": None,
        "archivo_lengua_senas": None,
        "metadatos": {},
    }


def construir_url_archivo_campo(
    instancia: TraduccionContenido,
    campo: str,
    solicitud: Any,
) -> str | None:
    """Construye la URL absoluta de un archivo accesible si existe en repositorio."""
    from aplicaciones.archivos.servicios import construir_url

    nombre_repositorio = MAPEO_CAMPO_REPOSITORIO.get(campo)
    if nombre_repositorio is None:
        return None

    archivo_repositorio = getattr(instancia, nombre_repositorio, None)
    if archivo_repositorio is None:
        return None

    return construir_url(archivo_repositorio, solicitud)


def _construir_contenido_accesible_desde_traduccion(
    traduccion: TraduccionContenido,
    solicitud: Any,
) -> dict[str, Any]:
    """Construye el diccionario de contenido accesible desde una traduccion."""
    contenido = construir_contenido_accesible_vacio()
    contenido["lectura_facil"] = traduccion.lectura_facil or ""
    contenido["texto_alternativo"] = traduccion.texto_alternativo or ""
    contenido["transcripcion"] = traduccion.transcripcion or ""
    for campo_archivo in CAMPOS_ARCHIVO_ACCESIBLE:
        contenido[campo_archivo] = construir_url_archivo_campo(
            traduccion,
            campo_archivo,
            solicitud,
        )
    metadatos = traduccion.metadatos
    contenido["metadatos"] = metadatos if isinstance(metadatos, dict) else {}
    return contenido


def obtener_contenido_accesible(
    entidad: str,
    entidad_id: str,
    campo: str,
    codigo_idioma: str | None = None,
    request: Any = None,
) -> dict[str, Any]:
    """Retorna contenido accesible multimodal para una traduccion o valores vacios."""
    codigo_normalizado = normalizar_codigo_idioma(codigo_idioma)
    if codigo_normalizado is None:
        return construir_contenido_accesible_vacio()

    traduccion = obtener_traduccion_contenido_accesible(
        entidad=entidad,
        entidad_id=entidad_id,
        campo=campo,
        codigo_idioma=codigo_normalizado,
    )
    if traduccion is None:
        return construir_contenido_accesible_vacio()

    return _construir_contenido_accesible_desde_traduccion(traduccion, request)


def construir_mapa_contenido_accesible(
    codigo_idioma: str | None,
    entidad: str,
    entidad_id: str,
    campos: tuple[str, ...],
    solicitud: Any = None,
) -> dict[str, dict[str, Any]]:
    """Construye contenido accesible para multiples campos de una entidad."""
    mapa: dict[str, dict[str, Any]] = {}
    for campo in campos:
        mapa[campo] = obtener_contenido_accesible(
            entidad=entidad,
            entidad_id=entidad_id,
            campo=campo,
            codigo_idioma=codigo_idioma,
            request=solicitud,
        )
    return mapa


def resolver_uuid_entidad(instancia: models.Model, nombre_entidad: str) -> UUID:
    """Resuelve el UUID de referencia para traducciones de una instancia."""
    uuid_nativo = getattr(instancia, "uuid", None)
    if uuid_nativo is not None:
        return uuid_nativo
    return uuid.uuid5(NAMESPACE_UUID_ENTIDAD, f"{nombre_entidad}:{instancia.pk}")


def normalizar_codigo_idioma(codigo_idioma: str | None) -> str | None:
    """Normaliza el codigo de idioma recibido en solicitudes publicas."""
    if codigo_idioma is None or not codigo_idioma.strip():
        return None
    return codigo_idioma.strip().lower()


def requiere_traduccion(codigo_idioma: str | None) -> bool:
    """Indica si se debe aplicar traduccion para el codigo de idioma."""
    codigo_normalizado = normalizar_codigo_idioma(codigo_idioma)
    if codigo_normalizado is None:
        return False

    predeterminado = obtener_idioma_predeterminado()
    codigo_predeterminado = (
        predeterminado.codigo_iso
        if predeterminado is not None
        else IDIOMA_PREDETERMINADO_CODIGO
    )
    return codigo_normalizado != codigo_predeterminado.lower()


def obtener_traduccion(
    codigo_idioma: str,
    entidad: str,
    entidad_uuid: UUID,
    campo: str,
) -> TraduccionContenido | None:
    """Retorna la traduccion activa para un contenido especifico."""
    return obtener_traduccion_registro(
        codigo_idioma=codigo_idioma,
        entidad=entidad,
        entidad_uuid=entidad_uuid,
        campo=campo,
    )


def listar_traducciones(
    codigo_idioma: str | None = None,
    entidad: str | None = None,
    entidad_uuid: UUID | None = None,
    campo: str | None = None,
) -> list[TraduccionContenido]:
    """Lista traducciones activas segun filtros opcionales."""
    return list(
        listar_traducciones_registros(
            codigo_idioma=codigo_idioma,
            entidad=entidad,
            entidad_uuid=entidad_uuid,
            campo=campo,
        ),
    )


def guardar_traduccion(
    codigo_idioma: str,
    entidad: str,
    entidad_uuid: UUID,
    campo: str,
    valor_traducido: str,
) -> TraduccionContenido:
    """Crea o actualiza una traduccion de contenido."""
    idioma = obtener_idioma_por_codigo(codigo_idioma)
    if idioma is None:
        raise ValueError("El idioma solicitado no existe o no está activo.")

    with transaction.atomic():
        traduccion = TraduccionContenido.todos.filter(
            idioma=idioma,
            entidad=entidad,
            entidad_uuid=entidad_uuid,
            campo=campo,
        ).first()

        if traduccion is None:
            traduccion = TraduccionContenido(
                idioma=idioma,
                entidad=entidad,
                entidad_uuid=entidad_uuid,
                campo=campo,
            )

        traduccion.valor_traducido = valor_traducido
        traduccion.esta_eliminado = False
        traduccion.save()

    return traduccion


def obtener_texto(
    codigo_idioma: str | None,
    entidad: str,
    entidad_uuid: UUID,
    campo: str,
    texto_original: str,
) -> str:
    """Retorna el texto traducido o el original si no existe traduccion."""
    valor_original = texto_original if texto_original is not None else ""
    codigo_normalizado = normalizar_codigo_idioma(codigo_idioma)

    if not requiere_traduccion(codigo_normalizado):
        return valor_original

    traduccion = obtener_traduccion(
        codigo_idioma=codigo_normalizado,
        entidad=entidad,
        entidad_uuid=entidad_uuid,
        campo=campo,
    )
    if traduccion is not None and traduccion.valor_traducido:
        return traduccion.valor_traducido
    return valor_original


def construir_mapa_traducciones(
    codigo_idioma: str | None,
    entidad_uuids: list[UUID],
    entidades: list[str] | None = None,
) -> dict[tuple[str, UUID, str], str]:
    """Construye un mapa de traducciones para aplicacion masiva en serializers."""
    codigo_normalizado = normalizar_codigo_idioma(codigo_idioma)
    if not requiere_traduccion(codigo_normalizado) or not entidad_uuids:
        return {}

    traducciones = listar_traducciones_por_entidades(
        codigo_idioma=codigo_normalizado,
        entidad_uuids=entidad_uuids,
        entidades=entidades,
    )

    mapa: dict[tuple[str, UUID, str], str] = {}
    for traduccion in traducciones.iterator():
        clave = (
            traduccion.entidad,
            traduccion.entidad_uuid,
            traduccion.campo,
        )
        mapa[clave] = traduccion.valor_traducido
    return mapa


def aplicar_texto_traducido(
    mapa_traducciones: dict[tuple[str, UUID, str], str],
    entidad: str,
    entidad_uuid: UUID,
    campo: str,
    texto_original: str,
) -> str:
    """Aplica traduccion desde un mapa precargado o retorna el texto original."""
    valor_original = texto_original if texto_original is not None else ""
    clave = (entidad, entidad_uuid, campo)
    traducido = mapa_traducciones.get(clave)
    if traducido:
        return traducido
    return valor_original


def recolectar_uuids_estructura_formulario(
    estructura: object,
) -> list[UUID]:
    """Recolecta UUIDs de entidades traducibles en una estructura de formulario."""
    formulario = estructura.formulario
    version = estructura.version
    uuids: list[UUID] = [resolver_uuid_entidad(formulario, "Formulario")]

    textos = getattr(version, "textos_activos", version.textos.all())
    for texto in textos:
        uuids.append(resolver_uuid_entidad(texto, "TextoFormulario"))

    secciones = getattr(version, "secciones_activas", version.secciones.all())
    for seccion in secciones:
        uuids.append(resolver_uuid_entidad(seccion, "SeccionFormulario"))
        for pregunta in seccion.preguntas.all():
            uuids.append(resolver_uuid_entidad(pregunta, "Pregunta"))
            if pregunta.catalogo_asociado_id is not None:
                uuids.append(
                    resolver_uuid_entidad(
                        pregunta.catalogo_asociado,
                        "Catalogo",
                    ),
                )
            for opcion in pregunta.opciones.all():
                uuids.append(resolver_uuid_entidad(opcion, "OpcionRespuesta"))
            for regla in pregunta.reglas_origen.all():
                uuids.append(resolver_uuid_entidad(regla, "ReglaPregunta"))

    return uuids
