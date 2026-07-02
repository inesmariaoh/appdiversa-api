"""
Pruebas de servicios de catalogos parametrizables.
"""

from django.test import TestCase

from aplicaciones.catalogos.constantes import TiposCatalogo
from aplicaciones.catalogos.models import Catalogo, ItemCatalogo
from aplicaciones.catalogos.servicios import (
    crear_catalogo_si_no_existe,
    crear_item_catalogo_si_no_existe,
    listar_hijos_item_catalogo,
    obtener_items_catalogo,
)


class CatalogoServiciosTests(TestCase):
    """Pruebas de servicios de catalogos."""

    def test_crear_catalogo_si_no_existe(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="estratos",
            nombre="Estratos",
            tipo_catalogo=TiposCatalogo.SOCIOECONOMICO,
        )
        self.assertEqual(catalogo.codigo, "estratos")
        duplicado = crear_catalogo_si_no_existe(
            codigo="estratos",
            nombre="Estratos",
            tipo_catalogo=TiposCatalogo.SOCIOECONOMICO,
        )
        self.assertEqual(catalogo.pk, duplicado.pk)

    def test_crear_item_catalogo_si_no_existe(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="sexos_nacimiento",
            nombre="Sexos al nacer",
            tipo_catalogo=TiposCatalogo.DEMOGRAFICO,
        )
        item = crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="M",
            nombre="Masculino",
            valor="M",
        )
        self.assertEqual(item.codigo, "M")
        duplicado = crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="M",
            nombre="Masculino",
        )
        self.assertEqual(item.pk, duplicado.pk)

    def test_obtener_items_activos(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="grupos_etnicos",
            nombre="Grupos etnicos",
            tipo_catalogo=TiposCatalogo.DEMOGRAFICO,
        )
        crear_item_catalogo_si_no_existe(catalogo=catalogo, codigo="01", nombre="Activo")
        item_inactivo = crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="02",
            nombre="Inactivo",
        )
        item_inactivo.esta_activo = False
        item_inactivo.save(update_fields=["esta_activo"])

        items = obtener_items_catalogo("grupos_etnicos", solo_activos=True)
        self.assertEqual(items.count(), 1)
        self.assertEqual(items.first().codigo, "01")

    def test_filtrar_por_item_padre(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="municipios",
            nombre="Municipios",
            tipo_catalogo=TiposCatalogo.GEOGRAFICO,
        )
        departamento = crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="15",
            nombre="Boyaca",
        )
        crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="15001",
            nombre="Tunja",
            item_padre=departamento,
        )
        crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="11",
            nombre="Bogota",
        )

        items = obtener_items_catalogo("municipios", codigo_padre="15")
        self.assertEqual(items.count(), 1)
        self.assertEqual(items.first().codigo, "15001")

    def test_no_incluye_eliminados_logicamente(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="areas_residencia",
            nombre="Areas de residencia",
            tipo_catalogo=TiposCatalogo.SOCIOECONOMICO,
        )
        item = crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="URB",
            nombre="Urbana",
        )
        item.eliminar_logicamente()

        items = obtener_items_catalogo("areas_residencia")
        self.assertEqual(items.count(), 0)

    def test_listar_hijos_item_catalogo(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="tipos_discapacidad",
            nombre="Tipos de discapacidad",
            tipo_catalogo=TiposCatalogo.DISCAPACIDAD,
        )
        padre = crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="FIS",
            nombre="Fisica",
        )
        crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="FIS-01",
            nombre="Motriz",
            item_padre=padre,
        )

        hijos = listar_hijos_item_catalogo("tipos_discapacidad", "FIS")
        self.assertEqual(hijos.count(), 1)
        self.assertEqual(hijos.first().codigo, "FIS-01")

    def test_auditoria_no_rompe_creacion(self) -> None:
        catalogo = Catalogo.objects.create(
            codigo="orientaciones_sexuales",
            nombre="Orientaciones sexuales",
            tipo_catalogo=TiposCatalogo.IDENTIDAD,
        )
        item = ItemCatalogo.objects.create(
            catalogo=catalogo,
            codigo="HET",
            nombre="Heterosexual",
        )
        self.assertFalse(catalogo.esta_eliminado)
        self.assertFalse(item.esta_eliminado)
        self.assertIsNotNone(catalogo.fecha_creacion)
        self.assertIsNotNone(item.fecha_creacion)
