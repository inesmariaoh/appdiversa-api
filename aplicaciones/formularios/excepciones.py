"""
Excepciones funcionales del modulo de formularios.
"""

from aplicaciones.formularios.constantes import MensajesFormularioApi


class FormularioNoDisponibleError(Exception):
    """Indica que el formulario solicitado no esta disponible."""

    def __init__(self) -> None:
        super().__init__(MensajesFormularioApi.FORMULARIO_NO_DISPONIBLE)
        self.mensaje = MensajesFormularioApi.FORMULARIO_NO_DISPONIBLE


class VersionPublicadaNoDisponibleError(Exception):
    """Indica que el formulario no tiene version publicada."""

    def __init__(self) -> None:
        super().__init__(MensajesFormularioApi.VERSION_NO_DISPONIBLE)
        self.mensaje = MensajesFormularioApi.VERSION_NO_DISPONIBLE


class FormularioAunNoDisponibleError(Exception):
    """Indica que el formulario esta publicado pero aun no inicia."""

    def __init__(self) -> None:
        super().__init__(MensajesFormularioApi.FORMULARIO_AUN_NO_DISPONIBLE)
        self.mensaje = MensajesFormularioApi.FORMULARIO_AUN_NO_DISPONIBLE
