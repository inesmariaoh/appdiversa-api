"""
Constantes del motor transversal de exportaciones.
"""

from django.db import models


class TipoExportacion(models.TextChoices):
    """Tipos de exportacion soportados."""

    RESPUESTAS = "respuestas", "Respuestas"
    CATALOGOS = "catalogos", "Catálogos"
    ANALITICA = "analitica", "Analítica"


class FormatoExportacion(models.TextChoices):
    """Formatos de archivo de exportacion."""

    CSV = "csv", "CSV"
    XLSX = "xlsx", "Excel"
    JSON = "json", "JSON"
    SQL = "sql", "SQL"
    PDF = "pdf", "PDF"
    ODS = "ods", "ODS"


class EstadoExportacion(models.TextChoices):
    """Estados del proceso de exportacion."""

    PENDIENTE = "pendiente", "Pendiente"
    PROCESANDO = "procesando", "Procesando"
    FINALIZADA = "finalizada", "Finalizada"
    FALLIDA = "fallida", "Fallida"


class MensajesExportacionApi:
    """Mensajes funcionales de la API de exportaciones."""

    EXPORTACION_NO_ENCONTRADA = "La exportación solicitada no existe."
    FORMATO_NO_SOPORTADO = "El formato de exportación solicitado no está soportado."
    PARAMETROS_INVALIDOS = "Los parámetros de exportación no son válidos."

EXTENSION_POR_FORMATO = {
    FormatoExportacion.CSV: "csv",
    FormatoExportacion.XLSX: "xlsx",
    FormatoExportacion.JSON: "json",
    FormatoExportacion.SQL: "sql",
    FormatoExportacion.PDF: "pdf",
    FormatoExportacion.ODS: "ods",
}

MIME_POR_FORMATO = {
    FormatoExportacion.CSV: "text/csv",
    FormatoExportacion.XLSX: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    FormatoExportacion.JSON: "application/json",
    FormatoExportacion.SQL: "application/sql",
    FormatoExportacion.PDF: "application/pdf",
    FormatoExportacion.ODS: "application/vnd.oasis.opendocument.spreadsheet",
}
