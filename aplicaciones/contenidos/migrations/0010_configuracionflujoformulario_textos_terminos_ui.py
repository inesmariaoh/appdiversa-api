"""
Agrega textos administrables de botones y enlace de terminos del flujo.
"""

from django.db import migrations, models


def cargar_textos_terminos_ui(apps, schema_editor) -> None:
    """Completa textos de botones y enlace en configuraciones existentes."""
    configuracion_flujo_formulario = apps.get_model(
        "contenidos",
        "ConfiguracionFlujoFormulario",
    )
    valores_defecto = {
        "terminos_boton_aceptar": "Aceptar y comenzar encuesta",
        "terminos_boton_cerrar": "Cerrar",
        "terminos_enlace": "Términos y condiciones",
    }
    for configuracion in configuracion_flujo_formulario.objects.all().iterator():
        campos_actualizar = {}
        for campo, valor in valores_defecto.items():
            if not getattr(configuracion, campo, ""):
                campos_actualizar[campo] = valor
        if campos_actualizar:
            configuracion_flujo_formulario.objects.filter(pk=configuracion.pk).update(
                **campos_actualizar,
            )


class Migration(migrations.Migration):

    dependencies = [
        ("contenidos", "0009_cargar_configuracion_flujo_formulario_inicial"),
    ]

    operations = [
        migrations.AddField(
            model_name="configuracionflujoformulario",
            name="terminos_boton_aceptar",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="configuracionflujoformulario",
            name="terminos_boton_cerrar",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="configuracionflujoformulario",
            name="terminos_enlace",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.RunPython(
            cargar_textos_terminos_ui,
            migrations.RunPython.noop,
        ),
    ]
