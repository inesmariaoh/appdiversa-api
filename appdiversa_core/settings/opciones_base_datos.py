"""
Construye opciones de conexion MySQL segun variables de entorno.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import environ

MODOS_SSL_VALIDOS = frozenset({"REQUIRED", "VERIFY_CA", "VERIFY_IDENTITY"})


def construir_opciones_mysql(env: environ.Env) -> dict[str, object]:
    """Agrega charset y SSL cuando Aiven u otro proveedor lo exige."""
    opciones: dict[str, object] = {"charset": "utf8mb4"}
    modo_ssl = env("DB_SSL_MODE", default="").strip().upper()

    if not modo_ssl or modo_ssl == "DISABLED":
        return opciones

    if modo_ssl not in MODOS_SSL_VALIDOS:
        return opciones

    opciones["ssl_mode"] = modo_ssl

    ruta_ca = env("DB_SSL_CA", default="").strip()
    if ruta_ca:
        opciones["ssl"] = {"ca": ruta_ca}

    return opciones
