"""
Generadores de archivos del motor de exportaciones.
"""

import csv
import io
import json
from abc import ABC, abstractmethod
from typing import Any

from aplicaciones.exportaciones.constantes import FormatoExportacion
from aplicaciones.exportaciones.excepciones import FormatoExportacionNoSoportadoError


class GeneradorExportacion(ABC):
    """Contrato de generacion de archivos de exportacion."""

    @abstractmethod
    def generar(
        self,
        registros: list[dict[str, Any]],
        parametros: dict[str, Any],
    ) -> bytes:
        """Genera el contenido binario del archivo exportado."""


def _obtener_columnas(registros: list[dict[str, Any]]) -> list[str]:
    """Obtiene las columnas unicas de un conjunto de registros."""
    columnas: list[str] = []
    for registro in registros:
        for clave in registro.keys():
            if clave not in columnas:
                columnas.append(clave)
    return columnas


def _serializar_valor_celda(valor: Any) -> str:
    """Convierte un valor a representacion textual para exportacion."""
    if valor is None:
        return ""
    if isinstance(valor, (dict, list)):
        return json.dumps(valor, ensure_ascii=False)
    return str(valor)


class CsvExportador(GeneradorExportacion):
    """Generador de exportaciones en formato CSV."""

    def generar(
        self,
        registros: list[dict[str, Any]],
        parametros: dict[str, Any],
    ) -> bytes:
        """Genera contenido CSV desde registros planos."""
        buffer = io.StringIO()
        if not registros:
            return b""

        columnas = _obtener_columnas(registros)
        escritor = csv.DictWriter(buffer, fieldnames=columnas, extrasaction="ignore")
        escritor.writeheader()
        for registro in registros:
            fila = {
                columna: _serializar_valor_celda(registro.get(columna))
                for columna in columnas
            }
            escritor.writerow(fila)
        return buffer.getvalue().encode("utf-8-sig")


class JsonExportador(GeneradorExportacion):
    """Generador de exportaciones en formato JSON."""

    def generar(
        self,
        registros: list[dict[str, Any]],
        parametros: dict[str, Any],
    ) -> bytes:
        """Genera contenido JSON desde registros."""
        contenido = json.dumps(registros, ensure_ascii=False, indent=2, default=str)
        return contenido.encode("utf-8")


class SqlExportador(GeneradorExportacion):
    """Generador de exportaciones en formato SQL."""

    def generar(
        self,
        registros: list[dict[str, Any]],
        parametros: dict[str, Any],
    ) -> bytes:
        """Genera sentencias INSERT SQL desde registros."""
        tabla = parametros.get("tabla", "datos_exportados")
        lineas: list[str] = []
        for registro in registros:
            columnas = list(registro.keys())
            valores = [
                _serializar_valor_sql(registro.get(columna))
                for columna in columnas
            ]
            columnas_sql = ", ".join(columnas)
            valores_sql = ", ".join(valores)
            lineas.append(f"INSERT INTO {tabla} ({columnas_sql}) VALUES ({valores_sql});")
        return "\n".join(lineas).encode("utf-8")


def _serializar_valor_sql(valor: Any) -> str:
    """Serializa un valor para uso en sentencias SQL."""
    if valor is None:
        return "NULL"
    if isinstance(valor, bool):
        return "1" if valor else "0"
    if isinstance(valor, (int, float)):
        return str(valor)
    if isinstance(valor, (dict, list)):
        texto = json.dumps(valor, ensure_ascii=False)
        return "'" + texto.replace("'", "''") + "'"
    texto = str(valor).replace("'", "''")
    return f"'{texto}'"


class ExcelExportador(GeneradorExportacion):
    """Generador de exportaciones en formato Excel (xlsx)."""

    def generar(
        self,
        registros: list[dict[str, Any]],
        parametros: dict[str, Any],
    ) -> bytes:
        """Genera hoja Excel desde registros."""
        from openpyxl import Workbook

        libro = Workbook()
        hoja = libro.active
        hoja.title = parametros.get("nombre_hoja", "Exportacion")

        if not registros:
            buffer = io.BytesIO()
            libro.save(buffer)
            return buffer.getvalue()

        columnas = _obtener_columnas(registros)
        hoja.append(columnas)
        for registro in registros:
            hoja.append(
                [_serializar_valor_celda(registro.get(columna)) for columna in columnas],
            )

        buffer = io.BytesIO()
        libro.save(buffer)
        return buffer.getvalue()


class PdfExportador(GeneradorExportacion):
    """Generador PDF preparado para implementacion futura."""

    def generar(
        self,
        registros: list[dict[str, Any]],
        parametros: dict[str, Any],
    ) -> bytes:
        """Indica que el formato PDF aun no esta implementado."""
        raise FormatoExportacionNoSoportadoError()


class OdsExportador(GeneradorExportacion):
    """Generador ODS preparado para implementacion futura."""

    def generar(
        self,
        registros: list[dict[str, Any]],
        parametros: dict[str, Any],
    ) -> bytes:
        """Indica que el formato ODS aun no esta implementado."""
        raise FormatoExportacionNoSoportadoError()


def obtener_generador_exportacion(formato: str) -> GeneradorExportacion:
    """Retorna el generador correspondiente al formato solicitado."""
    generadores: dict[str, GeneradorExportacion] = {
        FormatoExportacion.CSV: CsvExportador(),
        FormatoExportacion.XLSX: ExcelExportador(),
        FormatoExportacion.JSON: JsonExportador(),
        FormatoExportacion.SQL: SqlExportador(),
        FormatoExportacion.PDF: PdfExportador(),
        FormatoExportacion.ODS: OdsExportador(),
    }
    generador = generadores.get(formato)
    if generador is None:
        raise FormatoExportacionNoSoportadoError()
    return generador


def generar_csv(
    registros: list[dict[str, Any]],
    parametros: dict[str, Any] | None = None,
) -> bytes:
    """Genera exportacion CSV."""
    return CsvExportador().generar(registros, parametros or {})


def generar_excel(
    registros: list[dict[str, Any]],
    parametros: dict[str, Any] | None = None,
) -> bytes:
    """Genera exportacion Excel."""
    return ExcelExportador().generar(registros, parametros or {})


def generar_json(
    registros: list[dict[str, Any]],
    parametros: dict[str, Any] | None = None,
) -> bytes:
    """Genera exportacion JSON."""
    return JsonExportador().generar(registros, parametros or {})


def generar_sql(
    registros: list[dict[str, Any]],
    parametros: dict[str, Any] | None = None,
) -> bytes:
    """Genera exportacion SQL."""
    return SqlExportador().generar(registros, parametros or {})
