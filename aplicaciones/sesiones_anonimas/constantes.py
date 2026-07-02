"""
Mensajes funcionales de la API de sesiones anonimas.
"""

from aplicaciones.formularios.constantes import MensajesFormularioApi


class MensajesSesionApi:
    """Mensajes de respuesta para endpoints de sesiones anonimas."""

    FORMULARIO_NO_DISPONIBLE = MensajesFormularioApi.FORMULARIO_NO_DISPONIBLE
    VERSION_NO_DISPONIBLE = MensajesFormularioApi.VERSION_NO_DISPONIBLE
    SESION_NO_EXISTE = "La sesión anónima no existe."
    TOKEN_SESION_INVALIDO = "El token de sesión no es válido."
    SESION_YA_FINALIZADA = "La sesión ya fue finalizada."
    SESION_YA_VINCULADA = (
        "La sesión anónima ya está asociada a otro usuario registrado."
    )
    SESION_VINCULADA = "La sesión anónima se asoció correctamente al usuario."
