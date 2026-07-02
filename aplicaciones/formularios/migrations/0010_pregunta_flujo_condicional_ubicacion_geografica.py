"""
Campos de flujo condicional y ubicacion geografica en preguntas.
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Agrega soporte de visibilidad condicional y ubicacion geografica compuesta."""

    dependencies = [
        ("formularios", "0009_pregunta_opcion_tiene_tooltip"),
    ]

    operations = [
        migrations.AddField(
            model_name="pregunta",
            name="visible_por_defecto",
            field=models.BooleanField(
                default=True,
                help_text="Indica si la pregunta se muestra sin una regla de visibilidad.",
            ),
        ),
        migrations.AddField(
            model_name="pregunta",
            name="limpiar_respuesta_al_ocultar",
            field=models.BooleanField(
                default=True,
                help_text="Indica si se elimina la respuesta cuando la pregunta queda oculta.",
            ),
        ),
        migrations.AddField(
            model_name="pregunta",
            name="pregunta_origen_flujo",
            field=models.ForeignKey(
                blank=True,
                help_text="Pregunta tras la cual se inserta visualmente cuando es visible.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="preguntas_dependientes_flujo",
                to="formularios.pregunta",
            ),
        ),
        migrations.AddField(
            model_name="pregunta",
            name="codigo_catalogo_departamento",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Codigo del catalogo de departamentos para ubicacion geografica.",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="pregunta",
            name="tipo_pregunta",
            field=models.CharField(
                choices=[
                    ("texto_corto", "Texto corto"),
                    ("texto_largo", "Texto largo"),
                    ("numero", "Número"),
                    ("fecha", "Fecha"),
                    ("hora", "Hora"),
                    ("fecha_hora", "Fecha y hora"),
                    ("radio", "Radio"),
                    ("checkbox", "Checkbox"),
                    ("select", "Select"),
                    ("select_multiple", "Select múltiple"),
                    ("autocomplete", "Autocomplete"),
                    ("likert", "Likert"),
                    ("matriz", "Matriz"),
                    ("archivo", "Archivo"),
                    ("firma", "Firma"),
                    ("geolocalizacion", "Geolocalización"),
                    ("ubicacion_geografica", "Ubicación geográfica"),
                    ("audio", "Audio"),
                    ("video", "Video"),
                ],
                max_length=30,
            ),
        ),
    ]
