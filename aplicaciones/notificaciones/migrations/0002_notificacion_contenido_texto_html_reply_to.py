# Generated manually for campos de contenido separado en notificaciones

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notificaciones", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="notificacion",
            name="contenido_texto_generado",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="notificacion",
            name="contenido_html_generado",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="notificacion",
            name="reply_to",
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
