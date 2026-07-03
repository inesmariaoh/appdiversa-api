"""
Pruebas de la migracion que unifica el catalogo geografico legado.
"""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

MIGRACION_ORIGEN = ("formularios", "0018_disc001_periodo_condicional")
MIGRACION_DATOS = ("formularios", "0019_migrar_catalogo_geografico_a_catalogos")
MIGRACION_FINAL = ("formularios", "0020_delete_catalogogeografico")


class MigracionGeograficaTests(TransactionTestCase):
    """Verifica el traslado de datos geograficos hacia la app catalogos."""

    def tearDown(self) -> None:
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate([MIGRACION_FINAL])

    def test_migra_registros_a_catalogos(self) -> None:
        executor = MigrationExecutor(connection)
        executor.migrate([MIGRACION_ORIGEN])
        estado_origen = executor.loader.project_state([MIGRACION_ORIGEN]).apps
        catalogo_geografico = estado_origen.get_model("formularios", "CatalogoGeografico")

        catalogo_geografico.objects.create(tipo="pais", codigo="CO", nombre="Colombia")
        catalogo_geografico.objects.create(
            tipo="departamento",
            codigo="05",
            nombre="Antioquia",
            codigo_padre="CO",
        )

        executor.loader.build_graph()
        executor.migrate([MIGRACION_DATOS])
        estado_datos = executor.loader.project_state([MIGRACION_DATOS]).apps
        catalogo = estado_datos.get_model("catalogos", "Catalogo")
        item_catalogo = estado_datos.get_model("catalogos", "ItemCatalogo")

        self.assertTrue(catalogo.objects.filter(codigo="geo_pais").exists())
        self.assertTrue(catalogo.objects.filter(codigo="geo_departamento").exists())

        item_departamento = item_catalogo.objects.get(codigo="05")
        self.assertEqual(item_departamento.nombre, "Antioquia")
        self.assertEqual(item_departamento.metadatos["nivel"], "departamento")
        self.assertEqual(item_departamento.metadatos["codigo_padre"], "CO")
