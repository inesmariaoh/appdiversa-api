"""
Servicios de negocio del motor de formularios parametrizables.
"""

from uuid import UUID

from django.db.models import QuerySet

from aplicaciones.formularios.constantes import FuenteOpciones
from aplicaciones.formularios.excepciones import (
    FormularioNoDisponibleError,
    VersionPublicadaNoDisponibleError,
)
from aplicaciones.formularios.models import Formulario, Pregunta
from aplicaciones.formularios.selectores import (
    FormularioEstructuraDatos,
    obtener_estructura_formulario,
    obtener_formulario_por_uuid,
    obtener_formularios_disponibles,
    obtener_version_publicada,
)


def obtener_fuente_opciones_pregunta(pregunta: Pregunta) -> str:
    """Retorna el origen de opciones de una pregunta parametrizable."""
    if pregunta.usa_catalogo:
        return FuenteOpciones.CATALOGO
    return FuenteOpciones.OPCIONES


def listar_formularios_disponibles() -> QuerySet[Formulario]:
    """Lista formularios publicados y vigentes para consumo publico."""
    return obtener_formularios_disponibles()


def obtener_estructura_formulario_publica(
    uuid_formulario: UUID,
) -> FormularioEstructuraDatos:
    """Obtiene la estructura completa de un formulario publicado y vigente."""
    formulario_vigente = obtener_formulario_por_uuid(uuid_formulario)
    if formulario_vigente is None:
        raise FormularioNoDisponibleError()

    version_publicada = obtener_version_publicada(formulario_vigente)
    if version_publicada is None:
        raise VersionPublicadaNoDisponibleError()

    estructura = obtener_estructura_formulario(uuid_formulario)
    if estructura is None:
        raise VersionPublicadaNoDisponibleError()

    return estructura
