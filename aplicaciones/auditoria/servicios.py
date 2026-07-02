"""
Servicios de registro de auditoria.
"""

import logging
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

from django.db import DatabaseError, models
from django.db.models.fields.files import FieldFile

from aplicaciones.auditoria.contexto import ContextoAuditoria, obtener_contexto_auditoria
from aplicaciones.auditoria.constantes import SUBCADENAS_CAMPOS_SENSIBLES
from aplicaciones.auditoria.models import RegistroAuditoria

_logger = logging.getLogger(__name__)


def _es_campo_sensible(nombre_campo: str) -> bool:
    """Indica si el nombre del campo contiene datos sensibles."""
    nombre_minuscula = nombre_campo.lower()
    return any(
        subcadena in nombre_minuscula for subcadena in SUBCADENAS_CAMPOS_SENSIBLES
    )


def _normalizar_ruta_archivo_campo(valor: FieldFile) -> str | None:
    """Normaliza la ruta almacenada de un archivo para snapshot multiplataforma."""
    if not valor or not valor.name:
        return None
    return valor.name.replace("\\", "/")


def _serializar_valor_campo(valor: Any) -> Any:
    """Serializa un valor de campo para almacenamiento en JSON."""
    if valor is None:
        return None
    if isinstance(valor, (datetime, date, time)):
        return valor.isoformat()
    if isinstance(valor, Decimal):
        return str(valor)
    if isinstance(valor, UUID):
        return str(valor)
    if isinstance(valor, models.Model):
        return str(valor.pk)
    if isinstance(valor, FieldFile):
        return _normalizar_ruta_archivo_campo(valor)
    return valor


def crear_snapshot_modelo(instancia: models.Model) -> dict[str, Any]:
    """Genera un snapshot seguro de los campos simples de un modelo."""
    snapshot: dict[str, Any] = {}
    for campo in instancia._meta.fields:
        nombre_campo = campo.name
        if _es_campo_sensible(nombre_campo):
            continue
        snapshot[nombre_campo] = _serializar_valor_campo(
            getattr(instancia, nombre_campo),
        )
    return snapshot


def _valores_contexto_auditoria(
    contexto: ContextoAuditoria | None,
) -> dict[str, Any]:
    """Extrae los valores del contexto para persistir en el registro."""
    if contexto is None:
        return {
            "usuario": None,
            "identificador_keycloak": "",
            "uuid_sesion_anonima": "",
            "ip": None,
            "user_agent": "",
        }
    return {
        "usuario": contexto.usuario,
        "identificador_keycloak": contexto.identificador_keycloak,
        "uuid_sesion_anonima": contexto.uuid_sesion_anonima,
        "ip": contexto.ip,
        "user_agent": contexto.user_agent,
    }


def registrar_auditoria(
    entidad: str,
    entidad_id: str,
    accion: str,
    valor_anterior: dict[str, Any] | None = None,
    valor_nuevo: dict[str, Any] | None = None,
    descripcion: str = "",
) -> None:
    """Registra una accion de auditoria sin interrumpir el flujo principal."""
    contexto = obtener_contexto_auditoria()
    datos_contexto = _valores_contexto_auditoria(contexto)
    try:
        RegistroAuditoria.objects.create(
            entidad=entidad,
            entidad_id=entidad_id,
            accion=accion,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            descripcion=descripcion,
            **datos_contexto,
        )
    except DatabaseError as error:
        _logger.exception(
            "No se pudo registrar auditoria para %s (%s): %s",
            entidad,
            entidad_id,
            error,
        )
