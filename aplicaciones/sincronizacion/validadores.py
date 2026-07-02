"""
Validadores del motor de sincronizacion offline.
"""

import hashlib
import json
from typing import Any


def calcular_checksum_operacion(
    codigo_pregunta: str,
    valor: Any,
    version_cliente: int,
) -> str:
    """Calcula el checksum SHA-256 canonico de una operacion de sincronizacion."""
    payload = json.dumps(
        {
            "codigo_pregunta": codigo_pregunta,
            "valor": valor,
            "version_cliente": version_cliente,
        },
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validar_checksum_operacion(
    codigo_pregunta: str,
    valor: Any,
    version_cliente: int,
    checksum_recibido: str,
) -> bool:
    """Verifica que el checksum recibido coincida con el calculado."""
    if not checksum_recibido.strip():
        return True
    checksum_esperado = calcular_checksum_operacion(
        codigo_pregunta,
        valor,
        version_cliente,
    )
    return checksum_esperado == checksum_recibido.strip()
