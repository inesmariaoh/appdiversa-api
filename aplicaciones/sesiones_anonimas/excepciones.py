"""
Excepciones funcionales de sesiones anonimas.
"""

from aplicaciones.sesiones_anonimas.constantes import MensajesSesionApi


class FormularioSesionNoDisponibleError(Exception):
    """Indica que el formulario no esta disponible para sesion."""

    def __init__(self) -> None:
        super().__init__(MensajesSesionApi.FORMULARIO_NO_DISPONIBLE)
        self.mensaje = MensajesSesionApi.FORMULARIO_NO_DISPONIBLE


class VersionSesionNoDisponibleError(Exception):
    """Indica que no existe version publicada para el formulario."""

    def __init__(self) -> None:
        super().__init__(MensajesSesionApi.VERSION_NO_DISPONIBLE)
        self.mensaje = MensajesSesionApi.VERSION_NO_DISPONIBLE


class SesionNoExisteError(Exception):
    """Indica que la sesion anonima no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesSesionApi.SESION_NO_EXISTE)
        self.mensaje = MensajesSesionApi.SESION_NO_EXISTE


class TokenSesionInvalidoError(Exception):
    """Indica que el token de sesion anonima no es valido."""

    def __init__(self) -> None:
        super().__init__(MensajesSesionApi.TOKEN_SESION_INVALIDO)
        self.mensaje = MensajesSesionApi.TOKEN_SESION_INVALIDO


class SesionFinalizadaAccesoError(Exception):
    """Indica que la sesion ya fue finalizada y no admite modificaciones."""

    def __init__(self) -> None:
        super().__init__(MensajesSesionApi.SESION_YA_FINALIZADA)
        self.mensaje = MensajesSesionApi.SESION_YA_FINALIZADA


class SesionYaVinculadaOtroUsuarioError(Exception):
    """Indica que la sesion ya pertenece a otro usuario registrado."""

    def __init__(self) -> None:
        super().__init__(MensajesSesionApi.SESION_YA_VINCULADA)
        self.mensaje = MensajesSesionApi.SESION_YA_VINCULADA
