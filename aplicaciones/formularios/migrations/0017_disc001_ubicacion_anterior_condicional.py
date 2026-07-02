"""
Agrega la pregunta condicional opcional de ubicacion anterior (departamento y municipio)
al formulario de discriminacion, visible solo cuando el encuestado indica que cambio de municipio.
"""

from django.db import migrations

FORMULARIO_OBJETIVO = "DISC-001"
CODIGO_ORIGEN = "P7"
CODIGO_DEPENDIENTE = "P7-ANT"
CATALOGO_MUNICIPIOS = "municipios"
CODIGO_CATALOGO_DEPARTAMENTO = "departamentos"
TIPO_UBICACION_GEOGRAFICA = "ubicacion_geografica"
OPERADOR_IGUAL = "equals"
ACCION_MOSTRAR = "mostrar"
VALOR_ESPERADO_SI = {"valor": "si"}
ORDEN_DEPENDIENTE = 75

TEXTO_DEPENDIENTE = "Indique el departamento y municipio donde residía anteriormente."
DESCRIPCION_DEPENDIENTE = "Seleccione departamento y municipio."
MENSAJE_ERROR_DEPENDIENTE = (
    "Debe seleccionar el departamento y municipio donde residía anteriormente."
)


def _construir_valores_dependiente(pregunta_origen, catalogo_municipios) -> dict[str, object]:
    """Arma los valores parametrizados de la pregunta condicional opcional."""
    return {
        "texto": TEXTO_DEPENDIENTE,
        "descripcion": DESCRIPCION_DEPENDIENTE,
        "tipo_pregunta": TIPO_UBICACION_GEOGRAFICA,
        "es_obligatoria": False,
        "orden": ORDEN_DEPENDIENTE,
        "esta_activa": True,
        "usa_catalogo": True,
        "catalogo_asociado": catalogo_municipios,
        "codigo_catalogo_departamento": CODIGO_CATALOGO_DEPARTAMENTO,
        "permite_busqueda_catalogo": True,
        "visible_por_defecto": False,
        "limpiar_respuesta_al_ocultar": True,
        "pregunta_origen_flujo": pregunta_origen,
        "mensaje_error": MENSAJE_ERROR_DEPENDIENTE,
    }


def _obtener_o_crear_dependiente(modelo_pregunta, pregunta_origen, catalogo_municipios):
    """Obtiene o crea la pregunta condicional en la seccion de la pregunta origen."""
    dependiente = modelo_pregunta.objects.filter(
        codigo=CODIGO_DEPENDIENTE,
        seccion=pregunta_origen.seccion,
    ).first()
    if dependiente is not None:
        return dependiente
    return modelo_pregunta.objects.create(
        codigo=CODIGO_DEPENDIENTE,
        seccion=pregunta_origen.seccion,
        **_construir_valores_dependiente(pregunta_origen, catalogo_municipios),
    )


def _asegurar_regla_mostrar(modelo_regla, pregunta_origen, dependiente) -> None:
    """Crea la regla que muestra la pregunta condicional cuando el origen es afirmativo."""
    existe = modelo_regla.objects.filter(
        pregunta_origen=pregunta_origen,
        pregunta_destino=dependiente,
        accion=ACCION_MOSTRAR,
    ).exists()
    if existe:
        return
    modelo_regla.objects.create(
        pregunta_origen=pregunta_origen,
        pregunta_destino=dependiente,
        operador=OPERADOR_IGUAL,
        valor_esperado=VALOR_ESPERADO_SI,
        accion=ACCION_MOSTRAR,
        mensaje="",
        esta_activa=True,
    )


def agregar_ubicacion_anterior_condicional(apps, schema_editor) -> None:
    """Crea la pregunta condicional opcional y su regla de visibilidad."""
    modelo_pregunta = apps.get_model("formularios", "Pregunta")
    modelo_regla = apps.get_model("formularios", "ReglaPregunta")
    modelo_catalogo = apps.get_model("catalogos", "Catalogo")

    catalogo_municipios = modelo_catalogo.objects.filter(codigo=CATALOGO_MUNICIPIOS).first()
    if catalogo_municipios is None:
        return

    preguntas_origen = modelo_pregunta.objects.filter(
        codigo=CODIGO_ORIGEN,
        seccion__formulario_version__formulario__codigo=FORMULARIO_OBJETIVO,
        seccion__formulario_version__es_publicada=True,
    ).select_related("seccion")

    for pregunta_origen in preguntas_origen:
        dependiente = _obtener_o_crear_dependiente(
            modelo_pregunta,
            pregunta_origen,
            catalogo_municipios,
        )
        _asegurar_regla_mostrar(modelo_regla, pregunta_origen, dependiente)


def revertir_ubicacion_anterior_condicional(apps, schema_editor) -> None:
    """Elimina la pregunta condicional y su regla asociada."""
    modelo_pregunta = apps.get_model("formularios", "Pregunta")
    modelo_regla = apps.get_model("formularios", "ReglaPregunta")

    filtro_formulario = {
        "pregunta_destino__codigo": CODIGO_DEPENDIENTE,
        "pregunta_destino__seccion__formulario_version__formulario__codigo": (
            FORMULARIO_OBJETIVO
        ),
        "accion": ACCION_MOSTRAR,
    }
    modelo_regla.objects.filter(**filtro_formulario).delete()
    modelo_pregunta.objects.filter(
        codigo=CODIGO_DEPENDIENTE,
        seccion__formulario_version__formulario__codigo=FORMULARIO_OBJETIVO,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("formularios", "0016_activar_texto_otro_obligatorio_disc001"),
        ("catalogos", "0002_alter_catalogo_options_alter_itemcatalogo_options"),
    ]

    operations = [
        migrations.RunPython(
            agregar_ubicacion_anterior_condicional,
            revertir_ubicacion_anterior_condicional,
        ),
    ]
