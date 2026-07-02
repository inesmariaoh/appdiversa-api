"""
Activa el texto libre obligatorio en las opciones tipo otro del formulario de discriminacion.
"""

from django.db import migrations

from aplicaciones.formularios.utilidades_opcion_otro import resolver_activa_otro

FORMULARIO_OBJETIVO = "DISC-001"
CAMPO_OBJETIVO = "texto_otro_obligatorio"


def _preguntas_con_opcion_otro(modelo_pregunta):
    """Retorna preguntas del formulario objetivo que exponen alguna opcion tipo otro."""
    preguntas = (
        modelo_pregunta.objects.filter(
            permite_otro=True,
            seccion__formulario_version__formulario__codigo=FORMULARIO_OBJETIVO,
        )
        .prefetch_related("opciones")
    )
    for pregunta in preguntas:
        tiene_opcion_otro = any(
            resolver_activa_otro(opcion.activa_otro, pregunta.permite_otro, opcion.etiqueta)
            for opcion in pregunta.opciones.all()
        )
        if tiene_opcion_otro:
            yield pregunta


def _asignar_texto_otro_obligatorio(modelo_pregunta, obligatorio: bool) -> None:
    """Ajusta la obligatoriedad del texto libre en preguntas con opcion otro."""
    for pregunta in _preguntas_con_opcion_otro(modelo_pregunta):
        if pregunta.texto_otro_obligatorio == obligatorio:
            continue
        pregunta.texto_otro_obligatorio = obligatorio
        pregunta.save(update_fields=[CAMPO_OBJETIVO])


def activar_texto_otro_obligatorio(apps, schema_editor) -> None:
    """Marca como obligatorio el texto libre de las opciones otro del formulario objetivo."""
    modelo_pregunta = apps.get_model("formularios", "Pregunta")
    _asignar_texto_otro_obligatorio(modelo_pregunta, True)


def revertir_texto_otro_obligatorio(apps, schema_editor) -> None:
    """Restaura el caracter opcional del texto libre de las opciones otro del formulario objetivo."""
    modelo_pregunta = apps.get_model("formularios", "Pregunta")
    _asignar_texto_otro_obligatorio(modelo_pregunta, False)


class Migration(migrations.Migration):

    dependencies = [
        ("formularios", "0015_pregunta_texto_otro_obligatorio"),
    ]

    operations = [
        migrations.RunPython(
            activar_texto_otro_obligatorio,
            revertir_texto_otro_obligatorio,
        ),
    ]
