"""
Sincroniza validaciones de filtros preliminares definidas en datos semilla.
"""

from decimal import Decimal
from typing import Any

from django.db import migrations

CAMPOS_FILTRO = (
    "tipo_validacion_filtro",
    "valor_minimo",
    "valor_maximo",
    "valor_filtro_esperado",
    "bloquea_continuacion_si_no_cumple",
    "mensaje_error",
    "mensaje_no_cumple",
)

ACTUALIZACIONES_VALIDACION_FILTRO: tuple[dict[str, Any], ...] = (
    {
        "formulario_codigo": "DISC-001",
        "pregunta_codigo": "P1",
        "campos": {
            "tipo_validacion_filtro": "rango_edad",
            "valor_minimo": Decimal("18"),
            "valor_maximo": Decimal("109"),
            "bloquea_continuacion_si_no_cumple": True,
            "mensaje_error": (
                "Debes tener 18 años o más para participar. "
                "Revisa tu fecha o vuelve a la lista de encuestas."
            ),
            "mensaje_no_cumple": (
                "Debes tener 18 años o más para participar. "
                "Revisa tu fecha o vuelve a la lista de encuestas."
            ),
        },
    },
    {
        "formulario_codigo": "DISC-001",
        "pregunta_codigo": "P2",
        "campos": {
            "tipo_validacion_filtro": "opcion_exacta",
            "valor_filtro_esperado": {"valor": "si"},
            "bloquea_continuacion_si_no_cumple": True,
            "mensaje_no_cumple": (
                "En este momento no cumples las condiciones para diligenciar esta encuesta."
            ),
        },
    },
)


def _aplicar_actualizacion(Pregunta, Formulario, actualizacion: dict[str, Any]) -> None:
    """Aplica una actualizacion de validacion de filtro a una pregunta existente."""
    pregunta = (
        Pregunta.objects.filter(
            codigo=actualizacion["pregunta_codigo"],
            seccion__formulario_version__formulario__codigo=actualizacion["formulario_codigo"],
            seccion__formulario_version__es_publicada=True,
            es_pregunta_filtro=True,
        )
        .order_by("-seccion__formulario_version__numero_version")
        .first()
    )
    if pregunta is None:
        return

    campos = actualizacion["campos"]
    for nombre_campo in CAMPOS_FILTRO:
        if nombre_campo in campos:
            setattr(pregunta, nombre_campo, campos[nombre_campo])
    pregunta.save(update_fields=list(campos.keys()))


def sincronizar_validacion_filtros_semilla(apps, schema_editor) -> None:
    """Sincroniza validaciones de filtros desde datos semilla parametrizados."""
    Pregunta = apps.get_model("formularios", "Pregunta")
    Formulario = apps.get_model("formularios", "Formulario")
    for actualizacion in ACTUALIZACIONES_VALIDACION_FILTRO:
        _aplicar_actualizacion(Pregunta, Formulario, actualizacion)


class Migration(migrations.Migration):

    dependencies = [
        ("formularios", "0012_pregunta_validacion_filtro_preliminar"),
    ]

    operations = [
        migrations.RunPython(
            sincronizar_validacion_filtros_semilla,
            migrations.RunPython.noop,
        ),
    ]
