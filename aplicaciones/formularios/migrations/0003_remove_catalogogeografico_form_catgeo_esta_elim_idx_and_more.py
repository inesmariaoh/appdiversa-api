# Alineacion de indices de auditoria con el estado del modelo Django

from django.db import migrations

from aplicaciones.auditoria.utilidades_migracion_indices import (
    eliminar_indices_por_columnas,
    separar_estado_indices,
)

TABLAS_FORMULARIOS = (
    "formularios_catalogogeografico",
    "formularios_formulario",
    "formularios_formularioversion",
    "formularios_opcionrespuesta",
    "formularios_pregunta",
    "formularios_preguntamatrizcolumna",
    "formularios_preguntamatrizfila",
    "formularios_reglapregunta",
    "formularios_seccionformulario",
    "formularios_textoformulario",
)

STATE_OPERATIONS = [
    migrations.RemoveIndex(
        model_name="catalogogeografico",
        name="form_catgeo_esta_elim_idx",
    ),
    migrations.RemoveIndex(
        model_name="catalogogeografico",
        name="form_catgeo_fecha_cre_idx",
    ),
    migrations.RemoveIndex(
        model_name="formulario",
        name="form_formulario_esta_elim_idx",
    ),
    migrations.RemoveIndex(
        model_name="formulario",
        name="form_formulario_fecha_cre_idx",
    ),
    migrations.RemoveIndex(
        model_name="formularioversion",
        name="form_formversion_esta_elim_idx",
    ),
    migrations.RemoveIndex(
        model_name="formularioversion",
        name="form_formversion_fecha_cre_idx",
    ),
    migrations.RemoveIndex(
        model_name="opcionrespuesta",
        name="form_opcion_esta_elim_idx",
    ),
    migrations.RemoveIndex(
        model_name="opcionrespuesta",
        name="form_opcion_fecha_cre_idx",
    ),
    migrations.RemoveIndex(
        model_name="pregunta",
        name="form_pregunta_esta_elim_idx",
    ),
    migrations.RemoveIndex(
        model_name="pregunta",
        name="form_pregunta_fecha_cre_idx",
    ),
    migrations.RemoveIndex(
        model_name="preguntamatrizcolumna",
        name="form_matcol_esta_elim_idx",
    ),
    migrations.RemoveIndex(
        model_name="preguntamatrizcolumna",
        name="form_matcol_fecha_cre_idx",
    ),
    migrations.RemoveIndex(
        model_name="preguntamatrizfila",
        name="form_matfila_esta_elim_idx",
    ),
    migrations.RemoveIndex(
        model_name="preguntamatrizfila",
        name="form_matfila_fecha_cre_idx",
    ),
    migrations.RemoveIndex(
        model_name="reglapregunta",
        name="form_regla_esta_elim_idx",
    ),
    migrations.RemoveIndex(
        model_name="reglapregunta",
        name="form_regla_fecha_cre_idx",
    ),
    migrations.RemoveIndex(
        model_name="seccionformulario",
        name="form_seccion_esta_elim_idx",
    ),
    migrations.RemoveIndex(
        model_name="seccionformulario",
        name="form_seccion_fecha_cre_idx",
    ),
    migrations.RemoveIndex(
        model_name="textoformulario",
        name="form_texto_esta_elim_idx",
    ),
    migrations.RemoveIndex(
        model_name="textoformulario",
        name="form_texto_fecha_cre_idx",
    ),
]


def _eliminar_indices_formularios(apps, schema_editor) -> None:
    for tabla in TABLAS_FORMULARIOS:
        eliminar_indices_por_columnas(schema_editor, tabla)


class Migration(migrations.Migration):

    dependencies = [
        ("formularios", "0002_auditoria_campos"),
    ]

    operations = [
        separar_estado_indices(_eliminar_indices_formularios, STATE_OPERATIONS),
    ]
