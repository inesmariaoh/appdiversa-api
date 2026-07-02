# Generated manually para auditoria transversal

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

TABLA_RESPUESTA = "respuestas_respuesta"
INDICE_ELIMINACION = "respuestas__elimina_aa5a80_idx"
INDICE_UQ_SESION_PREGUNTA = "uq_respuesta_sesion_pregunta"
INDICE_ESTA_ELIMINADO = "respuestas_esta_elim_idx"
INDICE_FECHA_CREACION = "respuestas_fecha_cre_idx"
INDICE_UQ_SESION_PREGUNTA_ACTIVA = "uq_respuesta_sesion_pregunta_activa"
COLUMNAS_USUARIO_AUDITORIA = (
    "creado_por_id",
    "modificado_por_id",
    "eliminado_por_id",
)


def _columna_existe(connection, tabla: str, columna: str) -> bool:
    with connection.cursor() as cursor:
        if connection.vendor == "sqlite":
            cursor.execute(f"PRAGMA table_info({tabla})")
            return any(row[1] == columna for row in cursor.fetchall())
        cursor.execute(
            """
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = %s
              AND column_name = %s
            """,
            [tabla, columna],
        )
        return cursor.fetchone()[0] > 0


def _indice_existe(connection, tabla: str, indice: str) -> bool:
    with connection.cursor() as cursor:
        if connection.vendor == "sqlite":
            cursor.execute(f"PRAGMA index_list({tabla})")
            return any(row[1] == indice for row in cursor.fetchall())
        cursor.execute(
            """
            SELECT COUNT(*) FROM information_schema.statistics
            WHERE table_schema = DATABASE()
              AND table_name = %s
              AND index_name = %s
            """,
            [tabla, indice],
        )
        return cursor.fetchone()[0] > 0


def _ejecutar_sql(schema_editor, sentencia: str) -> None:
    schema_editor.execute(sentencia)


def _tipo_id_usuario(connection, apps) -> str:
    usuario_model = apps.get_model(settings.AUTH_USER_MODEL)
    campo_id = usuario_model._meta.get_field("id")
    if campo_id.get_internal_type() == "BigAutoField":
        return "bigint"
    if connection.vendor == "mysql":
        return "int"
    return "integer"


def _tipo_columna_usuario(connection, columna: str) -> str | None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DATA_TYPE FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = %s
              AND column_name = %s
            """,
            [TABLA_RESPUESTA, columna],
        )
        resultado = cursor.fetchone()
        if resultado is None:
            return None
        return resultado[0]


def _agregar_columna_usuario(
    schema_editor,
    connection,
    apps,
    columna: str,
) -> None:
    if _columna_existe(connection, TABLA_RESPUESTA, columna):
        return
    tipo_id = _tipo_id_usuario(connection, apps)
    usuario_tabla = schema_editor.quote_name(
        apps.get_model(settings.AUTH_USER_MODEL)._meta.db_table
    )
    if connection.vendor == "sqlite":
        _ejecutar_sql(
            schema_editor,
            f"ALTER TABLE {TABLA_RESPUESTA} "
            f"ADD COLUMN {columna} {tipo_id} NULL "
            f"REFERENCES {usuario_tabla}(id) DEFERRABLE INITIALLY DEFERRED",
        )
        return
    _ejecutar_sql(
        schema_editor,
        f"ALTER TABLE {TABLA_RESPUESTA} "
        f"ADD COLUMN {columna} {tipo_id} NULL",
    )
    _ejecutar_sql(
        schema_editor,
        f"ALTER TABLE {TABLA_RESPUESTA} "
        f"ADD CONSTRAINT respuestas_{columna}_fk "
        f"FOREIGN KEY ({columna}) REFERENCES {usuario_tabla}(id)",
    )


def _corregir_columna_usuario_incompatible(
    schema_editor,
    connection,
    apps,
    columna: str,
) -> None:
    if connection.vendor != "mysql":
        return
    tipo_esperado = _tipo_id_usuario(connection, apps)
    tipo_actual = _tipo_columna_usuario(connection, columna)
    if tipo_actual is None:
        return
    if tipo_actual == "bigint" and tipo_esperado == "int":
        _ejecutar_sql(
            schema_editor,
            f"ALTER TABLE {TABLA_RESPUESTA} DROP COLUMN {columna}",
        )


def _eliminar_indice_si_existe(
    schema_editor,
    connection,
    indice: str,
    sentencia_sqlite: str,
    sentencia_default: str,
) -> None:
    if not _indice_existe(connection, TABLA_RESPUESTA, indice):
        return
    sentencia = (
        sentencia_sqlite
        if connection.vendor == "sqlite"
        else sentencia_default
    )
    _ejecutar_sql(schema_editor, sentencia)


def _renombrar_eliminada_logicamente(schema_editor, connection) -> None:
    if not _columna_existe(connection, TABLA_RESPUESTA, "eliminada_logicamente"):
        return
    _eliminar_indice_si_existe(
        schema_editor,
        connection,
        INDICE_ELIMINACION,
        f"DROP INDEX {INDICE_ELIMINACION}",
        f"DROP INDEX {INDICE_ELIMINACION} ON {TABLA_RESPUESTA}",
    )
    _eliminar_indice_si_existe(
        schema_editor,
        connection,
        INDICE_UQ_SESION_PREGUNTA,
        f"DROP INDEX {INDICE_UQ_SESION_PREGUNTA}",
        f"ALTER TABLE {TABLA_RESPUESTA} DROP INDEX {INDICE_UQ_SESION_PREGUNTA}",
    )
    if connection.vendor == "sqlite":
        _ejecutar_sql(
            schema_editor,
            f"ALTER TABLE {TABLA_RESPUESTA} "
            "RENAME COLUMN eliminada_logicamente TO esta_eliminado",
        )
        return
    _ejecutar_sql(
        schema_editor,
        f"ALTER TABLE {TABLA_RESPUESTA} "
        "CHANGE eliminada_logicamente esta_eliminado "
        "tinyint(1) NOT NULL DEFAULT 0",
    )


def _agregar_fecha_eliminacion(schema_editor, connection) -> None:
    if _columna_existe(connection, TABLA_RESPUESTA, "fecha_eliminacion"):
        return
    if connection.vendor == "sqlite":
        _ejecutar_sql(
            schema_editor,
            f"ALTER TABLE {TABLA_RESPUESTA} "
            "ADD COLUMN fecha_eliminacion datetime NULL",
        )
        return
    _ejecutar_sql(
        schema_editor,
        f"ALTER TABLE {TABLA_RESPUESTA} "
        "ADD COLUMN fecha_eliminacion datetime(6) NULL",
    )


def _aplicar_columnas_usuario_auditoria(schema_editor, connection, apps) -> None:
    for columna in COLUMNAS_USUARIO_AUDITORIA:
        _corregir_columna_usuario_incompatible(
            schema_editor,
            connection,
            apps,
            columna,
        )
        _agregar_columna_usuario(schema_editor, connection, apps, columna)


def _crear_indice_si_no_existe(
    schema_editor,
    connection,
    indice: str,
    sentencia_creacion: str,
) -> None:
    if _indice_existe(connection, TABLA_RESPUESTA, indice):
        return
    _ejecutar_sql(schema_editor, sentencia_creacion)


def _crear_indice_unico_activa_sqlite(schema_editor, connection) -> None:
    if (
        connection.vendor != "sqlite"
        or _indice_existe(
            connection,
            TABLA_RESPUESTA,
            INDICE_UQ_SESION_PREGUNTA_ACTIVA,
        )
    ):
        return
    _ejecutar_sql(
        schema_editor,
        f"CREATE UNIQUE INDEX {INDICE_UQ_SESION_PREGUNTA_ACTIVA} "
        f"ON {TABLA_RESPUESTA} (sesion_id, pregunta_id) "
        "WHERE esta_eliminado = 0",
    )


def _crear_indices_auditoria_respuesta(schema_editor, connection) -> None:
    _crear_indice_si_no_existe(
        schema_editor,
        connection,
        INDICE_ESTA_ELIMINADO,
        f"CREATE INDEX {INDICE_ESTA_ELIMINADO} "
        f"ON {TABLA_RESPUESTA} (esta_eliminado)",
    )
    _crear_indice_si_no_existe(
        schema_editor,
        connection,
        INDICE_FECHA_CREACION,
        f"CREATE INDEX {INDICE_FECHA_CREACION} "
        f"ON {TABLA_RESPUESTA} (fecha_creacion)",
    )
    _crear_indice_unico_activa_sqlite(schema_editor, connection)


def aplicar_auditoria_respuesta(apps, schema_editor) -> None:
    """Aplica cambios de auditoria tolerando estados parciales de la base."""
    connection = schema_editor.connection
    _renombrar_eliminada_logicamente(schema_editor, connection)
    _agregar_fecha_eliminacion(schema_editor, connection)
    _aplicar_columnas_usuario_auditoria(schema_editor, connection, apps)
    _crear_indices_auditoria_respuesta(schema_editor, connection)


class Migration(migrations.Migration):

    dependencies = [
        ("respuestas", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    state_operations = [
        migrations.RemoveIndex(
            model_name="respuesta",
            name="respuestas__elimina_aa5a80_idx",
        ),
        migrations.RemoveConstraint(
            model_name="respuesta",
            name="uq_respuesta_sesion_pregunta",
        ),
        migrations.RenameField(
            model_name="respuesta",
            old_name="eliminada_logicamente",
            new_name="esta_eliminado",
        ),
        migrations.AddField(
            model_name="respuesta",
            name="fecha_eliminacion",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="respuesta",
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
            model_name="respuesta",
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
            model_name="respuesta",
            name="eliminado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="respuesta",
            index=models.Index(
                fields=["esta_eliminado"],
                name="respuestas_esta_elim_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="respuesta",
            index=models.Index(
                fields=["fecha_creacion"],
                name="respuestas_fecha_cre_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="respuesta",
            constraint=models.UniqueConstraint(
                condition=models.Q(("esta_eliminado", False)),
                fields=("sesion", "pregunta"),
                name="uq_respuesta_sesion_pregunta_activa",
            ),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    aplicar_auditoria_respuesta,
                    migrations.RunPython.noop,
                ),
            ],
            state_operations=state_operations,
        ),
    ]
