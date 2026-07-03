"""
Pruebas de las tareas asincronas del motor de exportaciones.
"""

import uuid
from unittest.mock import MagicMock, patch

from django.test import TestCase

from aplicaciones.exportaciones.tasks import (
    generar_exportacion_analitica_async,
    generar_exportacion_respuestas_async,
)


class ExportacionTasksTests(TestCase):
    """Pruebas de las tareas de generacion de exportaciones."""

    @patch("aplicaciones.exportaciones.tasks.exportar_respuestas")
    def test_tarea_respuestas_delega_en_servicio(self, mock_exportar: MagicMock) -> None:
        identificador = uuid.uuid4()
        mock_exportar.return_value = MagicMock(uuid=identificador)
        resultado = generar_exportacion_respuestas_async.delay("csv", {"a": 1}, "admin")
        self.assertEqual(resultado.get(), str(identificador))
        mock_exportar.assert_called_once_with("csv", {"a": 1}, "admin")

    @patch("aplicaciones.exportaciones.tasks.exportar_analitica")
    def test_tarea_analitica_delega_en_servicio(self, mock_exportar: MagicMock) -> None:
        identificador = uuid.uuid4()
        mock_exportar.return_value = MagicMock(uuid=identificador)
        resultado = generar_exportacion_analitica_async.delay("json")
        self.assertEqual(resultado.get(), str(identificador))
        mock_exportar.assert_called_once_with("json", None, "")
