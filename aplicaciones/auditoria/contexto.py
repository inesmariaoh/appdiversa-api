"""
Contexto de auditoria por request mediante contextvars.
"""

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ContextoAuditoria:
    """Datos de contexto para registrar auditoria en una solicitud."""

    usuario: Any = None
    identificador_keycloak: str = ""
    uuid_sesion_anonima: str = ""
    ip: str | None = None
    user_agent: str = ""


_contexto_auditoria: ContextVar[ContextoAuditoria | None] = ContextVar(
    "contexto_auditoria",
    default=None,
)


def establecer_contexto_auditoria(
    usuario: Any = None,
    identificador_keycloak: str = "",
    uuid_sesion_anonima: str = "",
    ip: str | None = None,
    user_agent: str = "",
) -> None:
    """Establece el contexto de auditoria para el request actual."""
    _contexto_auditoria.set(
        ContextoAuditoria(
            usuario=usuario,
            identificador_keycloak=identificador_keycloak,
            uuid_sesion_anonima=uuid_sesion_anonima,
            ip=ip,
            user_agent=user_agent,
        ),
    )


def obtener_contexto_auditoria() -> ContextoAuditoria | None:
    """Retorna el contexto de auditoria del request actual."""
    return _contexto_auditoria.get()


def limpiar_contexto_auditoria() -> None:
    """Limpia el contexto de auditoria del request actual."""
    _contexto_auditoria.set(None)
