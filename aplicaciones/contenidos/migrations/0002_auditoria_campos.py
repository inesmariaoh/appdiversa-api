# Generated manually for auditoria transversal

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenidos", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="configuracioninterfaz",
            name="fecha_eliminacion",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="configuracioninterfaz",
            name="creado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="configuracioninterfaz",
            name="modificado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="configuracioninterfaz",
            name="eliminado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="configuracioninterfaz",
            name="esta_eliminado",
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name="configuracioninterfaz",
            index=models.Index(
                fields=["esta_eliminado"],
                name="contenidos_cfg_esta_elim_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="configuracioninterfaz",
            index=models.Index(
                fields=["fecha_creacion"],
                name="contenidos_cfg_fecha_cre_idx",
            ),
        ),
    ]
