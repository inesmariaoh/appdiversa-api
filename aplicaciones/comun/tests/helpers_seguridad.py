"""
Utilidades de prueba para seguridad de la API.
"""

from aplicaciones.comun.constantes_seguridad import HEADER_API_INTERNA, HEADER_TOKEN_SESION
from aplicaciones.auditoria.constantes import HEADER_SESION_ANONIMA

TOKEN_API_INTERNA_PRUEBA = "test-internal-token"


def headers_api_interna() -> dict[str, str]:
    """Retorna headers HTTP con token de API interna para pruebas."""
    return {HEADER_API_INTERNA: TOKEN_API_INTERNA_PRUEBA}


def headers_sesion_anonima(uuid_sesion: str, token_cliente: str) -> dict[str, str]:
    """Retorna headers HTTP con credenciales de sesion anonima."""
    return {
        HEADER_SESION_ANONIMA: uuid_sesion,
        HEADER_TOKEN_SESION: token_cliente,
    }
