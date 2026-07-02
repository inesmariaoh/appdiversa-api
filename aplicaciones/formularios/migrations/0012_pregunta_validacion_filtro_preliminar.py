"""Migracion de campos de validacion para preguntas filtro/preliminares."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("formularios", "0011_alter_catalogogeografico_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="pregunta",
            name="bloquea_continuacion_si_no_cumple",
            field=models.BooleanField(
                default=True,
                help_text="Indica si el incumplimiento del filtro bloquea el ingreso al formulario.",
            ),
        ),
        migrations.AddField(
            model_name="pregunta",
            name="mensaje_no_cumple",
            field=models.TextField(
                blank=True,
                help_text="Mensaje visible cuando la respuesta no cumple la condicion del filtro.",
            ),
        ),
        migrations.AddField(
            model_name="pregunta",
            name="tipo_validacion_filtro",
            field=models.CharField(
                blank=True,
                choices=[
                    ("rango_edad", "Rango de edad"),
                    ("opcion_exacta", "Opción exacta"),
                    ("lista_opciones", "Lista de opciones"),
                    ("rango_numerico", "Rango numérico"),
                    ("booleano", "Booleano"),
                ],
                default="",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="pregunta",
            name="valor_filtro_esperado",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
