"""
Selectores de consulta para sincronizacion offline.
"""

from uuid import UUID

from django.db.models import QuerySet

from aplicaciones.sincronizacion.models import ConflictoSincronizacion, OperacionSincronizacion


def obtener_operacion_por_uuid_local(
    uuid_sesion: UUID,
    uuid_local: UUID,
) -> OperacionSincronizacion | None:
    """Retorna la ultima operacion registrada para un uuid_local en una sesion."""
    return (
        OperacionSincronizacion.objects.filter(
            uuid_sesion=uuid_sesion,
            uuid_local=uuid_local,
        )
        .order_by("-fecha_servidor")
        .first()
    )


def listar_conflictos_por_uuid_local(uuid_local: UUID) -> QuerySet[ConflictoSincronizacion]:
    """Retorna conflictos asociados a un identificador local."""
    return ConflictoSincronizacion.objects.filter(uuid_local=uuid_local).order_by("-fecha")
