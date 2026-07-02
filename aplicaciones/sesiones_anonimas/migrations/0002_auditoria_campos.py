# Generated manually for auditoria transversal

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sesiones_anonimas", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="sesionanonima",
            name="fecha_eliminacion",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sesionanonima",
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
            model_name="sesionanonima",
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
            model_name="sesionanonima",
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
            model_name="sesionanonima",
            name="esta_eliminado",
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name="sesionanonima",
            index=models.Index(
                fields=["esta_eliminado"],
                name="sesiones_an_esta_elim_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="sesionanonima",
            index=models.Index(
                fields=["fecha_creacion"],
                name="sesiones_an_fecha_cre_idx",
            ),
        ),
    ]
