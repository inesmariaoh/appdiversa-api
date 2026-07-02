"""
Sincroniza recursos de imagen alojados en Cloudinary con el repositorio documental.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from django.db import transaction

from aplicaciones.archivos.constantes import (
    EstadoArchivo,
    OrigenArchivo,
    TipoArchivo,
)
from aplicaciones.archivos.models import ArchivoRepositorio
from aplicaciones.contenidos.constantes import CodigosLogoInterfaz
from aplicaciones.contenidos.models import ConfiguracionInterfaz, LogoInterfaz
from aplicaciones.formularios.models import Formulario

METADATO_CODIGO_RECURSO = "codigo_recurso"
METADATO_PROVEEDOR = "proveedor"
PROVEEDOR_CLOUDINARY = "cloudinary"
PATRONES_PORTADA_FORMULARIO = {
    "image_ecu_disponible": "image_ecu_disponible",
    "image_proxma_enc": "image_proxma_enc",
}


@dataclass(frozen=True)
class RecursoImagenExterna:
    """Describe un recurso visual externo parametrizable."""

    url: str
    nombre_original: str
    extension: str
    mime_type: str


RECURSOS_IMAGENES_CLOUDINARY: dict[str, RecursoImagenExterna] = {
    "image_ecu_disponible": RecursoImagenExterna(
        url=(
            "https://res.cloudinary.com/t46o5s2e/image/upload/"
            "v1782969030/image_ecu_disponible_afimrf.png"
        ),
        nombre_original="image_ecu_disponible.png",
        extension="png",
        mime_type="image/png",
    ),
    "image_proxma_enc": RecursoImagenExterna(
        url=(
            "https://res.cloudinary.com/t46o5s2e/image/upload/"
            "v1782969030/image_proxma_enc_bxrsql.png"
        ),
        nombre_original="image_proxma_enc.png",
        extension="png",
        mime_type="image/png",
    ),
    "logos_dane_sen": RecursoImagenExterna(
        url=(
            "https://res.cloudinary.com/t46o5s2e/image/upload/"
            "v1782968982/logos_dane_sen_kidtd8.png"
        ),
        nombre_original="logos_dane_sen.png",
        extension="png",
        mime_type="image/png",
    ),
    "logo_propuesta_2": RecursoImagenExterna(
        url=(
            "https://res.cloudinary.com/t46o5s2e/image/upload/"
            "v1782969016/Propuesta_2_oeijeq.jpg"
        ),
        nombre_original="Propuesta_2.jpg",
        extension="jpg",
        mime_type="image/jpeg",
    ),
}

MAPEO_LOGO_RECURSO = {
    CodigosLogoInterfaz.INSTITUCIONAL: "logos_dane_sen",
    CodigosLogoInterfaz.PRINCIPAL: "logo_propuesta_2",
}


def _calcular_checksum(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def _obtener_o_crear_archivo(codigo_recurso: str, recurso: RecursoImagenExterna) -> ArchivoRepositorio:
    archivo = ArchivoRepositorio.objects.filter(
        metadatos__codigo_recurso=codigo_recurso,
        esta_eliminado=False,
    ).first()
    if archivo is None:
        uuid_archivo = uuid.uuid4()
        archivo = ArchivoRepositorio(
            uuid=uuid_archivo,
            nombre_fisico=f"{uuid_archivo}.{recurso.extension}",
            ruta_relativa=f"externo/cloudinary/{codigo_recurso}.{recurso.extension}",
        )

    archivo.nombre_original = recurso.nombre_original
    archivo.extension = recurso.extension
    archivo.mime_type = recurso.mime_type
    archivo.tamano_bytes = 0
    archivo.checksum_sha256 = _calcular_checksum(recurso.url)
    archivo.tipo_archivo = TipoArchivo.IMAGEN
    archivo.url_publica = recurso.url
    archivo.es_publico = True
    archivo.origen = OrigenArchivo.CONFIGURACION
    archivo.estado = EstadoArchivo.ACTIVO
    archivo.descripcion = f"Recurso Cloudinary: {codigo_recurso}"
    archivo.metadatos = {
        METADATO_CODIGO_RECURSO: codigo_recurso,
        METADATO_PROVEEDOR: PROVEEDOR_CLOUDINARY,
    }
    archivo.save()
    return archivo


def _vincular_portadas_formulario(archivos: dict[str, ArchivoRepositorio]) -> None:
    for codigo_recurso, patron in PATRONES_PORTADA_FORMULARIO.items():
        archivo = archivos[codigo_recurso]
        formularios = Formulario.objects.filter(
            imagen_portada__icontains=patron,
            esta_eliminado=False,
        )
        formularios.update(imagen_portada_repositorio=archivo)


def _vincular_logos_interfaz(archivos: dict[str, ArchivoRepositorio]) -> None:
    for codigo_logo, codigo_recurso in MAPEO_LOGO_RECURSO.items():
        archivo = archivos[codigo_recurso]
        logos = LogoInterfaz.objects.filter(
            codigo=codigo_logo,
            esta_eliminado=False,
        )
        logos.update(archivo_repositorio=archivo)


def _vincular_configuracion_interfaz(archivos: dict[str, ArchivoRepositorio]) -> None:
    configuraciones = ConfiguracionInterfaz.objects.filter(esta_eliminado=False)
    archivo_institucional = archivos["logos_dane_sen"]
    archivo_principal = archivos["logo_propuesta_2"]
    configuraciones.update(
        logo_institucional_repositorio=archivo_institucional,
        logo_principal_repositorio=archivo_principal,
    )


@transaction.atomic
def sincronizar_recursos_imagenes_cloudinary() -> None:
    """Crea o actualiza archivos externos y sus relaciones parametrizadas."""
    archivos = {
        codigo: _obtener_o_crear_archivo(codigo, recurso)
        for codigo, recurso in RECURSOS_IMAGENES_CLOUDINARY.items()
    }
    _vincular_portadas_formulario(archivos)
    _vincular_logos_interfaz(archivos)
    _vincular_configuracion_interfaz(archivos)
