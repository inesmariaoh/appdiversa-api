"""
Agrega indicador tiene_tooltip y activa registros existentes con texto.
"""

from django.db import migrations, models


def activar_tiene_tooltip_desde_texto(apps, schema_editor) -> None:
    """Marca tiene_tooltip cuando ya existe texto almacenado."""
    pregunta_model = apps.get_model("formularios", "Pregunta")
    opcion_model = apps.get_model("formularios", "OpcionRespuesta")

    for pregunta in pregunta_model.objects.all().iterator():
        if str(pregunta.tooltip).strip():
            pregunta.tiene_tooltip = True
            pregunta.save(update_fields=["tiene_tooltip"])

    for opcion in opcion_model.objects.all().iterator():
        if str(opcion.tooltip).strip():
            opcion.tiene_tooltip = True
            opcion.save(update_fields=["tiene_tooltip"])


class Migration(migrations.Migration):

    dependencies = [
        ("formularios", "0008_rename_formularios_orden_4b8f2a_idx_formularios_orden_6d3759_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="pregunta",
            name="tiene_tooltip",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="opcionrespuesta",
            name="tiene_tooltip",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(
            activar_tiene_tooltip_desde_texto,
            migrations.RunPython.noop,
        ),
    ]
