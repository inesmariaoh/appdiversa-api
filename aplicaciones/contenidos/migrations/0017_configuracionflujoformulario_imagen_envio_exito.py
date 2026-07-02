"""
Agrega la imagen parametrizable de la pantalla de envio exitoso y la sincroniza.
"""

import django.db.models.deletion
from django.db import migrations, models


def sincronizar_imagen_envio_exito(apps, schema_editor) -> None:
    """Crea el recurso Cloudinary y lo vincula a las configuraciones de flujo."""
    from aplicaciones.contenidos.servicios_imagenes_cloudinary import (
        sincronizar_recursos_imagenes_cloudinary,
        vincular_imagen_envio_exito_flujo,
    )

    sincronizar_recursos_imagenes_cloudinary()
    vincular_imagen_envio_exito_flujo()


class Migration(migrations.Migration):

    dependencies = [
        ("archivos", "0001_initial"),
        ("contenidos", "0016_resync_imagenes_cloudinary"),
    ]

    operations = [
        migrations.AddField(
            model_name="configuracionflujoformulario",
            name="img_enc_enviada_exito",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="configuraciones_flujo_envio_exito",
                to="archivos.archivorepositorio",
            ),
        ),
        migrations.AddField(
            model_name="configuracionflujoformulario",
            name="img_enc_enviada_exito_alt",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.RunPython(
            sincronizar_imagen_envio_exito,
            migrations.RunPython.noop,
        ),
    ]
