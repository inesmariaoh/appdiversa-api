"""
Agrega vinculacion opcional de sesion anonima con usuario autenticado.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("sesiones_anonimas", "0003_remove_sesionanonima_sesiones_an_esta_elim_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="sesionanonima",
            name="usuario",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="sesiones_anonimas_vinculadas",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="sesionanonima",
            index=models.Index(fields=["usuario"], name="sesiones_an_usuario_idx"),
        ),
    ]
