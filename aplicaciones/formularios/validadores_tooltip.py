"""
Validadores reutilizables para tooltips de preguntas y opciones.
"""

from django.core.exceptions import ValidationError

from aplicaciones.formularios.excepciones_admin import ValidacionFormularioAdminError
from aplicaciones.formularios.models import MensajesValidacion


def _texto_tooltip_limpio(tooltip: str) -> str:
    """Retorna el texto del tooltip sin espacios laterales."""
    return str(tooltip).strip()


def validar_tooltip_configurado(tiene_tooltip: bool, tooltip: str) -> None:
    """Valida que exista texto cuando el tooltip esta activado."""
    if tiene_tooltip and not _texto_tooltip_limpio(tooltip):
        raise ValidationError(
            {"tooltip": MensajesValidacion.TOOLTIP_TEXTO_OBLIGATORIO},
        )


def normalizar_tooltip(tiene_tooltip: bool, tooltip: str) -> tuple[bool, str]:
    """Normaliza la configuracion del tooltip antes de persistir."""
    texto = _texto_tooltip_limpio(tooltip)
    if tiene_tooltip and not texto:
        raise ValidationError(
            {"tooltip": MensajesValidacion.TOOLTIP_TEXTO_OBLIGATORIO},
        )
    if texto:
        return True, texto
    return False, ""


def tooltip_visible_en_api(tiene_tooltip: bool, tooltip: str) -> str:
    """Retorna el texto del tooltip solo cuando esta activado."""
    if not tiene_tooltip:
        return ""
    return _texto_tooltip_limpio(tooltip)


def _extraer_mensaje_tooltip(error: ValidationError) -> str:
    """Obtiene el mensaje de validacion asociado al campo tooltip."""
    if hasattr(error, "message_dict"):
        mensajes = error.message_dict.get("tooltip")
        if mensajes:
            return str(mensajes[0])
    if error.messages:
        return str(error.messages[0])
    return MensajesValidacion.TOOLTIP_TEXTO_OBLIGATORIO


def validar_y_normalizar_tooltip_admin(
    tiene_tooltip: bool,
    tooltip: str,
) -> tuple[bool, str]:
    """Valida y normaliza tooltip para operaciones administrativas."""
    try:
        return normalizar_tooltip(tiene_tooltip, tooltip)
    except ValidationError as error:
        raise ValidacionFormularioAdminError(
            _extraer_mensaje_tooltip(error),
        ) from error
