"""
Selectores de consulta para sincronizacion offline.
"""

from uuid import UUID

from django.db.models import QuerySet

from aplicaciones.sincronizacion.constantes import FiltrosConflicto
from aplicaciones.sincronizacion.models import ConflictoSincronizacion, OperacionSincronizacion

_VALOR_RESUELTO_VERDADERO = ("true", "1", "si", "sí")
_VALOR_RESUELTO_FALSO = ("false", "0", "no")


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


def obtener_conflicto_por_uuid(conflicto_uuid: UUID) -> ConflictoSincronizacion | None:
    """Retorna un conflicto por su identificador publico."""
    return (
        ConflictoSincronizacion.objects.select_related("respuesta", "respuesta__pregunta")
        .filter(uuid=conflicto_uuid)
        .first()
    )


def _aplicar_filtro_resuelto(
    consulta: QuerySet[ConflictoSincronizacion],
    valor_resuelto: str,
) -> QuerySet[ConflictoSincronizacion]:
    """Filtra conflictos por estado resuelto o pendiente."""
    valor = valor_resuelto.strip().lower()
    if valor in _VALOR_RESUELTO_VERDADERO:
        return consulta.exclude(resolucion="")
    if valor in _VALOR_RESUELTO_FALSO:
        return consulta.filter(resolucion="")
    return consulta


def listar_conflictos(filtros: dict[str, str]) -> QuerySet[ConflictoSincronizacion]:
    """Lista conflictos aplicando filtros opcionales de tipo, resolucion y estado."""
    consulta = ConflictoSincronizacion.objects.select_related("respuesta").all()

    tipo_conflicto = filtros.get(FiltrosConflicto.TIPO_CONFLICTO)
    if tipo_conflicto:
        consulta = consulta.filter(tipo_conflicto=tipo_conflicto)

    resolucion = filtros.get(FiltrosConflicto.RESOLUCION)
    if resolucion:
        consulta = consulta.filter(resolucion=resolucion)

    uuid_local = filtros.get(FiltrosConflicto.UUID_LOCAL)
    if uuid_local:
        consulta = consulta.filter(uuid_local=uuid_local)

    resuelto = filtros.get(FiltrosConflicto.RESUELTO)
    if resuelto is not None and resuelto != "":
        consulta = _aplicar_filtro_resuelto(consulta, resuelto)

    return consulta.order_by("-fecha")
