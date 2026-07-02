"""
Migracion de logos legacy desde ConfiguracionInterfaz hacia LogoInterfaz.
"""

from django.db import migrations

MAPEO_LOGOS_LEGACY = (
    ("logo_principal", "logo_principal_repositorio", "Logo principal", 1),
    ("logo_secundario", "logo_secundario_repositorio", "Logo secundario", 2),
    ("logo_institucional", "logo_institucional_repositorio", "Logo institucional", 3),
    ("favicon", "favicon_repositorio", "Favicon", 4),
)


def migrar_logos_desde_configuracion(apps, schema_editor) -> None:
    """Copia los logos existentes en configuracion hacia el modelo parametrizado."""
    ConfiguracionInterfaz = apps.get_model("contenidos", "ConfiguracionInterfaz")
    LogoInterfaz = apps.get_model("contenidos", "LogoInterfaz")

    for configuracion in ConfiguracionInterfaz.objects.all().iterator():
        for codigo, campo_repositorio, nombre, orden in MAPEO_LOGOS_LEGACY:
            imagen = getattr(configuracion, codigo)
            archivo_repositorio = getattr(configuracion, campo_repositorio)
            if not imagen and archivo_repositorio is None:
                continue

            if LogoInterfaz.objects.filter(
                configuracion_interfaz=configuracion,
                codigo=codigo,
                esta_eliminado=False,
            ).exists():
                continue

            LogoInterfaz.objects.create(
                configuracion_interfaz=configuracion,
                codigo=codigo,
                nombre=nombre,
                imagen=imagen or "",
                archivo_repositorio=archivo_repositorio,
                orden=orden,
                esta_activo=True,
            )


class Migration(migrations.Migration):

    dependencies = [
        ("contenidos", "0006_logo_interfaz"),
    ]

    operations = [
        migrations.RunPython(
            migrar_logos_desde_configuracion,
            migrations.RunPython.noop,
        ),
    ]
