"""
Migra los registros del modelo legado CatalogoGeografico hacia la app catalogos.

Cada nivel geografico se representa como un catalogo generico y cada registro
como un item de catalogo. La relacion jerarquica original se conserva en el
campo de metadatos del item para no perder informacion durante la unificacion.
"""

from django.db import migrations

TIPO_CATALOGO_GEOGRAFICO = "geografico"
PREFIJO_CODIGO_CATALOGO = "geo_"


def _construir_metadatos(codigo_padre: str, nivel: str) -> dict:
    """Arma los metadatos del item preservando el nivel y el codigo padre."""
    metadatos = {"nivel": nivel}
    if codigo_padre:
        metadatos["codigo_padre"] = codigo_padre
    return metadatos


def migrar_catalogo_geografico(apps, schema_editor) -> None:
    """Copia los registros geograficos legados a la estructura generica."""
    modelo_geografico = apps.get_model("formularios", "CatalogoGeografico")
    modelo_catalogo = apps.get_model("catalogos", "Catalogo")
    modelo_item = apps.get_model("catalogos", "ItemCatalogo")

    catalogos_por_tipo: dict[str, object] = {}
    for registro in modelo_geografico.objects.all().iterator():
        catalogo = catalogos_por_tipo.get(registro.tipo)
        if catalogo is None:
            catalogo, _ = modelo_catalogo.objects.get_or_create(
                codigo=f"{PREFIJO_CODIGO_CATALOGO}{registro.tipo}",
                defaults={
                    "nombre": registro.tipo.replace("_", " ").title(),
                    "tipo_catalogo": TIPO_CATALOGO_GEOGRAFICO,
                    "es_sistema": True,
                },
            )
            catalogos_por_tipo[registro.tipo] = catalogo

        modelo_item.objects.get_or_create(
            catalogo=catalogo,
            codigo=registro.codigo,
            defaults={
                "nombre": registro.nombre,
                "esta_activo": registro.esta_activo,
                "metadatos": _construir_metadatos(registro.codigo_padre, registro.tipo),
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("formularios", "0018_disc001_periodo_condicional"),
        ("catalogos", "0002_alter_catalogo_options_alter_itemcatalogo_options"),
    ]

    operations = [
        migrations.RunPython(
            migrar_catalogo_geografico,
            migrations.RunPython.noop,
        ),
    ]
