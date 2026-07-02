# Generated manually for auditoria transversal

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

MODELOS_AUDITORIA_COMPLETA = (
    "catalogogeografico",
    "pregunta",
    "opcionrespuesta",
    "preguntamatrizcolumna",
    "preguntamatrizfila",
    "seccionformulario",
    "reglapregunta",
    "textoformulario",
)

SUFIJO_INDICE_POR_MODELO = {
    "catalogogeografico": "catgeo",
    "pregunta": "pregunta",
    "opcionrespuesta": "opcion",
    "preguntamatrizcolumna": "matcol",
    "preguntamatrizfila": "matfila",
    "seccionformulario": "seccion",
    "reglapregunta": "regla",
    "textoformulario": "texto",
}


def _operaciones_auditoria_completa(model_name: str) -> list:
    """Genera operaciones de campos de auditoria para modelos sin campos previos."""
    ahora = django.utils.timezone.now
    sufijo = SUFIJO_INDICE_POR_MODELO.get(model_name, model_name[:6])
    return [
        migrations.AddField(
            model_name=model_name,
            name="fecha_creacion",
            field=models.DateTimeField(auto_now_add=True, default=ahora),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name=model_name,
            name="fecha_modificacion",
            field=models.DateTimeField(auto_now=True, default=ahora),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name=model_name,
            name="fecha_eliminacion",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name=model_name,
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
            model_name=model_name,
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
            model_name=model_name,
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
            model_name=model_name,
            name="esta_eliminado",
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name=model_name,
            index=models.Index(
                fields=["esta_eliminado"],
                name=f"form_{sufijo}_esta_elim_idx",
            ),
        ),
        migrations.AddIndex(
            model_name=model_name,
            index=models.Index(
                fields=["fecha_creacion"],
                name=f"form_{sufijo}_fecha_cre_idx",
            ),
        ),
    ]


class Migration(migrations.Migration):

    dependencies = [
        ("formularios", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="formulario",
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
            model_name="formulario",
            name="fecha_eliminacion",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="formulario",
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
            model_name="formulario",
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
            model_name="formulario",
            name="esta_eliminado",
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name="formulario",
            index=models.Index(
                fields=["esta_eliminado"],
                name="form_formulario_esta_elim_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="formulario",
            index=models.Index(
                fields=["fecha_creacion"],
                name="form_formulario_fecha_cre_idx",
            ),
        ),
        migrations.AddField(
            model_name="formularioversion",
            name="fecha_modificacion",
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="formularioversion",
            name="fecha_eliminacion",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="formularioversion",
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
            model_name="formularioversion",
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
            model_name="formularioversion",
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
            model_name="formularioversion",
            name="esta_eliminado",
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name="formularioversion",
            index=models.Index(
                fields=["esta_eliminado"],
                name="form_formversion_esta_elim_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="formularioversion",
            index=models.Index(
                fields=["fecha_creacion"],
                name="form_formversion_fecha_cre_idx",
            ),
        ),
        *[
            operacion
            for modelo in MODELOS_AUDITORIA_COMPLETA
            for operacion in _operaciones_auditoria_completa(modelo)
        ],
    ]
