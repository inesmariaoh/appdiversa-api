"""
Calculo de disponibilidad publica de formularios por fechas.
"""

from datetime import datetime
from uuid import UUID

from django.utils import timezone

from aplicaciones.formularios.constantes import (
    EstadoDisponibilidadFormulario,
    EtiquetaEstadoFormulario,
)
from aplicaciones.formularios.excepciones import (
    FormularioAunNoDisponibleError,
    FormularioNoDisponibleError,
)
from aplicaciones.formularios.models import Formulario
from aplicaciones.formularios.selectores import (
    obtener_formulario_iniciable_por_uuid,
    obtener_formulario_publicado_listado_por_uuid,
)


def calcular_metadatos_disponibilidad(
    formulario: Formulario,
    instante: datetime | None = None,
) -> dict[str, str | bool]:
    """Calcula estado de disponibilidad visible para el listado publico."""
    ahora = instante or timezone.now()
    if formulario.fecha_inicio and formulario.fecha_inicio > ahora:
        return {
            "estado_disponibilidad": EstadoDisponibilidadFormulario.PROXIMAMENTE,
            "puede_iniciar": False,
            "etiqueta_estado": EtiquetaEstadoFormulario.PROXIMAMENTE,
        }
    return {
        "estado_disponibilidad": EstadoDisponibilidadFormulario.DISPONIBLE,
        "puede_iniciar": True,
        "etiqueta_estado": EtiquetaEstadoFormulario.DISPONIBLE,
    }


def validar_formulario_para_iniciar_sesion(uuid_formulario: UUID) -> Formulario:
    """Valida que un formulario publicado pueda iniciar sesion anonima."""
    formulario_listado = obtener_formulario_publicado_listado_por_uuid(uuid_formulario)
    if formulario_listado is None:
        raise FormularioNoDisponibleError()

    formulario_iniciable = obtener_formulario_iniciable_por_uuid(uuid_formulario)
    if formulario_iniciable is None:
        raise FormularioAunNoDisponibleError()

    return formulario_iniciable
