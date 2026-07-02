"""
Migracion que agrega orden de visualizacion a formularios.
"""

from django.db import migrations, models


def asignar_orden_inicial_formularios(apps, schema_editor) -> None:
    """Asigna un orden inicial segun el nombre de cada formulario existente."""
    formulario_model = apps.get_model("formularios", "Formulario")
    formularios = formulario_model.objects.order_by("nombre", "pk")
    for indice, formulario in enumerate(formularios, start=1):
        formulario.orden = indice
        formulario.save(update_fields=["orden"])


class Migration(migrations.Migration):

    dependencies = [
        ("formularios", "0006_formulario_imagen_portada_repositorio"),
    ]

    operations = [
        migrations.AddField(
            model_name="formulario",
            name="orden",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.RunPython(
            asignar_orden_inicial_formularios,
            migrations.RunPython.noop,
        ),
        migrations.AlterModelOptions(
            name="formulario",
            options={
                "ordering": ["orden", "nombre"],
                "verbose_name": "Formulario",
                "verbose_name_plural": "Formularios",
            },
        ),
        migrations.AddIndex(
            model_name="formulario",
            index=models.Index(fields=["orden"], name="formularios_orden_4b8f2a_idx"),
        ),
    ]
