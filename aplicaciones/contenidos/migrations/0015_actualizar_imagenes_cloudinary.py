"""
Actualiza logos y portadas con URLs publicas de Cloudinary.
"""

from django.db import migrations


def actualizar_imagenes_cloudinary(apps, schema_editor) -> None:
    """Delega la sincronizacion al servicio reutilizable del dominio."""
    from aplicaciones.contenidos.servicios_imagenes_cloudinary import (
        sincronizar_recursos_imagenes_cloudinary,
    )

    sincronizar_recursos_imagenes_cloudinary()


class Migration(migrations.Migration):

    dependencies = [
        ("contenidos", "0014_configuracioninterfaz_correos_soporte_notificaciones"),
        ("formularios", "0013_sincronizar_validacion_filtros_semilla"),
    ]

    operations = [
        migrations.RunPython(
            actualizar_imagenes_cloudinary,
            migrations.RunPython.noop,
        ),
    ]
