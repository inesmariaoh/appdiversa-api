"""
Agrega textos administrables de enlaces legales del modal de terminos.
"""

from django.db import migrations, models

TEXTO_ENLACE_LEY = "Consultar Ley 1581 de 2012"
TEXTO_ENLACE_POLITICA = "Política de Protección de Datos Personales"
TEXTO_ENLACE_POLITICA_SIN_TILDE = "Politica de Proteccion de Datos Personales"


def cargar_textos_enlaces_terminos(apps, schema_editor) -> None:
    """Completa textos de enlaces legales en configuraciones existentes."""
    modelo = apps.get_model("contenidos", "ConfiguracionFlujoFormulario")
    for registro in modelo.objects.all():
        campos_actualizar: dict[str, str] = {}
        if not (registro.terminos_enlace_ley or "").strip():
            campos_actualizar["terminos_enlace_ley"] = TEXTO_ENLACE_LEY
        if not (registro.terminos_enlace_politica_datos or "").strip():
            campos_actualizar["terminos_enlace_politica_datos"] = TEXTO_ENLACE_POLITICA
        if campos_actualizar:
            modelo.objects.filter(pk=registro.pk).update(**campos_actualizar)


def corregir_enlaces_sin_tildes(apps, schema_editor) -> None:
    """Corrige variantes conocidas sin tildes en textos de enlaces legales."""
    modelo = apps.get_model("contenidos", "ConfiguracionFlujoFormulario")
    modelo.objects.filter(terminos_enlace_politica_datos=TEXTO_ENLACE_POLITICA_SIN_TILDE).update(
        terminos_enlace_politica_datos=TEXTO_ENLACE_POLITICA,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("contenidos", "0012_alter_configuracionflujoformulario_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="configuracionflujoformulario",
            name="terminos_enlace_ley",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="configuracionflujoformulario",
            name="terminos_enlace_politica_datos",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.RunPython(
            cargar_textos_enlaces_terminos,
            migrations.RunPython.noop,
        ),
        migrations.RunPython(
            corregir_enlaces_sin_tildes,
            migrations.RunPython.noop,
        ),
    ]
