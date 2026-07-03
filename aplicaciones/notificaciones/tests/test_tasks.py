"""
Pruebas de las tareas asincronas del motor de notificaciones.
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from aplicaciones.notificaciones.tasks import enviar_notificacion_async


class EnviarNotificacionTaskTests(TestCase):
    """Pruebas de la tarea de envio de notificaciones."""

    @patch("aplicaciones.notificaciones.tasks.enviar_notificacion")
    def test_task_delega_en_servicio(self, mock_enviar: MagicMock) -> None:
        mock_enviar.return_value = MagicMock(pk=7)
        resultado = enviar_notificacion_async.delay(
            "codigo_plantilla",
            "destino@example.com",
            {"nombre": "Ana"},
        )
        self.assertEqual(resultado.get(), 7)
        mock_enviar.assert_called_once_with(
            codigo_plantilla="codigo_plantilla",
            destinatario="destino@example.com",
            variables={"nombre": "Ana"},
            reply_to=None,
        )
