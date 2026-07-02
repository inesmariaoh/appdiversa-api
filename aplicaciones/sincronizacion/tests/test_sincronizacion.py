"""
Pruebas del motor de sincronizacion offline.
"""

import uuid
from datetime import datetime, timezone

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.models import RegistroAuditoria
from aplicaciones.comun.tests.helpers_seguridad import headers_sesion_anonima
from aplicaciones.respuestas.models import Respuesta
from aplicaciones.sesiones_anonimas.constantes import MensajesSesionApi
from aplicaciones.sincronizacion.constantes import MensajesSincronizacionApi
from aplicaciones.sincronizacion.models import (
    ConflictoSincronizacion,
    EstadoSincronizacion,
    OperacionSincronizacion,
    TipoConflicto,
)
from aplicaciones.sincronizacion.servicios import (
    OperacionEntrada,
    registrar_conflicto,
    registrar_operacion,
    sincronizar_batch,
    sincronizar_respuesta,
)
from aplicaciones.sincronizacion.tests.helpers import (
    construir_operacion,
    construir_payload_batch,
    crear_contexto_sincronizacion,
    crear_pregunta_adicional,
    crear_respuesta_con_uuid_local,
)
from aplicaciones.sincronizacion.validadores import calcular_checksum_operacion

URL_SINCRONIZACION = "/api/v1/sincronizacion/"


class SincronizacionServiciosTests(TestCase):
    """Pruebas de servicios de sincronizacion."""

    def test_sincronizacion_nueva_crea_respuesta(self) -> None:
        sesion, _, _, pregunta = crear_contexto_sincronizacion()
        uuid_local = uuid.uuid4()
        operacion = OperacionEntrada(
            uuid_local=uuid_local,
            codigo_pregunta=pregunta.codigo,
            valor=42,
            version_cliente=1,
            fecha_cliente=datetime(2026, 6, 28, 10, 0, tzinfo=timezone.utc),
            checksum=calcular_checksum_operacion(pregunta.codigo, 42, 1),
        )
        resultado = sincronizar_respuesta(sesion, "device-1", operacion)
        self.assertEqual(resultado.estado, EstadoSincronizacion.SINCRONIZADA)
        respuesta = Respuesta.objects.get(uuid_local=uuid_local)
        self.assertEqual(respuesta.valor_numero, 42)

    def test_respuesta_duplicada_no_actualiza(self) -> None:
        sesion, _, _, pregunta = crear_contexto_sincronizacion()
        uuid_local = uuid.uuid4()
        crear_respuesta_con_uuid_local(sesion, pregunta, uuid_local, 2, 10)
        operacion = OperacionEntrada(
            uuid_local=uuid_local,
            codigo_pregunta=pregunta.codigo,
            valor=99,
            version_cliente=2,
            fecha_cliente=datetime(2026, 6, 28, 10, 0, tzinfo=timezone.utc),
        )
        resultado = sincronizar_respuesta(sesion, "device-1", operacion)
        self.assertEqual(
            resultado.mensaje,
            MensajesSincronizacionApi.OPERACION_DUPLICADA,
        )
        respuesta = Respuesta.objects.get(uuid_local=uuid_local)
        self.assertEqual(int(respuesta.valor_numero), 10)

    def test_uuid_local_repetido_con_version_mayor_actualiza(self) -> None:
        sesion, _, _, pregunta = crear_contexto_sincronizacion()
        uuid_local = uuid.uuid4()
        crear_respuesta_con_uuid_local(sesion, pregunta, uuid_local, 1, 5)
        operacion = OperacionEntrada(
            uuid_local=uuid_local,
            codigo_pregunta=pregunta.codigo,
            valor=20,
            version_cliente=3,
            fecha_cliente=datetime(2026, 6, 28, 11, 0, tzinfo=timezone.utc),
        )
        resultado = sincronizar_respuesta(sesion, "device-1", operacion)
        self.assertEqual(resultado.estado, EstadoSincronizacion.SINCRONIZADA)
        respuesta = Respuesta.objects.get(uuid_local=uuid_local)
        self.assertEqual(int(respuesta.valor_numero), 20)
        self.assertEqual(respuesta.version_cliente, 3)

    def test_version_menor_registra_conflicto(self) -> None:
        sesion, _, _, pregunta = crear_contexto_sincronizacion()
        uuid_local = uuid.uuid4()
        crear_respuesta_con_uuid_local(sesion, pregunta, uuid_local, 5, 50)
        operacion = OperacionEntrada(
            uuid_local=uuid_local,
            codigo_pregunta=pregunta.codigo,
            valor=10,
            version_cliente=2,
            fecha_cliente=datetime(2026, 6, 28, 10, 0, tzinfo=timezone.utc),
        )
        resultado = sincronizar_respuesta(sesion, "device-1", operacion)
        self.assertEqual(resultado.estado, EstadoSincronizacion.CONFLICTO)
        self.assertTrue(
            ConflictoSincronizacion.objects.filter(
                uuid_local=uuid_local,
                tipo_conflicto=TipoConflicto.VERSION,
            ).exists(),
        )

    def test_checksum_invalido_retorna_error(self) -> None:
        sesion, _, _, pregunta = crear_contexto_sincronizacion()
        uuid_local = uuid.uuid4()
        operacion = OperacionEntrada(
            uuid_local=uuid_local,
            codigo_pregunta=pregunta.codigo,
            valor=7,
            version_cliente=1,
            fecha_cliente=datetime(2026, 6, 28, 10, 0, tzinfo=timezone.utc),
            checksum="checksum-invalido",
        )
        resultado = sincronizar_respuesta(sesion, "device-1", operacion)
        self.assertEqual(resultado.estado, EstadoSincronizacion.ERROR)
        self.assertEqual(resultado.mensaje, MensajesSincronizacionApi.CHECKSUM_INVALIDO)

    def test_batch_completo_exitoso(self) -> None:
        sesion, _, _, pregunta = crear_contexto_sincronizacion()
        pregunta2 = crear_pregunta_adicional(sesion, "P_SYNC_2")
        operaciones = [
            construir_operacion(uuid.uuid4(), pregunta.codigo, 1, 1),
            construir_operacion(uuid.uuid4(), pregunta2.codigo, 2, 1),
        ]
        resultado = sincronizar_batch(
            sesion.uuid_sesion,
            "device-batch",
            "1.0.0",
            operaciones,
        )
        self.assertEqual(resultado.operaciones_procesadas, 2)
        self.assertEqual(resultado.operaciones_actualizadas, 2)
        self.assertEqual(resultado.errores, [])

    def test_batch_parcialmente_exitoso(self) -> None:
        sesion, _, _, pregunta = crear_contexto_sincronizacion()
        operaciones = [
            construir_operacion(uuid.uuid4(), pregunta.codigo, 15, 1),
            construir_operacion(uuid.uuid4(), "P_INEXISTENTE", 99, 1),
        ]
        resultado = sincronizar_batch(
            sesion.uuid_sesion,
            "device-batch",
            "1.0.0",
            operaciones,
        )
        self.assertEqual(resultado.operaciones_procesadas, 2)
        self.assertEqual(len(resultado.errores), 1)
        self.assertEqual(resultado.operaciones_actualizadas, 1)

    def test_respuesta_eliminada_retorna_error(self) -> None:
        sesion, _, _, pregunta = crear_contexto_sincronizacion()
        uuid_local = uuid.uuid4()
        respuesta = crear_respuesta_con_uuid_local(sesion, pregunta, uuid_local, 1, 8)
        respuesta.esta_eliminado = True
        respuesta.save(update_fields=["esta_eliminado"])
        operacion = OperacionEntrada(
            uuid_local=uuid_local,
            codigo_pregunta=pregunta.codigo,
            valor=12,
            version_cliente=2,
            fecha_cliente=datetime(2026, 6, 28, 10, 0, tzinfo=timezone.utc),
        )
        resultado = sincronizar_respuesta(sesion, "device-1", operacion)
        self.assertEqual(resultado.estado, EstadoSincronizacion.ERROR)
        self.assertEqual(resultado.mensaje, MensajesSincronizacionApi.RESPUESTA_ELIMINADA)

    def test_respuesta_actualizada_incrementa_version(self) -> None:
        sesion, _, _, pregunta = crear_contexto_sincronizacion()
        uuid_local = uuid.uuid4()
        crear_respuesta_con_uuid_local(sesion, pregunta, uuid_local, 1, 3)
        operacion = OperacionEntrada(
            uuid_local=uuid_local,
            codigo_pregunta=pregunta.codigo,
            valor=30,
            version_cliente=2,
            fecha_cliente=datetime(2026, 6, 28, 12, 0, tzinfo=timezone.utc),
        )
        sincronizar_respuesta(sesion, "device-1", operacion)
        respuesta = Respuesta.objects.get(uuid_local=uuid_local)
        self.assertEqual(respuesta.version_cliente, 2)
        self.assertGreater(respuesta.version_respuesta, 1)

    def test_registrar_operacion(self) -> None:
        sesion, _, _, pregunta = crear_contexto_sincronizacion()
        operacion = OperacionEntrada(
            uuid_local=uuid.uuid4(),
            codigo_pregunta=pregunta.codigo,
            valor=1,
            version_cliente=1,
            fecha_cliente=datetime(2026, 6, 28, 10, 0, tzinfo=timezone.utc),
        )
        registro = registrar_operacion(
            sesion.uuid_sesion,
            operacion,
            "device-admin",
            EstadoSincronizacion.SINCRONIZADA,
            "test",
        )
        self.assertEqual(registro.estado, EstadoSincronizacion.SINCRONIZADA)

    def test_registrar_conflicto(self) -> None:
        sesion, _, _, pregunta = crear_contexto_sincronizacion()
        uuid_local = uuid.uuid4()
        respuesta = crear_respuesta_con_uuid_local(sesion, pregunta, uuid_local, 1, 5)
        conflicto = registrar_conflicto(
            uuid_local,
            respuesta,
            TipoConflicto.VERSION,
            10,
            5,
            "servidor",
        )
        self.assertEqual(conflicto.tipo_conflicto, TipoConflicto.VERSION)
        self.assertTrue(
            RegistroAuditoria.objects.filter(
                accion=AccionAuditoria.CONFLICTO,
            ).exists(),
        )

    def test_auditoria_sincronizacion_batch(self) -> None:
        sesion, _, _, pregunta = crear_contexto_sincronizacion()
        sincronizar_batch(
            sesion.uuid_sesion,
            "device-audit",
            "1.0.0",
            [construir_operacion(uuid.uuid4(), pregunta.codigo, 7, 1)],
        )
        self.assertTrue(
            RegistroAuditoria.objects.filter(
                accion=AccionAuditoria.SINCRONIZAR,
            ).exists(),
        )


class SincronizacionApiTests(TestCase):
    """Pruebas del endpoint de sincronizacion."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.sesion, self.uuid_sesion, self.token, self.pregunta = (
            crear_contexto_sincronizacion()
        )

    def test_endpoint_ok(self) -> None:
        payload = construir_payload_batch(
            self.uuid_sesion,
            self.token,
            [construir_operacion(uuid.uuid4(), self.pregunta.codigo, 25, 1)],
        )
        respuesta = self.cliente.post(
            URL_SINCRONIZACION,
            payload,
            format="json",
            **headers_sesion_anonima(self.uuid_sesion, self.token),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()["operaciones_procesadas"], 1)

    def test_endpoint_403_token_invalido(self) -> None:
        payload = construir_payload_batch(
            self.uuid_sesion,
            "token-invalido",
            [construir_operacion(uuid.uuid4(), self.pregunta.codigo, 1, 1)],
        )
        respuesta = self.cliente.post(URL_SINCRONIZACION, payload, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_endpoint_404_sesion_inexistente(self) -> None:
        uuid_falso = str(uuid.uuid4())
        token = self.token
        payload = construir_payload_batch(
            uuid_falso,
            token,
            [construir_operacion(uuid.uuid4(), self.pregunta.codigo, 1, 1)],
        )
        respuesta = self.cliente.post(
            URL_SINCRONIZACION,
            payload,
            format="json",
            **headers_sesion_anonima(uuid_falso, token),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            respuesta.json()["detalle"],
            MensajesSesionApi.SESION_NO_EXISTE,
        )

    def test_endpoint_404_ruta_inexistente(self) -> None:
        respuesta = self.cliente.post(
            "/api/v1/sincronizacion/extra/",
            {},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)

    def test_endpoint_checksum_invalido(self) -> None:
        operacion = construir_operacion(
            uuid.uuid4(),
            self.pregunta.codigo,
            33,
            1,
            incluir_checksum=False,
        )
        operacion["checksum"] = "checksum-mal"
        payload = construir_payload_batch(
            self.uuid_sesion,
            self.token,
            [operacion],
        )
        respuesta = self.cliente.post(
            URL_SINCRONIZACION,
            payload,
            format="json",
            **headers_sesion_anonima(self.uuid_sesion, self.token),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.json()["errores"]), 1)

    def test_operacion_sincronizacion_registrada_en_batch(self) -> None:
        payload = construir_payload_batch(
            self.uuid_sesion,
            self.token,
            [construir_operacion(uuid.uuid4(), self.pregunta.codigo, 44, 1)],
        )
        self.cliente.post(
            URL_SINCRONIZACION,
            payload,
            format="json",
            **headers_sesion_anonima(self.uuid_sesion, self.token),
        )
        self.assertTrue(OperacionSincronizacion.objects.exists())

    def test_conflicto_en_batch(self) -> None:
        uuid_local = uuid.uuid4()
        crear_respuesta_con_uuid_local(self.sesion, self.pregunta, uuid_local, 5, 100)
        payload = construir_payload_batch(
            self.uuid_sesion,
            self.token,
            [construir_operacion(uuid_local, self.pregunta.codigo, 1, 2)],
        )
        respuesta = self.cliente.post(
            URL_SINCRONIZACION,
            payload,
            format="json",
            **headers_sesion_anonima(self.uuid_sesion, self.token),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.json()["conflictos"]), 1)
