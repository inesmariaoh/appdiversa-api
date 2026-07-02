"""
Re-sincroniza recursos Cloudinary tras corregir la URL de la portada proxima.
"""

from django.db import migrations


def resync_imagenes_cloudinary(apps, schema_editor) -> None:
    """Actualiza URLs publicas y relaciones con los valores vigentes del dominio."""
    from aplicaciones.contenidos.servicios_imagenes_cloudinary import (
        sincronizar_recursos_imagenes_cloudinary,
    )

    sincronizar_recursos_imagenes_cloudinary()


class Migration(migrations.Migration):

    dependencies = [
        ("contenidos", "0015_actualizar_imagenes_cloudinary"),
    ]

    operations = [
        migrations.RunPython(
            resync_imagenes_cloudinary,
            migrations.RunPython.noop,
        ),
    ]
