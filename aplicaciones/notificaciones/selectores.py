"""
Selectores de consulta del motor de notificaciones.
"""

from uuid import UUID

from aplicaciones.notificaciones.models import Notificacion, PlantillaNotificacion


def obtener_plantilla_por_codigo(codigo: str) -> PlantillaNotificacion | None:
    """Retorna una plantilla activa por su codigo."""
    return PlantillaNotificacion.objects.filter(
        codigo=codigo,
        esta_activa=True,
        esta_eliminado=False,
    ).first()


def obtener_notificacion_por_uuid(uuid_notificacion: UUID) -> Notificacion | None:
    """Retorna una notificacion activa por su UUID."""
    return Notificacion.objects.filter(
        uuid=uuid_notificacion,
        esta_eliminado=False,
    ).select_related("plantilla").first()


def listar_notificaciones_registros() -> list[Notificacion]:
    """Lista notificaciones activas ordenadas por fecha de creacion."""
    return list(
        Notificacion.objects.filter(esta_eliminado=False)
        .select_related("plantilla")
        .order_by("-fecha_creacion"),
    )
