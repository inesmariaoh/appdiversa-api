"""
Corrige ortografia del texto del boton de aceptacion de terminos.
"""

from django.db import migrations


TEXTO_ANTERIOR = "Aceptar y comenzar encuesta"
TEXTO_CORREGIDO = "Aceptar y comenzar la encuesta"


def corregir_texto_boton_terminos(apps, schema_editor) -> None:
    """Actualiza el texto del boton de terminos en configuraciones existentes."""
    modelo = apps.get_model("contenidos", "ConfiguracionFlujoFormulario")
    modelo.objects.filter(terminos_boton_aceptar=TEXTO_ANTERIOR).update(
        terminos_boton_aceptar=TEXTO_CORREGIDO,
    )


def revertir_texto_boton_terminos(apps, schema_editor) -> None:
    """Restaura el texto anterior del boton de terminos."""
    modelo = apps.get_model("contenidos", "ConfiguracionFlujoFormulario")
    modelo.objects.filter(terminos_boton_aceptar=TEXTO_CORREGIDO).update(
        terminos_boton_aceptar=TEXTO_ANTERIOR,
    )


class Migration(migrations.Migration):
    """Migracion de correccion ortografica del boton de terminos."""

    dependencies = [
        ("contenidos", "0010_configuracionflujoformulario_textos_terminos_ui"),
    ]

    operations = [
        migrations.RunPython(
            corregir_texto_boton_terminos,
            revertir_texto_boton_terminos,
        ),
    ]
