"""
Constantes del repositorio documental transversal.
"""

from django.db import models


class TipoArchivo(models.TextChoices):
    """Tipos de archivo soportados por el repositorio."""

    IMAGEN = "imagen", "Imagen"
    DOCUMENTO = "documento", "Documento"
    AUDIO = "audio", "Audio"
    VIDEO = "video", "Video"
    FIRMA = "firma", "Firma"
    MULTIMEDIA = "multimedia", "Multimedia"
    ARCHIVO_GENERAL = "archivo_general", "Archivo general"


class EstadoArchivo(models.TextChoices):
    """Estados del ciclo de vida de un archivo en el repositorio."""

    ACTIVO = "activo", "Activo"
    ELIMINADO = "eliminado", "Eliminado"
    CUARENTENA = "cuarentena", "Cuarentena"
    PROCESANDO = "procesando", "Procesando"


class OrigenArchivo(models.TextChoices):
    """Origen funcional del archivo en el aplicativo."""

    FORMULARIO = "formulario", "Formulario"
    PREGUNTA = "pregunta", "Pregunta"
    RESPUESTA = "respuesta", "Respuesta"
    INTERNACIONALIZACION = "internacionalizacion", "Internacionalización"
    CONFIGURACION = "configuracion", "Configuración"
    CATALOGO = "catalogo", "Catálogo"
    NOTIFICACION = "notificacion", "Notificación"
    OTRO = "otro", "Otro"


EXTENSIONES_PROHIBIDAS = frozenset(
    {
        "exe",
        "dll",
        "bat",
        "cmd",
        "ps1",
        "sh",
        "jar",
        "msi",
        "apk",
        "ipa",
        "scr",
        "com",
    },
)

MIME_IMAGEN_JPEG = "image/jpeg"
MIME_IMAGEN_PNG = "image/png"
MIME_IMAGEN_WEBP = "image/webp"
MIME_IMAGEN_SVG = "image/svg+xml"
MIME_AUDIO_MPEG = "audio/mpeg"
MIME_VIDEO_MP4 = "video/mp4"
MIME_APLICACION_PDF = "application/pdf"
MIME_TEXTO_PLAIN = "text/plain"
MIME_HOJA_CALCULO_ODS = "application/vnd.oasis.opendocument.spreadsheet"

MIME_PERMITIDOS_POR_TIPO: dict[str, frozenset[str]] = {
    TipoArchivo.IMAGEN: frozenset(
        {
            MIME_IMAGEN_JPEG,
            MIME_IMAGEN_PNG,
            MIME_IMAGEN_WEBP,
            "image/gif",
            MIME_IMAGEN_SVG,
        },
    ),
    TipoArchivo.DOCUMENTO: frozenset(
        {
            MIME_APLICACION_PDF,
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            MIME_HOJA_CALCULO_ODS,
            "text/csv",
            MIME_TEXTO_PLAIN,
            "application/json",
            "application/sql",
        },
    ),
    TipoArchivo.AUDIO: frozenset(
        {
            MIME_AUDIO_MPEG,
            "audio/wav",
            "audio/ogg",
            "audio/mp4",
            "audio/x-wav",
        },
    ),
    TipoArchivo.VIDEO: frozenset(
        {
            MIME_VIDEO_MP4,
            "video/webm",
            "video/quicktime",
        },
    ),
    TipoArchivo.FIRMA: frozenset(
        {
            MIME_IMAGEN_PNG,
            MIME_IMAGEN_JPEG,
            MIME_IMAGEN_SVG,
        },
    ),
    TipoArchivo.MULTIMEDIA: frozenset(
        {
            MIME_IMAGEN_JPEG,
            MIME_IMAGEN_PNG,
            MIME_IMAGEN_WEBP,
            MIME_AUDIO_MPEG,
            MIME_VIDEO_MP4,
        },
    ),
    TipoArchivo.ARCHIVO_GENERAL: frozenset(
        {
            MIME_APLICACION_PDF,
            MIME_TEXTO_PLAIN,
            MIME_IMAGEN_JPEG,
            MIME_IMAGEN_PNG,
        },
    ),
}

TAMANO_MAXIMO_POR_TIPO: dict[str, int] = {
    TipoArchivo.IMAGEN: 10 * 1024 * 1024,
    TipoArchivo.DOCUMENTO: 25 * 1024 * 1024,
    TipoArchivo.AUDIO: 50 * 1024 * 1024,
    TipoArchivo.VIDEO: 100 * 1024 * 1024,
    TipoArchivo.FIRMA: 5 * 1024 * 1024,
    TipoArchivo.MULTIMEDIA: 100 * 1024 * 1024,
    TipoArchivo.ARCHIVO_GENERAL: 25 * 1024 * 1024,
}

PREFIJO_RUTA_REPOSITORIO = "repositorio"

REFERENCIA_MODELO_ARCHIVO_REPOSITORIO = "archivos.ArchivoRepositorio"


class MensajesArchivoApi:
    """Mensajes funcionales de la API de archivos."""

    ARCHIVO_NO_ENCONTRADO = "El archivo solicitado no existe."
    EXTENSION_NO_PERMITIDA = "La extensión del archivo no está permitida."
    MIME_NO_PERMITIDO = "El tipo de contenido del archivo no está permitido."
    TAMANO_NO_PERMITIDO = "El archivo supera el tamaño máximo permitido."
    NOMBRE_NO_PERMITIDO = "El nombre del archivo no es válido."
    CHECKSUM_INVALIDO = "El checksum del archivo no es válido."
