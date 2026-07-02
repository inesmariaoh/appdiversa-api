"""
Estrategias de resolucion de conflictos de sincronizacion.
"""

from datetime import datetime

from aplicaciones.sincronizacion.models import ResolucionConflicto


def resolver_last_write_wins(
    version_cliente_nueva: int,
    version_cliente_servidor: int,
    fecha_cliente_nueva: datetime,
    fecha_cliente_servidor: datetime | None,
) -> str:
    """Determina el ganador con estrategia Last Write Wins por version y fecha."""
    if version_cliente_nueva > version_cliente_servidor:
        return ResolucionConflicto.CLIENTE
    if version_cliente_nueva < version_cliente_servidor:
        return ResolucionConflicto.SERVIDOR
    if fecha_cliente_servidor is None:
        return ResolucionConflicto.CLIENTE
    if fecha_cliente_nueva >= fecha_cliente_servidor:
        return ResolucionConflicto.CLIENTE
    return ResolucionConflicto.SERVIDOR
