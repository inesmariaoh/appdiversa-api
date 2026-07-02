"""
Validacion de credenciales de sesion anonima.
"""

import secrets
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from aplicaciones.auditoria.constantes import HEADER_SESION_ANONIMA
from aplicaciones.comun.constantes_seguridad import HEADER_TOKEN_SESION
from aplicaciones.sesiones_anonimas.constantes import MensajesSesionApi
from aplicaciones.sesiones_anonimas.excepciones import (
    SesionFinalizadaAccesoError,
    SesionNoExisteError,
    TokenSesionInvalidoError,
)
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima
from aplicaciones.sesiones_anonimas.selectores import obtener_sesion_por_uuid


def generar_token_cliente_seguro() -> str:
    """Genera un token seguro para autenticar mutaciones de sesion anonima."""
    return secrets.token_urlsafe(32)


@dataclass(frozen=True)
class CredencialesSesionAnonima:
    """Credenciales extraidas de una solicitud HTTP."""

    uuid_sesion: UUID | None
    token_cliente: str


def _normalizar_uuid_sesion(valor: Any) -> UUID | None:
    """Convierte un valor recibido a UUID de sesion si es valido."""
    if valor is None or valor == "":
        return None
    try:
        return UUID(str(valor))
    except (ValueError, TypeError, AttributeError):
        return None


def extraer_credenciales_sesion(
    solicitud: Any,
    uuid_sesion_url: UUID | None = None,
) -> CredencialesSesionAnonima:
    """Extrae uuid y token de sesion desde headers o body de la solicitud."""
    uuid_header = _normalizar_uuid_sesion(solicitud.META.get(HEADER_SESION_ANONIMA))
    token_header = str(solicitud.META.get(HEADER_TOKEN_SESION, "")).strip()

    uuid_body: UUID | None = None
    token_body = ""
    if hasattr(solicitud, "data") and solicitud.data:
        uuid_body = _normalizar_uuid_sesion(solicitud.data.get("uuid_sesion"))
        token_body = str(solicitud.data.get("token_cliente", "")).strip()

    uuid_sesion = uuid_sesion_url or uuid_header or uuid_body
    token_cliente = token_header or token_body
    return CredencialesSesionAnonima(
        uuid_sesion=uuid_sesion,
        token_cliente=token_cliente,
    )


def _tokens_coinciden(token_almacenado: str, token_recibido: str) -> bool:
    """Compara tokens de sesion evitando ataques de tiempo."""
    if not token_almacenado or not token_recibido:
        return False
    return secrets.compare_digest(token_almacenado, token_recibido)


def validar_acceso_sesion_anonima(
    uuid_sesion: UUID | None,
    token_cliente: str,
    requiere_modificacion: bool = True,
) -> SesionAnonima:
    """Valida credenciales de sesion anonima y retorna la sesion activa."""
    if uuid_sesion is None or not token_cliente.strip():
        raise TokenSesionInvalidoError()

    sesion = obtener_sesion_por_uuid(uuid_sesion)
    if sesion is None:
        raise SesionNoExisteError()

    if not _tokens_coinciden(sesion.token_cliente, token_cliente.strip()):
        raise TokenSesionInvalidoError()

    if requiere_modificacion and sesion.estado == EstadoSesionAnonima.FINALIZADA:
        raise SesionFinalizadaAccesoError()

    return sesion


def obtener_mensaje_error_acceso_sesion(error: Exception) -> str:
    """Retorna el mensaje funcional asociado a un error de acceso de sesion."""
    if isinstance(error, SesionNoExisteError):
        return error.mensaje
    if isinstance(error, TokenSesionInvalidoError):
        return error.mensaje
    if isinstance(error, SesionFinalizadaAccesoError):
        return error.mensaje
    return MensajesSesionApi.TOKEN_SESION_INVALIDO
