"""
Pruebas de la API administrativa de resolucion manual de conflictos.
"""

import uuid
from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.sincronizacion.models import (
    ConflictoSincronizacion,
    ResolucionConflicto,
    TipoConflicto,
)
from aplicaciones.sincronizacion.tests.helpers import (
    crear_contexto_sincronizacion,
    crear_respuesta_con_uuid_local,
)
from aplicaciones.usuarios.tests.helpers import (
    GRUPO_ADMIN,
    autenticar_cliente,
    crear_usuario_prueba,
    inicializar_entorno_usuarios,
)

URL_CONFLICTOS = "/api/v1/admin/sincronizacion/conflictos/"
VALOR_SERVIDOR = 10
VALOR_CLIENTE = 20
VALOR_MANUAL = 55


def _url_resolver(conflicto_uuid: uuid.UUID) -> str:
    """Construye la URL de resolucion de un conflicto."""
    return f"{URL_CONFLICTOS}{conflicto_uuid}/resolver/"


class ConflictosAdminTests(TestCase):
    """Pruebas del listado y resolucion de conflictos de sincronizacion."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()
        self._crear_conflicto_con_respuesta()

    def _crear_conflicto_con_respuesta(self) -> None:
        sesion, _, _, pregunta = crear_contexto_sincronizacion()
        self.respuesta = crear_respuesta_con_uuid_local(
            sesion,
            pregunta,
            uuid.uuid4(),
            version_cliente=1,
            valor_numero=VALOR_SERVIDOR,
        )
        self.conflicto = ConflictoSincronizacion.objects.create(
            uuid_local=self.respuesta.uuid_local,
            respuesta=self.respuesta,
            tipo_conflicto=TipoConflicto.VERSION,
            valor_cliente={"valor": VALOR_CLIENTE},
            valor_servidor={"valor": VALOR_SERVIDOR},
            resolucion="",
        )

    def _autenticar_admin(self) -> None:
        crear_usuario_prueba("admin_sync", grupo=GRUPO_ADMIN)
        autenticar_cliente(self.cliente, "admin_sync")

    def test_listado_requiere_autenticacion(self) -> None:
        respuesta = self.cliente.get(URL_CONFLICTOS)
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_lista_conflictos_paginados(self) -> None:
        self._autenticar_admin()
        respuesta = self.cliente.get(URL_CONFLICTOS)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(respuesta.data["count"], 1)

    def test_resolver_cliente_aplica_valor(self) -> None:
        self._autenticar_admin()
        respuesta = self.cliente.post(
            _url_resolver(self.conflicto.uuid),
            {"resolucion": ResolucionConflicto.CLIENTE},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.respuesta.refresh_from_db()
        self.assertEqual(self.respuesta.valor_numero, Decimal(VALOR_CLIENTE))
        self.assertEqual(self.respuesta.version_respuesta, 2)

    def test_resolver_servidor_no_cambia_valor(self) -> None:
        self._autenticar_admin()
        respuesta = self.cliente.post(
            _url_resolver(self.conflicto.uuid),
            {"resolucion": ResolucionConflicto.SERVIDOR},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.respuesta.refresh_from_db()
        self.assertEqual(self.respuesta.valor_numero, Decimal(VALOR_SERVIDOR))

    def test_resolver_manual_aplica_valor(self) -> None:
        self._autenticar_admin()
        respuesta = self.cliente.post(
            _url_resolver(self.conflicto.uuid),
            {"resolucion": ResolucionConflicto.MANUAL, "valor_manual": VALOR_MANUAL},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.respuesta.refresh_from_db()
        self.assertEqual(self.respuesta.valor_numero, Decimal(VALOR_MANUAL))

    def test_resolver_manual_sin_valor_retorna_400(self) -> None:
        self._autenticar_admin()
        respuesta = self.cliente.post(
            _url_resolver(self.conflicto.uuid),
            {"resolucion": ResolucionConflicto.MANUAL},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resolver_conflicto_inexistente_retorna_404(self) -> None:
        self._autenticar_admin()
        respuesta = self.cliente.post(
            _url_resolver(uuid.uuid4()),
            {"resolucion": ResolucionConflicto.SERVIDOR},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
