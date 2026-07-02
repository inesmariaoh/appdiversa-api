"""
Excepciones funcionales de respuestas.
"""

from aplicaciones.respuestas.constantes import MensajesRespuestaApi


class SesionRespuestaNoExisteError(Exception):
    """Indica que la sesion anonima no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesRespuestaApi.SESION_NO_EXISTE)
        self.mensaje = MensajesRespuestaApi.SESION_NO_EXISTE


class PreguntaNoExisteError(Exception):
    """Indica que la pregunta no existe en el formulario de la sesion."""

    def __init__(self) -> None:
        super().__init__(MensajesRespuestaApi.PREGUNTA_NO_EXISTE)
        self.mensaje = MensajesRespuestaApi.PREGUNTA_NO_EXISTE


class ValorInvalidoError(Exception):
    """Indica que el valor no es valido para el tipo de pregunta."""

    def __init__(self) -> None:
        super().__init__(MensajesRespuestaApi.VALOR_INVALIDO)
        self.mensaje = MensajesRespuestaApi.VALOR_INVALIDO


class ValorNoPerteneceCatalogoError(Exception):
    """Indica que el valor no pertenece al catalogo asociado a la pregunta."""

    def __init__(self) -> None:
        super().__init__(MensajesRespuestaApi.VALOR_NO_PERTENECE_CATALOGO)
        self.mensaje = MensajesRespuestaApi.VALOR_NO_PERTENECE_CATALOGO


class OrigenRespuestaInvalidoError(Exception):
    """Indica que el origen de respuesta no es valido."""

    def __init__(self) -> None:
        super().__init__(MensajesRespuestaApi.ORIGEN_INVALIDO)
        self.mensaje = MensajesRespuestaApi.ORIGEN_INVALIDO


class FormularioYaFinalizadoError(Exception):
    """Indica que el formulario de la sesion ya fue finalizado."""

    def __init__(self) -> None:
        super().__init__(MensajesRespuestaApi.FORMULARIO_YA_FINALIZADO)
        self.mensaje = MensajesRespuestaApi.FORMULARIO_YA_FINALIZADO
