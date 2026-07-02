"""
Agrega remitente de notificaciones y completa correo de soporte inicial.
"""

from django.db import migrations, models

CORREO_SOPORTE_INICIAL = "imoliverosh@dane.gov.co"


def cargar_correo_soporte_inicial(apps, schema_editor) -> None:
    """Completa el correo de soporte en configuraciones activas sin valor."""
    modelo = apps.get_model("contenidos", "ConfiguracionInterfaz")
    modelo.objects.filter(
        esta_activa=True,
        email_soporte="",
    ).update(email_soporte=CORREO_SOPORTE_INICIAL)


class Migration(migrations.Migration):

    dependencies = [
        ("contenidos", "0013_configuracionflujoformulario_enlaces_terminos"),
    ]

    operations = [
        migrations.AddField(
            model_name="configuracioninterfaz",
            name="email_remitente_notificaciones",
            field=models.EmailField(
                blank=True,
                help_text=(
                    "Remitente de correos del sistema. Si está vacío, "
                    "se usa EMAIL_DEFAULT_FROM."
                ),
                max_length=254,
                verbose_name="Correo remitente de notificaciones",
            ),
        ),
        migrations.AlterField(
            model_name="configuracioninterfaz",
            name="email_soporte",
            field=models.EmailField(
                blank=True,
                help_text=(
                    "Destino del formulario de contacto y referencia visible en términos."
                ),
                max_length=254,
                verbose_name="Correo de soporte",
            ),
        ),
        migrations.RunPython(
            cargar_correo_soporte_inicial,
            migrations.RunPython.noop,
        ),
    ]
