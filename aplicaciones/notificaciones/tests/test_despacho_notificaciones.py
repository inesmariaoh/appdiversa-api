"""
Pruebas del despacho diferido de notificaciones (sincrono y asincrono).
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from aplicaciones.notificaciones.excepciones import PlantillaNotificacionNoEncontradaError
from aplicaciones.notificaciones.servicios import despachar_notificacion

CODIGO_PLANTILLA = "bienvenida_correo"
DESTINATARIO = "destino@example.com"
VARIABLES = {"nombre": "Ana"}


@override_settings(NOTIFICACIONES_USAR_CELERY=False)
class DespachoSincronoTests(TestCase):
    """Pruebas del despacho cuando la cola asincrona esta deshabilitada."""

    @patch("aplicaciones.notificaciones.servicios.enviar_notificacion")
    def test_envio_ocurre_despues_del_commit(self, mock_enviar: MagicMock) -> None:
        with self.captureOnCommitCallbacks(execute=True):
            despachar_notificacion(
                codigo_plantilla=CODIGO_PLANTILLA,
                destinatario=DESTINATARIO,
                variables=VARIABLES,
            )
            mock_enviar.assert_not_called()
        mock_enviar.assert_called_once_with(
            codigo_plantilla=CODIGO_PLANTILLA,
            destinatario=DESTINATARIO,
            variables=VARIABLES,
            reply_to=None,
        )

    @patch(
        "aplicaciones.notificaciones.servicios.enviar_notificacion",
        side_effect=PlantillaNotificacionNoEncontradaError(),
    )
    def test_plantilla_faltante_no_propaga_error(self, mock_enviar: MagicMock) -> None:
        with self.captureOnCommitCallbacks(execute=True):
            despachar_notificacion(
                codigo_plantilla=CODIGO_PLANTILLA,
                destinatario=DESTINATARIO,
            )
        mock_enviar.assert_called_once()


@override_settings(NOTIFICACIONES_USAR_CELERY=True)
class DespachoAsincronoTests(TestCase):
    """Pruebas del despacho cuando la cola asincrona esta habilitada."""

    @patch("aplicaciones.notificaciones.tasks.enviar_notificacion_async")
    @patch("aplicaciones.notificaciones.servicios.enviar_notificacion")
    def test_encola_en_celery_sin_envio_sincrono(
        self,
        mock_enviar: MagicMock,
        mock_task: MagicMock,
    ) -> None:
        with self.captureOnCommitCallbacks(execute=True):
            despachar_notificacion(
                codigo_plantilla=CODIGO_PLANTILLA,
                destinatario=DESTINATARIO,
                variables=VARIABLES,
            )
        mock_task.delay.assert_called_once_with(
            codigo_plantilla=CODIGO_PLANTILLA,
            destinatario=DESTINATARIO,
            variables=VARIABLES,
            reply_to=None,
        )
        mock_enviar.assert_not_called()

    @patch("aplicaciones.notificaciones.tasks.enviar_notificacion_async")
    @patch("aplicaciones.notificaciones.servicios.enviar_notificacion")
    def test_broker_no_disponible_envia_sincrono(
        self,
        mock_enviar: MagicMock,
        mock_task: MagicMock,
    ) -> None:
        from kombu.exceptions import OperationalError

        mock_task.delay.side_effect = OperationalError("broker caido")
        with self.captureOnCommitCallbacks(execute=True):
            despachar_notificacion(
                codigo_plantilla=CODIGO_PLANTILLA,
                destinatario=DESTINATARIO,
                variables=VARIABLES,
            )
        mock_enviar.assert_called_once_with(
            codigo_plantilla=CODIGO_PLANTILLA,
            destinatario=DESTINATARIO,
            variables=VARIABLES,
            reply_to=None,
        )
