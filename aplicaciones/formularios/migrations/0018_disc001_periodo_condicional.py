"""
Configura la regla condicional que oculta la pregunta del periodo de discriminacion
cuando el encuestado indica que no ha sentido discriminacion en el formulario de discriminacion.
"""

from django.db import migrations

FORMULARIO_OBJETIVO = "DISC-001"
CODIGO_ORIGEN = "P12"
CODIGO_DESTINO = "P13"
OPERADOR_CONTIENE = "contains"
ACCION_OCULTAR = "ocultar"
CODIGO_OPCION_SIN_DISCRIMINACION = "OP26-P12"
VALOR_OPCION_SIN_DISCRIMINACION = "no_he_sentido"
VALOR_ESPERADO_SIN_DISCRIMINACION = {
    "valores": [CODIGO_OPCION_SIN_DISCRIMINACION, VALOR_OPCION_SIN_DISCRIMINACION],
}


def _obtener_preguntas_origen(modelo_pregunta):
    """Obtiene las preguntas origen publicadas del formulario objetivo."""
    return modelo_pregunta.objects.filter(
        codigo=CODIGO_ORIGEN,
        seccion__formulario_version__formulario__codigo=FORMULARIO_OBJETIVO,
        seccion__formulario_version__es_publicada=True,
    ).select_related("seccion")


def _obtener_pregunta_destino(modelo_pregunta, pregunta_origen):
    """Obtiene la pregunta destino dentro de la misma version del origen."""
    return modelo_pregunta.objects.filter(
        codigo=CODIGO_DESTINO,
        seccion__formulario_version_id=pregunta_origen.seccion.formulario_version_id,
    ).first()


def _asegurar_limpieza_destino(pregunta_destino) -> None:
    """Garantiza que la pregunta destino limpie su respuesta al quedar oculta."""
    if pregunta_destino.limpiar_respuesta_al_ocultar:
        return
    pregunta_destino.limpiar_respuesta_al_ocultar = True
    pregunta_destino.save(update_fields=["limpiar_respuesta_al_ocultar"])


def _asegurar_regla_ocultar(modelo_regla, pregunta_origen, pregunta_destino) -> None:
    """Crea la regla que oculta la pregunta destino cuando aplica la opcion excluyente."""
    existe = modelo_regla.objects.filter(
        pregunta_origen=pregunta_origen,
        pregunta_destino=pregunta_destino,
        accion=ACCION_OCULTAR,
    ).exists()
    if existe:
        return
    modelo_regla.objects.create(
        pregunta_origen=pregunta_origen,
        pregunta_destino=pregunta_destino,
        operador=OPERADOR_CONTIENE,
        valor_esperado=VALOR_ESPERADO_SIN_DISCRIMINACION,
        accion=ACCION_OCULTAR,
        mensaje="",
        esta_activa=True,
    )


def agregar_regla_periodo_condicional(apps, schema_editor) -> None:
    """Crea la regla de visibilidad condicional para la pregunta del periodo."""
    modelo_pregunta = apps.get_model("formularios", "Pregunta")
    modelo_regla = apps.get_model("formularios", "ReglaPregunta")

    for pregunta_origen in _obtener_preguntas_origen(modelo_pregunta):
        pregunta_destino = _obtener_pregunta_destino(modelo_pregunta, pregunta_origen)
        if pregunta_destino is None:
            continue
        _asegurar_limpieza_destino(pregunta_destino)
        _asegurar_regla_ocultar(modelo_regla, pregunta_origen, pregunta_destino)


def revertir_regla_periodo_condicional(apps, schema_editor) -> None:
    """Elimina la regla de visibilidad condicional creada para la pregunta del periodo."""
    modelo_regla = apps.get_model("formularios", "ReglaPregunta")
    modelo_regla.objects.filter(
        pregunta_origen__codigo=CODIGO_ORIGEN,
        pregunta_destino__codigo=CODIGO_DESTINO,
        pregunta_destino__seccion__formulario_version__formulario__codigo=(
            FORMULARIO_OBJETIVO
        ),
        accion=ACCION_OCULTAR,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("formularios", "0017_disc001_ubicacion_anterior_condicional"),
    ]

    operations = [
        migrations.RunPython(
            agregar_regla_periodo_condicional,
            revertir_regla_periodo_condicional,
        ),
    ]
