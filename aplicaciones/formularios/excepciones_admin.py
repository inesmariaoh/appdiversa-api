"""
Excepciones de la API administrativa de formularios.
"""

from aplicaciones.formularios.constantes_admin import MensajesFormularioAdmin


class FormularioAdminNoEncontradoError(Exception):
    """Indica que el formulario no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesFormularioAdmin.FORMULARIO_NO_ENCONTRADO)
        self.mensaje = MensajesFormularioAdmin.FORMULARIO_NO_ENCONTRADO


class VersionAdminNoEncontradaError(Exception):
    """Indica que la version no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesFormularioAdmin.VERSION_NO_ENCONTRADA)
        self.mensaje = MensajesFormularioAdmin.VERSION_NO_ENCONTRADA


class SeccionAdminNoEncontradaError(Exception):
    """Indica que la seccion no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesFormularioAdmin.SECCION_NO_ENCONTRADA)
        self.mensaje = MensajesFormularioAdmin.SECCION_NO_ENCONTRADA


class PreguntaAdminNoEncontradaError(Exception):
    """Indica que la pregunta no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesFormularioAdmin.PREGUNTA_NO_ENCONTRADA)
        self.mensaje = MensajesFormularioAdmin.PREGUNTA_NO_ENCONTRADA


class OpcionAdminNoEncontradaError(Exception):
    """Indica que la opcion no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesFormularioAdmin.OPCION_NO_ENCONTRADA)
        self.mensaje = MensajesFormularioAdmin.OPCION_NO_ENCONTRADA


class ReglaAdminNoEncontradaError(Exception):
    """Indica que la regla no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesFormularioAdmin.REGLA_NO_ENCONTRADA)
        self.mensaje = MensajesFormularioAdmin.REGLA_NO_ENCONTRADA


class TextoAdminNoEncontradoError(Exception):
    """Indica que el texto no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesFormularioAdmin.TEXTO_NO_ENCONTRADO)
        self.mensaje = MensajesFormularioAdmin.TEXTO_NO_ENCONTRADO


class ValidacionFormularioAdminError(Exception):
    """Indica error de validacion de negocio en administracion."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
