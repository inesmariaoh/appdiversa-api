"""
Selectores de consulta del repositorio documental.
"""

from uuid import UUID

from aplicaciones.archivos.constantes import EstadoArchivo
from aplicaciones.archivos.models import ArchivoRepositorio


def obtener_archivo_por_uuid(uuid_archivo: UUID) -> ArchivoRepositorio | None:
    """Retorna un archivo activo del repositorio por su UUID."""
    return ArchivoRepositorio.objects.filter(
        uuid=uuid_archivo,
        estado=EstadoArchivo.ACTIVO,
        esta_eliminado=False,
    ).first()


def obtener_archivo_por_uuid_sin_estado(uuid_archivo: UUID) -> ArchivoRepositorio | None:
    """Retorna un archivo del repositorio por UUID sin filtrar por estado."""
    return ArchivoRepositorio.objects.filter(uuid=uuid_archivo).first()
