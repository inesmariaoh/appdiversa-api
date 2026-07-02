"""
Pruebas de API de catalogos parametrizables.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.catalogos.constantes import TiposCatalogo
from aplicaciones.catalogos.models import Catalogo, ItemCatalogo
from aplicaciones.catalogos.servicios import (
    crear_catalogo_si_no_existe,
    crear_item_catalogo_si_no_existe,
)

URL_CATALOGOS = "/api/v1/catalogos/"


class CatalogosApiTests(TestCase):
    """Pruebas de endpoints publicos de catalogos."""

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_endpoint_lista_catalogos(self) -> None:
        Catalogo.objects.create(
            codigo="paises",
            nombre="Paises",
            tipo_catalogo=TiposCatalogo.GEOGRAFICO,
            esta_activo=True,
        )
        Catalogo.objects.create(
            codigo="inactivo",
            nombre="Inactivo",
            tipo_catalogo=TiposCatalogo.GENERAL,
            esta_activo=False,
        )
        respuesta = self.cliente.get(URL_CATALOGOS)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.json()), 1)
        self.assertEqual(respuesta.json()[0]["codigo"], "paises")

    def test_endpoint_lista_items(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="departamentos",
            nombre="Departamentos",
            tipo_catalogo=TiposCatalogo.GEOGRAFICO,
        )
        crear_item_catalogo_si_no_existe(catalogo=catalogo, codigo="15", nombre="Boyaca")

        respuesta = self.cliente.get(f"{URL_CATALOGOS}departamentos/items/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.json()), 1)
        self.assertEqual(respuesta.json()[0]["codigo"], "15")

    def test_endpoint_lista_hijos(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="municipios",
            nombre="Municipios",
            tipo_catalogo=TiposCatalogo.GEOGRAFICO,
        )
        padre = crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="15",
            nombre="Boyaca",
        )
        crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="15001",
            nombre="Tunja",
            item_padre=padre,
        )

        respuesta = self.cliente.get(
            f"{URL_CATALOGOS}municipios/items/15/hijos/",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.json()), 1)
        self.assertEqual(respuesta.json()[0]["codigo"], "15001")

    def test_endpoint_filtra_items_por_padre(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="municipios_filtro",
            nombre="Municipios filtro",
            tipo_catalogo=TiposCatalogo.GEOGRAFICO,
        )
        padre = crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="15",
            nombre="Boyaca",
        )
        crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="15001",
            nombre="Tunja",
            item_padre=padre,
        )
        crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="11",
            nombre="Bogota",
        )

        respuesta = self.cliente.get(
            f"{URL_CATALOGOS}municipios_filtro/items/",
            {"codigo_padre": "15"},
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.json()), 1)
        self.assertEqual(respuesta.json()[0]["codigo"], "15001")

    def test_no_retorna_eliminados_logicamente(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="estratos",
            nombre="Estratos",
            tipo_catalogo=TiposCatalogo.SOCIOECONOMICO,
        )
        item = crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="1",
            nombre="Estrato 1",
        )
        item.eliminar_logicamente()
        catalogo.eliminar_logicamente()

        respuesta_catalogos = self.cliente.get(URL_CATALOGOS)
        self.assertEqual(respuesta_catalogos.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta_catalogos.json()), 0)

        respuesta_items = self.cliente.get(f"{URL_CATALOGOS}estratos/items/")
        self.assertEqual(respuesta_items.status_code, status.HTTP_404_NOT_FOUND)

    def test_endpoint_items_filtra_por_busqueda(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="ocupaciones",
            nombre="Ocupaciones",
            tipo_catalogo=TiposCatalogo.GENERAL,
        )
        crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="DOC",
            nombre="Doctor",
        )
        crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="ENG",
            nombre="Ingeniero",
        )

        respuesta = self.cliente.get(
            f"{URL_CATALOGOS}ocupaciones/items/",
            {"busqueda": "Doctor"},
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.json()), 1)
        self.assertEqual(respuesta.json()[0]["codigo"], "DOC")

    def test_endpoint_items_respeta_limite(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="estratos_lim",
            nombre="Estratos limite",
            tipo_catalogo=TiposCatalogo.SOCIOECONOMICO,
        )
        for indice in range(1, 6):
            crear_item_catalogo_si_no_existe(
                catalogo=catalogo,
                codigo=str(indice),
                nombre=f"Estrato {indice}",
            )

        respuesta = self.cliente.get(
            f"{URL_CATALOGOS}estratos_lim/items/",
            {"limite": 2},
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.json()), 2)

    def test_endpoint_items_no_permite_limite_mayor_a_1000(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="items_limite_max",
            nombre="Items limite max",
            tipo_catalogo=TiposCatalogo.GENERAL,
        )
        for indice in range(1, 4):
            crear_item_catalogo_si_no_existe(
                catalogo=catalogo,
                codigo=f"I{indice}",
                nombre=f"Item {indice}",
            )

        respuesta = self.cliente.get(
            f"{URL_CATALOGOS}items_limite_max/items/",
            {"limite": 2000},
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.json()), 3)

    def test_items_no_incluyen_contenido_accesible_por_defecto(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="tipos_discapacidad",
            nombre="Tipos discapacidad",
            tipo_catalogo=TiposCatalogo.GENERAL,
        )
        crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="visual",
            nombre="Visual",
        )

        respuesta = self.cliente.get(f"{URL_CATALOGOS}tipos_discapacidad/items/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertNotIn("contenido_accesible", respuesta.json()[0])

    def test_items_incluyen_contenido_accesible_con_parametro(self) -> None:
        from aplicaciones.internacionalizacion.models import Idioma, TraduccionContenido
        from aplicaciones.internacionalizacion.servicios import resolver_uuid_entidad

        Idioma.objects.create(
            codigo_iso="es",
            nombre="Espanol",
            nombre_nativo="Espanol",
            es_predeterminado=True,
        )
        Idioma.objects.create(
            codigo_iso="en",
            nombre="Ingles",
            nombre_nativo="English",
        )
        catalogo = crear_catalogo_si_no_existe(
            codigo="tipos_discap_i18n",
            nombre="Tipos discapacidad i18n",
            tipo_catalogo=TiposCatalogo.GENERAL,
        )
        item = crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="auditiva",
            nombre="Auditiva",
        )
        uuid_item = resolver_uuid_entidad(item, "ItemCatalogo")
        TraduccionContenido.objects.create(
            idioma=Idioma.objects.get(codigo_iso="en"),
            entidad="ItemCatalogo",
            entidad_uuid=uuid_item,
            campo="nombre",
            valor_traducido="Hearing",
            lectura_facil="Problemas de oido",
            esta_activa=True,
        )

        respuesta = self.cliente.get(
            f"{URL_CATALOGOS}tipos_discap_i18n/items/",
            {"idioma": "en", "incluir_accesibilidad": "true"},
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        item_respuesta = respuesta.json()[0]
        self.assertIn("contenido_accesible", item_respuesta)
        self.assertEqual(
            item_respuesta["contenido_accesible"]["nombre"]["lectura_facil"],
            "Problemas de oido",
        )
