# Alineacion de indices de auditoria con el estado del modelo Django

from django.db import migrations

from aplicaciones.auditoria.utilidades_migracion_indices import (
    eliminar_indices_por_columnas,
    separar_estado_indices,
)

STATE_OPERATIONS = [
    migrations.RemoveIndex(
        model_name="respuesta",
        name="respuestas_esta_elim_idx",
    ),
    migrations.RemoveIndex(
        model_name="respuesta",
        name="respuestas_fecha_cre_idx",
    ),
]


def _eliminar_indices_respuesta(apps, schema_editor) -> None:
    eliminar_indices_por_columnas(schema_editor, "respuestas_respuesta")


class Migration(migrations.Migration):

    dependencies = [
        ("respuestas", "0003_auditoria_campos"),
    ]

    operations = [
        separar_estado_indices(_eliminar_indices_respuesta, STATE_OPERATIONS),
    ]
