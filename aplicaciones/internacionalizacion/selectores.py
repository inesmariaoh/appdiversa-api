"""
Selectores de consulta para internacionalizacion.
"""

from uuid import UUID

from django.db.models import QuerySet

from aplicaciones.internacionalizacion.constantes import IDIOMA_PREDETERMINADO_CODIGO
from aplicaciones.internacionalizacion.models import Idioma, TraduccionContenido


def obtener_idioma_por_codigo(codigo_iso: str) -> Idioma | None:
    """Retorna un idioma activo por su codigo ISO o None si no existe."""
    return Idioma.objects.filter(
        codigo_iso=codigo_iso,
        esta_activo=True,
        esta_eliminado=False,
    ).first()


def obtener_idioma_predeterminado() -> Idioma | None:
    """Retorna el idioma predeterminado activo o None."""
    predeterminado = Idioma.objects.filter(
        es_predeterminado=True,
        esta_activo=True,
        esta_eliminado=False,
    ).first()
    if predeterminado is not None:
        return predeterminado
    return obtener_idioma_por_codigo(IDIOMA_PREDETERMINADO_CODIGO)


def obtener_traduccion_registro(
    codigo_idioma: str,
    entidad: str,
    entidad_uuid: UUID,
    campo: str,
) -> TraduccionContenido | None:
    """Retorna una traduccion activa para el idioma y contenido solicitado."""
    return TraduccionContenido.objects.filter(
        idioma__codigo_iso=codigo_idioma,
        idioma__esta_activo=True,
        idioma__esta_eliminado=False,
        entidad=entidad,
        entidad_uuid=entidad_uuid,
        campo=campo,
        esta_eliminado=False,
    ).select_related("idioma").first()


def listar_traducciones_registros(
    codigo_idioma: str | None = None,
    entidad: str | None = None,
    entidad_uuid: UUID | None = None,
    campo: str | None = None,
) -> QuerySet[TraduccionContenido]:
    """Lista traducciones activas con filtros opcionales."""
    consulta = TraduccionContenido.objects.filter(
        esta_eliminado=False,
    ).select_related("idioma")

    if codigo_idioma:
        consulta = consulta.filter(idioma__codigo_iso=codigo_idioma)

    if entidad:
        consulta = consulta.filter(entidad=entidad)

    if entidad_uuid is not None:
        consulta = consulta.filter(entidad_uuid=entidad_uuid)

    if campo:
        consulta = consulta.filter(campo=campo)

    return consulta.order_by("entidad", "campo")


def listar_traducciones_por_entidades(
    codigo_idioma: str,
    entidad_uuids: list[UUID],
    entidades: list[str] | None = None,
) -> QuerySet[TraduccionContenido]:
    """Lista traducciones activas para multiples entidades en un idioma."""
    if not entidad_uuids:
        return TraduccionContenido.objects.none()

    consulta = TraduccionContenido.objects.filter(
        idioma__codigo_iso=codigo_idioma,
        idioma__esta_activo=True,
        idioma__esta_eliminado=False,
        entidad_uuid__in=entidad_uuids,
        esta_eliminado=False,
    )

    if entidades:
        consulta = consulta.filter(entidad__in=entidades)

    return consulta.select_related("idioma")


def obtener_traduccion_contenido_accesible(
    entidad: str,
    entidad_id: str,
    campo: str,
    codigo_idioma: str | None,
) -> TraduccionContenido | None:
    """Retorna la traduccion activa con contenido accesible o None."""
    if not codigo_idioma:
        return None

    try:
        entidad_uuid = UUID(str(entidad_id))
    except (ValueError, AttributeError, TypeError):
        return None

    return TraduccionContenido.objects.filter(
        idioma__codigo_iso=codigo_idioma,
        idioma__esta_activo=True,
        idioma__esta_eliminado=False,
        entidad=entidad,
        entidad_uuid=entidad_uuid,
        campo=campo,
        esta_activa=True,
        esta_eliminado=False,
    ).select_related(
        "idioma",
        "repositorio_audio",
        "repositorio_video",
        "repositorio_imagen",
        "repositorio_lengua_senas",
    ).first()
