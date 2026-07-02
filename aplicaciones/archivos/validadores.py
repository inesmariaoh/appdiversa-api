"""
Validadores de seguridad para archivos del repositorio documental.
"""

import re

from aplicaciones.archivos.constantes import (
    EXTENSIONES_PROHIBIDAS,
    MIME_PERMITIDOS_POR_TIPO,
    TAMANO_MAXIMO_POR_TIPO,
    TipoArchivo,
    MensajesArchivoApi,
)
from aplicaciones.archivos.excepciones import ArchivoValidacionError

PATRON_NOMBRE_SEGURO = re.compile(r"^[a-zA-Z0-9._\- ]+$")


def obtener_extension(nombre_archivo: str) -> str:
    """Extrae la extension de un nombre de archivo en minusculas."""
    if "." not in nombre_archivo:
        return ""
    return nombre_archivo.rsplit(".", 1)[-1].lower()


def validar_nombre_archivo(nombre_archivo: str) -> None:
    """Valida que el nombre del archivo sea seguro."""
    if not nombre_archivo or not nombre_archivo.strip():
        raise ArchivoValidacionError(MensajesArchivoApi.NOMBRE_NO_PERMITIDO)
    if not PATRON_NOMBRE_SEGURO.match(nombre_archivo.strip()):
        raise ArchivoValidacionError(MensajesArchivoApi.NOMBRE_NO_PERMITIDO)


def validar_extension(nombre_archivo: str) -> str:
    """Valida la extension y retorna su valor normalizado."""
    extension = obtener_extension(nombre_archivo)
    if not extension:
        raise ArchivoValidacionError(MensajesArchivoApi.EXTENSION_NO_PERMITIDA)
    if extension in EXTENSIONES_PROHIBIDAS:
        raise ArchivoValidacionError(MensajesArchivoApi.EXTENSION_NO_PERMITIDA)
    return extension


def validar_mime(mime_type: str, tipo_archivo: str) -> None:
    """Valida el MIME del archivo segun el tipo declarado."""
    mime_normalizado = mime_type.split(";")[0].strip().lower()
    permitidos = MIME_PERMITIDOS_POR_TIPO.get(tipo_archivo, frozenset())
    if mime_normalizado not in permitidos:
        raise ArchivoValidacionError(MensajesArchivoApi.MIME_NO_PERMITIDO)


def validar_tamano(tamano_bytes: int, tipo_archivo: str) -> None:
    """Valida que el tamano no supere el limite del tipo de archivo."""
    maximo = TAMANO_MAXIMO_POR_TIPO.get(
        tipo_archivo,
        TAMANO_MAXIMO_POR_TIPO[TipoArchivo.ARCHIVO_GENERAL],
    )
    if tamano_bytes > maximo:
        raise ArchivoValidacionError(MensajesArchivoApi.TAMANO_NO_PERMITIDO)


def validar_checksum(checksum: str) -> None:
    """Valida el formato del checksum SHA-256."""
    if not checksum or len(checksum) != 64:
        raise ArchivoValidacionError(MensajesArchivoApi.CHECKSUM_INVALIDO)
    if not all(caracter in "0123456789abcdef" for caracter in checksum.lower()):
        raise ArchivoValidacionError(MensajesArchivoApi.CHECKSUM_INVALIDO)


def validar_archivo(
    nombre_archivo: str,
    mime_type: str,
    tamano_bytes: int,
    tipo_archivo: str,
) -> str:
    """Ejecuta todas las validaciones de un archivo y retorna la extension."""
    validar_nombre_archivo(nombre_archivo)
    extension = validar_extension(nombre_archivo)
    validar_mime(mime_type, tipo_archivo)
    validar_tamano(tamano_bytes, tipo_archivo)
    return extension
