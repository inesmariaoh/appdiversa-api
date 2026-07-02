"""
Utilidades para migraciones de indices de auditoria.
"""

from collections.abc import Callable

from django.db import migrations

COLUMNAS_INDICE_AUDITORIA = frozenset({"esta_eliminado", "fecha_creacion"})
PREFIJO_INDICE_AUTOMATICO = "sqlite_autoindex"


def _indice_cubre_auditoria(cursor, indice: str) -> bool:
    """Indica si un indice sqlite incluye columnas de auditoria."""
    cursor.execute(f"PRAGMA index_info({indice})")
    columnas = {row[2] for row in cursor.fetchall()}
    return bool(columnas.intersection(COLUMNAS_INDICE_AUDITORIA))


def _eliminar_indices_auditoria_sqlite(schema_editor, tabla: str) -> None:
    """Elimina indices de auditoria en tablas sqlite."""
    cursor = schema_editor.connection.cursor()
    cursor.execute(f"PRAGMA index_list({tabla})")
    for indice in [row[1] for row in cursor.fetchall()]:
        if indice.startswith(PREFIJO_INDICE_AUTOMATICO):
            continue
        if _indice_cubre_auditoria(cursor, indice):
            schema_editor.execute(f"DROP INDEX {indice}")


def _eliminar_indices_auditoria_mysql(schema_editor, tabla: str) -> None:
    """Elimina indices de auditoria en tablas mysql."""
    cursor = schema_editor.connection.cursor()
    cursor.execute(
        """
        SELECT DISTINCT index_name
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND column_name IN ('esta_eliminado', 'fecha_creacion')
          AND index_name != 'PRIMARY'
        """,
        [tabla],
    )
    for (indice,) in cursor.fetchall():
        schema_editor.execute(f"DROP INDEX {indice} ON {tabla}")


def eliminar_indices_por_columnas(schema_editor, tabla: str) -> None:
    """Elimina indices sobre columnas de auditoria en una tabla."""
    if schema_editor.connection.vendor == "sqlite":
        _eliminar_indices_auditoria_sqlite(schema_editor, tabla)
        return
    _eliminar_indices_auditoria_mysql(schema_editor, tabla)


def separar_estado_indices(
    database_forward: Callable[..., None],
    state_operations: list[migrations.operations.base.Operation],
) -> migrations.SeparateDatabaseAndState:
    """Envuelve operaciones de estado con limpieza segura en base de datos."""
    return migrations.SeparateDatabaseAndState(
        database_operations=[
            migrations.RunPython(database_forward, migrations.RunPython.noop),
        ],
        state_operations=state_operations,
    )
