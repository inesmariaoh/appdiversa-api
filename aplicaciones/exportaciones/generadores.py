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


_PDF_MARGEN_PUNTOS = 36
_PDF_TAMANO_FUENTE_CELDA = 7
_PDF_TAMANO_FUENTE_ENCABEZADO = 8
_PDF_LIMITE_CARACTERES_CELDA = 800
_PDF_TITULO_POR_DEFECTO = "Exportación de datos"
_PDF_MENSAJE_SIN_DATOS = "No se encontraron registros para exportar."


def _celda_pdf(texto: str, estilo: Any) -> Any:
    """Construye un parrafo de celda saneando el largo maximo del texto."""
    from reportlab.platypus import Paragraph

    contenido = texto[:_PDF_LIMITE_CARACTERES_CELDA]
    seguro = contenido.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(seguro or "&nbsp;", estilo)


def _construir_matriz_pdf(
    registros: list[dict[str, Any]],
    columnas: list[str],
    estilo_encabezado: Any,
    estilo_celda: Any,
) -> list[list[Any]]:
    """Genera la matriz de celdas de la tabla PDF con encabezado y datos."""
    filas: list[list[Any]] = [
        [_celda_pdf(str(columna), estilo_encabezado) for columna in columnas],
    ]
    for registro in registros:
        filas.append(
            [
                _celda_pdf(_serializar_valor_celda(registro.get(columna)), estilo_celda)
                for columna in columnas
            ],
        )
    return filas


def _estilo_tabla_pdf() -> Any:
    """Define el estilo visual de la tabla de exportacion PDF."""
    from reportlab.lib import colors
    from reportlab.platypus import TableStyle

    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#B0B0B0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5F9")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ],
    )


class PdfExportador(GeneradorExportacion):
    """Generador de exportaciones en formato PDF."""

    def generar(
        self,
        registros: list[dict[str, Any]],
        parametros: dict[str, Any],
    ) -> bytes:
        """Genera un documento PDF tabular a partir de registros planos."""
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table

        buffer = io.BytesIO()
        documento = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=_PDF_MARGEN_PUNTOS,
            rightMargin=_PDF_MARGEN_PUNTOS,
            topMargin=_PDF_MARGEN_PUNTOS,
            bottomMargin=_PDF_MARGEN_PUNTOS,
        )
        estilos = getSampleStyleSheet()
        titulo = parametros.get("titulo", _PDF_TITULO_POR_DEFECTO)
        elementos: list[Any] = [Paragraph(str(titulo), estilos["Title"]), Spacer(1, 12)]

        if not registros:
            elementos.append(Paragraph(_PDF_MENSAJE_SIN_DATOS, estilos["Normal"]))
            documento.build(elementos)
            return buffer.getvalue()

        estilo_celda = ParagraphStyle(
            "CeldaExportacion",
            parent=estilos["Normal"],
            fontSize=_PDF_TAMANO_FUENTE_CELDA,
            leading=_PDF_TAMANO_FUENTE_CELDA + 2,
        )
        estilo_encabezado = ParagraphStyle(
            "EncabezadoExportacion",
            parent=estilo_celda,
            fontSize=_PDF_TAMANO_FUENTE_ENCABEZADO,
            textColor="white",
        )
        columnas = _obtener_columnas(registros)
        ancho_columna = documento.width / len(columnas)
        tabla = Table(
            _construir_matriz_pdf(registros, columnas, estilo_encabezado, estilo_celda),
            colWidths=[ancho_columna] * len(columnas),
            repeatRows=1,
        )
        tabla.setStyle(_estilo_tabla_pdf())
        elementos.append(tabla)
        documento.build(elementos)
        return buffer.getvalue()


def _fila_ods(valores: list[str]) -> Any:
    """Construye una fila ODS con celdas de texto."""
    from odf.table import TableCell, TableRow
    from odf.text import P

    fila = TableRow()
    for valor in valores:
        celda = TableCell(valuetype="string")
        celda.addElement(P(text=valor))
        fila.addElement(celda)
    return fila


class OdsExportador(GeneradorExportacion):
    """Generador de exportaciones en formato ODS (hoja de calculo abierta)."""

    def generar(
        self,
        registros: list[dict[str, Any]],
        parametros: dict[str, Any],
    ) -> bytes:
        """Genera una hoja de calculo ODS a partir de registros planos."""
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.table import Table

        documento = OpenDocumentSpreadsheet()
        tabla = Table(name=parametros.get("nombre_hoja", "Exportacion"))

        if registros:
            columnas = _obtener_columnas(registros)
            tabla.addElement(_fila_ods([str(columna) for columna in columnas]))
            for registro in registros:
                valores = [
                    _serializar_valor_celda(registro.get(columna))
                    for columna in columnas
                ]
                tabla.addElement(_fila_ods(valores))

        documento.spreadsheet.addElement(tabla)
        buffer = io.BytesIO()
        documento.write(buffer)
        return buffer.getvalue()


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


def generar_pdf(
    registros: list[dict[str, Any]],
    parametros: dict[str, Any] | None = None,
) -> bytes:
    """Genera exportacion PDF."""
    return PdfExportador().generar(registros, parametros or {})


def generar_ods(
    registros: list[dict[str, Any]],
    parametros: dict[str, Any] | None = None,
) -> bytes:
    """Genera exportacion ODS."""
    return OdsExportador().generar(registros, parametros or {})
