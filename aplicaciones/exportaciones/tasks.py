"""
Tareas asincronas del motor de exportaciones.
"""

from typing import Any

from celery import shared_task

from aplicaciones.exportaciones.servicios import exportar_analitica, exportar_respuestas


@shared_task(name="exportaciones.generar_respuestas")
def generar_exportacion_respuestas_async(
    formato: str,
    parametros: dict[str, Any] | None = None,
    usuario: str = "",
) -> str:
    """Genera una exportacion de respuestas en segundo plano y retorna su uuid."""
    exportacion = exportar_respuestas(formato, parametros, usuario)
    return str(exportacion.uuid)


@shared_task(name="exportaciones.generar_analitica")
def generar_exportacion_analitica_async(
    formato: str,
    parametros: dict[str, Any] | None = None,
    usuario: str = "",
) -> str:
    """Genera una exportacion analitica en segundo plano y retorna su uuid."""
    exportacion = exportar_analitica(formato, parametros, usuario)
    return str(exportacion.uuid)
