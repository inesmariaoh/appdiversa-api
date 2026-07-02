"""
Servicios del repositorio documental transversal.
"""

import hashlib
import uuid
from datetime import datetime
from typing import Any
from uuid import UUID

from django.db import transaction

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import crear_snapshot_modelo, registrar_auditoria
from aplicaciones.comun.utilidades_media import construir_url_absoluta_desde_solicitud
from aplicaciones.archivos.constantes import (
    EstadoArchivo,
    OrigenArchivo,
    PREFIJO_RUTA_REPOSITORIO,
)
from aplicaciones.archivos.excepciones import ArchivoNoEncontradoError
from aplicaciones.archivos.models import ArchivoRepositorio
from aplicaciones.archivos.selectores import (
    obtener_archivo_por_uuid,
    obtener_archivo_por_uuid_sin_estado,
)
from aplicaciones.archivos.storage import obtener_storage_backend
from aplicaciones.archivos.validadores import validar_archivo


def calcular_checksum(contenido: bytes) -> str:
    """Calcula el checksum SHA-256 de un contenido binario."""
    return hashlib.sha256(contenido).hexdigest()


def _construir_ruta_relativa(uuid_archivo: UUID, extension: str) -> str:
    """Construye la ruta relativa de almacenamiento para un archivo."""
    ahora = datetime.now()
    nombre_fisico = f"{uuid_archivo}.{extension}"
    return (
        f"{PREFIJO_RUTA_REPOSITORIO}/"
        f"{ahora.year}/{ahora.month:02d}/"
        f"{uuid_archivo}/{nombre_fisico}"
    )


def construir_url(
    archivo: ArchivoRepositorio,
    solicitud: Any = None,
) -> str | None:
    """Construye la URL absoluta o relativa de un archivo del repositorio."""
    if archivo.estado != EstadoArchivo.ACTIVO or archivo.esta_eliminado:
        return None

    backend = obtener_storage_backend()
    url_relativa = archivo.url_publica or backend.obtener_url(archivo.ruta_relativa)
    if solicitud is None:
        return url_relativa
    return construir_url_absoluta_desde_solicitud(url_relativa, solicitud)


def obtener_archivo(uuid_archivo: UUID) -> ArchivoRepositorio:
    """Retorna un archivo activo del repositorio o lanza error funcional."""
    archivo = obtener_archivo_por_uuid(uuid_archivo)
    if archivo is None:
        raise ArchivoNoEncontradoError()
    return archivo


def guardar_archivo(
    contenido: bytes,
    nombre_original: str,
    mime_type: str,
    tipo_archivo: str,
    origen: str,
    descripcion: str = "",
    es_publico: bool = False,
    metadatos: dict[str, Any] | None = None,
    usuario_keycloak: str = "",
    uuid_sesion: UUID | None = None,
) -> ArchivoRepositorio:
    """Valida, almacena y registra un archivo en el repositorio documental."""
    tamano_bytes = len(contenido)
    extension = validar_archivo(
        nombre_original,
        mime_type,
        tamano_bytes,
        tipo_archivo,
    )
    checksum = calcular_checksum(contenido)
    uuid_archivo = uuid.uuid4()
    ruta_relativa = _construir_ruta_relativa(uuid_archivo, extension)
    nombre_fisico = f"{uuid_archivo}.{extension}"

    backend = obtener_storage_backend()
    backend.guardar(ruta_relativa, contenido)
    url_publica = backend.obtener_url(ruta_relativa)

    with transaction.atomic():
        archivo = ArchivoRepositorio.objects.create(
            uuid=uuid_archivo,
            nombre_original=nombre_original.strip(),
            nombre_fisico=nombre_fisico,
            extension=extension,
            mime_type=mime_type.split(";")[0].strip().lower(),
            tamano_bytes=tamano_bytes,
            checksum_sha256=checksum,
            tipo_archivo=tipo_archivo,
            ruta_relativa=ruta_relativa,
            url_publica=url_publica,
            es_publico=es_publico,
            origen=origen,
            estado=EstadoArchivo.ACTIVO,
            descripcion=descripcion,
            metadatos=metadatos or {},
            usuario_keycloak=usuario_keycloak,
            uuid_sesion=uuid_sesion,
        )
        registrar_auditoria(
            entidad=ArchivoRepositorio.__name__,
            entidad_id=str(archivo.pk),
            accion=AccionAuditoria.CREAR,
            valor_nuevo=crear_snapshot_modelo(archivo),
        )

    return archivo


def eliminar_archivo(uuid_archivo: UUID) -> ArchivoRepositorio:
    """Elimina logicamente un archivo del repositorio."""
    archivo = obtener_archivo_por_uuid_sin_estado(uuid_archivo)
    if archivo is None:
        raise ArchivoNoEncontradoError()

    valor_anterior = crear_snapshot_modelo(archivo)
    with transaction.atomic():
        archivo.estado = EstadoArchivo.ELIMINADO
        archivo.eliminar_logicamente()
        archivo.save(
            update_fields=[
                "estado",
                "esta_eliminado",
                "fecha_eliminacion",
                "fecha_modificacion",
            ],
        )
        registrar_auditoria(
            entidad=ArchivoRepositorio.__name__,
            entidad_id=str(archivo.pk),
            accion=AccionAuditoria.ELIMINAR,
            valor_anterior=valor_anterior,
            valor_nuevo=crear_snapshot_modelo(archivo),
        )

    return archivo


def leer_contenido_archivo(archivo: ArchivoRepositorio) -> bytes:
    """Lee el contenido binario de un archivo activo del repositorio."""
    if archivo.estado != EstadoArchivo.ACTIVO or archivo.esta_eliminado:
        raise ArchivoNoEncontradoError()

    backend = obtener_storage_backend()
    if not backend.existe(archivo.ruta_relativa):
        raise ArchivoNoEncontradoError()
    return backend.leer(archivo.ruta_relativa)


def preparar_asociacion_archivo_respuesta(uuid_archivo: UUID) -> ArchivoRepositorio | None:
    """Prepara la asociacion futura de un archivo del repositorio a una respuesta."""
    return obtener_archivo_por_uuid(uuid_archivo)
