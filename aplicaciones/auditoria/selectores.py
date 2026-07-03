"""
Selectores de consulta de registros de auditoria.
"""

from dataclasses import dataclass
from datetime import date

from django.db.models import Q, QuerySet

from aplicaciones.auditoria.models import RegistroAuditoria


@dataclass
class FiltrosConsultaAuditoria:
    """Filtros disponibles para la consulta de registros de auditoria."""

    entidad: str = ""
    entidad_id: str = ""
    accion: str = ""
    usuario: int | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    busqueda: str = ""


def _aplicar_filtros_exactos(
    consulta: QuerySet[RegistroAuditoria],
    filtros: FiltrosConsultaAuditoria,
) -> QuerySet[RegistroAuditoria]:
    """Aplica los filtros de coincidencia exacta a la consulta."""
    if filtros.entidad:
        consulta = consulta.filter(entidad=filtros.entidad)
    if filtros.entidad_id:
        consulta = consulta.filter(entidad_id=filtros.entidad_id)
    if filtros.accion:
        consulta = consulta.filter(accion=filtros.accion)
    if filtros.usuario is not None:
        consulta = consulta.filter(usuario_id=filtros.usuario)
    return consulta


def _aplicar_filtros_fecha(
    consulta: QuerySet[RegistroAuditoria],
    filtros: FiltrosConsultaAuditoria,
) -> QuerySet[RegistroAuditoria]:
    """Aplica el rango de fechas por dia sobre la fecha de accion."""
    if filtros.fecha_inicio is not None:
        consulta = consulta.filter(fecha_accion__date__gte=filtros.fecha_inicio)
    if filtros.fecha_fin is not None:
        consulta = consulta.filter(fecha_accion__date__lte=filtros.fecha_fin)
    return consulta


def _aplicar_busqueda(
    consulta: QuerySet[RegistroAuditoria],
    filtros: FiltrosConsultaAuditoria,
) -> QuerySet[RegistroAuditoria]:
    """Aplica una busqueda parcial sobre entidad y descripcion."""
    termino = filtros.busqueda.strip()
    if not termino:
        return consulta
    return consulta.filter(
        Q(entidad__icontains=termino) | Q(descripcion__icontains=termino),
    )


def listar_registros_auditoria(
    filtros: FiltrosConsultaAuditoria,
) -> QuerySet[RegistroAuditoria]:
    """Lista los registros de auditoria aplicando los filtros indicados."""
    consulta = RegistroAuditoria.objects.select_related("usuario").all()
    consulta = _aplicar_filtros_exactos(consulta, filtros)
    consulta = _aplicar_filtros_fecha(consulta, filtros)
    return _aplicar_busqueda(consulta, filtros)


def obtener_registro_auditoria(registro_id: int) -> RegistroAuditoria | None:
    """Retorna un registro de auditoria por identificador."""
    return (
        RegistroAuditoria.objects.select_related("usuario")
        .filter(pk=registro_id)
        .first()
    )
