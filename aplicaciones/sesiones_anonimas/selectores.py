"""
Selectores de consulta para sesiones anonimas.
"""

from uuid import UUID

from django.contrib.auth.models import AbstractBaseUser
from django.db.models import QuerySet

from aplicaciones.sesiones_anonimas.models import SesionAnonima


def obtener_sesion_por_uuid(uuid_sesion: UUID) -> SesionAnonima | None:
    """Retorna una sesion anonima por su uuid."""
    return (
        SesionAnonima.objects.select_related(
            "formulario",
            "version_formulario",
        )
        .filter(uuid_sesion=uuid_sesion)
        .first()
    )


def existe_sesion(uuid_sesion: UUID) -> bool:
    """Indica si existe una sesion con el uuid proporcionado."""
    return SesionAnonima.objects.filter(uuid_sesion=uuid_sesion).exists()


def listar_sesiones_vinculadas_usuario(
    usuario: AbstractBaseUser,
) -> QuerySet[SesionAnonima]:
    """Retorna sesiones anonimas asociadas al usuario autenticado."""
    return (
        SesionAnonima.objects.select_related("formulario", "version_formulario")
        .filter(usuario=usuario, esta_eliminado=False)
        .order_by("-fecha_ultima_actividad")
    )
