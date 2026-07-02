"""
Validadores de archivos multimedia para traducciones accesibles.
"""

from django.core.exceptions import ValidationError

EXTENSIONES_AUDIO = frozenset({"mp3", "wav", "ogg", "m4a"})
EXTENSIONES_VIDEO = frozenset({"mp4", "webm", "mov"})
EXTENSIONES_IMAGEN = frozenset({"jpg", "jpeg", "png", "webp", "svg"})
EXTENSIONES_LENGUA_SENAS = frozenset({"mp4", "webm", "mov"})


class MensajesValidacionArchivoMultimedia:
    """Mensajes funcionales de validacion de archivos multimedia."""

    EXTENSION_AUDIO_NO_PERMITIDA = (
        "El formato del archivo de audio no está permitido. "
        "Use mp3, wav, ogg o m4a."
    )
    EXTENSION_VIDEO_NO_PERMITIDA = (
        "El formato del archivo de vídeo no está permitido. "
        "Use mp4, webm o mov."
    )
    EXTENSION_IMAGEN_NO_PERMITIDA = (
        "El formato del archivo de imagen no está permitido. "
        "Use jpg, jpeg, png, webp o svg."
    )
    EXTENSION_LENGUA_SENAS_NO_PERMITIDA = (
        "El formato del archivo de lengua de señas no está permitido. "
        "Use mp4, webm o mov."
    )


def obtener_extension_archivo(nombre_archivo: str) -> str | None:
    """Extrae la extension de un nombre de archivo en minusculas."""
    if not nombre_archivo or "." not in nombre_archivo:
        return None
    return nombre_archivo.rsplit(".", 1)[-1].lower()


def validar_extension_archivo(
    nombre_archivo: str,
    extensiones_permitidas: frozenset[str],
) -> bool:
    """Indica si la extension del archivo esta dentro de las permitidas."""
    extension = obtener_extension_archivo(nombre_archivo)
    if extension is None:
        return False
    return extension in extensiones_permitidas


def validar_archivo_multimedia(
    nombre_archivo: str,
    extensiones_permitidas: frozenset[str],
    mensaje_error: str,
) -> None:
    """Valida la extension de un archivo multimedia o lanza ValidationError."""
    if not nombre_archivo:
        return
    if not validar_extension_archivo(nombre_archivo, extensiones_permitidas):
        raise ValidationError(mensaje_error)
