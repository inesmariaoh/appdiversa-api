"""
Selectores de consulta del motor de exportaciones.
"""

from uuid import UUID

from aplicaciones.exportaciones.models import Exportacion


def obtener_exportacion_por_uuid(uuid_exportacion: UUID) -> Exportacion | None:
    """Retorna una exportacion activa por su UUID."""
    return Exportacion.objects.filter(
        uuid=uuid_exportacion,
        esta_eliminado=False,
    ).select_related("archivo").first()
