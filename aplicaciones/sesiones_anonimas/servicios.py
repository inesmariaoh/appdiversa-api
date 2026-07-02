"""
Servicios de negocio para sesiones anonimas.
"""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from django.utils import timezone

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import crear_snapshot_modelo, registrar_auditoria
from aplicaciones.formularios.disponibilidad import validar_formulario_para_iniciar_sesion
from aplicaciones.formularios.excepciones import FormularioNoDisponibleError
from aplicaciones.formularios.models import Formulario
from aplicaciones.formularios.selectores import obtener_version_publicada
from aplicaciones.sesiones_anonimas.excepciones import (
    FormularioSesionNoDisponibleError,
    SesionNoExisteError,
    VersionSesionNoDisponibleError,
)
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima
from aplicaciones.sesiones_anonimas.selectores import obtener_sesion_por_uuid
from aplicaciones.sesiones_anonimas.seguridad import generar_token_cliente_seguro


@dataclass(frozen=True)
class ResultadoSesionAnonima:
    """Resultado de creacion u obtencion de sesion anonima."""

    sesion: SesionAnonima
    fue_creada: bool


def _obtener_direccion_ip(solicitud: Any) -> str | None:
    """Extrae la direccion IP de la solicitud de forma segura."""
    if solicitud is None:
        return None
    reenviado = solicitud.META.get("HTTP_X_FORWARDED_FOR")
    if reenviado:
        return str(reenviado).split(",")[0].strip()
    return solicitud.META.get("REMOTE_ADDR")


def _obtener_user_agent(solicitud: Any) -> str:
    """Extrae el user agent de la solicitud."""
    if solicitud is None:
        return ""
    return str(solicitud.META.get("HTTP_USER_AGENT", ""))


def _obtener_formulario_para_nueva_sesion(uuid_formulario: UUID) -> Formulario:
    """Valida que el formulario pueda iniciar una sesion anonima."""
    try:
        return validar_formulario_para_iniciar_sesion(uuid_formulario)
    except FormularioNoDisponibleError as error:
        raise FormularioSesionNoDisponibleError() from error


def crear_o_obtener_sesion_anonima(
    uuid_sesion: UUID,
    uuid_formulario: UUID,
    solicitud: Any = None,
    token_cliente: str = "",
    idioma: str = "",
    zona_horaria: str = "",
    es_offline: bool = False,
) -> ResultadoSesionAnonima:
    """Crea o reutiliza una sesion anonima asociada a un formulario publicado."""
    sesion_existente = obtener_sesion_por_uuid(uuid_sesion)
    if sesion_existente is not None:
        return ResultadoSesionAnonima(sesion=sesion_existente, fue_creada=False)

    formulario = _obtener_formulario_para_nueva_sesion(uuid_formulario)

    version_publicada = obtener_version_publicada(formulario)
    if version_publicada is None:
        raise VersionSesionNoDisponibleError()

    token_normalizado = token_cliente.strip()
    if not token_normalizado:
        token_normalizado = generar_token_cliente_seguro()

    sesion_nueva = SesionAnonima.objects.create(
        uuid_sesion=uuid_sesion,
        formulario=formulario,
        version_formulario=version_publicada,
        fecha_ultima_actividad=timezone.now(),
        direccion_ip=_obtener_direccion_ip(solicitud),
        user_agent=_obtener_user_agent(solicitud),
        idioma=idioma,
        zona_horaria=zona_horaria,
        estado=EstadoSesionAnonima.INICIADA,
        token_cliente=token_normalizado,
        es_offline=es_offline,
    )
    registrar_auditoria(
        entidad=SesionAnonima.__name__,
        entidad_id=str(sesion_nueva.pk),
        accion=AccionAuditoria.INICIAR_SESION,
        valor_nuevo=crear_snapshot_modelo(sesion_nueva),
    )
    return ResultadoSesionAnonima(sesion=sesion_nueva, fue_creada=True)


def obtener_sesion_anonima(uuid_sesion: UUID) -> SesionAnonima:
    """Obtiene una sesion anonima o lanza excepcion funcional."""
    sesion = obtener_sesion_por_uuid(uuid_sesion)
    if sesion is None:
        raise SesionNoExisteError()
    return sesion
