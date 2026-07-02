# Alineacion de indices de auditoria con el estado del modelo Django

from django.db import migrations

from aplicaciones.auditoria.utilidades_migracion_indices import (
    eliminar_indices_por_columnas,
    separar_estado_indices,
)

STATE_OPERATIONS = [
    migrations.RemoveIndex(
        model_name="sesionanonima",
        name="sesiones_an_esta_elim_idx",
    ),
    migrations.RemoveIndex(
        model_name="sesionanonima",
        name="sesiones_an_fecha_cre_idx",
    ),
]


def _eliminar_indices_sesion(apps, schema_editor) -> None:
    eliminar_indices_por_columnas(schema_editor, "sesiones_anonimas_sesionanonima")


class Migration(migrations.Migration):

    dependencies = [
        ("sesiones_anonimas", "0002_auditoria_campos"),
    ]

    operations = [
        separar_estado_indices(_eliminar_indices_sesion, STATE_OPERATIONS),
    ]
