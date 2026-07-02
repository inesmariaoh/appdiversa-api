"""
Carga inicial de textos de modales y terminos del flujo de formularios.
"""

from django.db import migrations

_APP_CONTENIDOS = "contenidos"
_MODELO_CONFIGURACION_FLUJO_FORMULARIO = "ConfiguracionFlujoFormulario"
_MODELO_CONFIGURACION_INTERFAZ = "ConfiguracionInterfaz"


def cargar_configuracion_flujo_formulario_inicial(apps, schema_editor) -> None:
    """Crea la configuracion activa inicial si no existe ningun registro."""
    configuracion_flujo_formulario = apps.get_model(
        _APP_CONTENIDOS,
        _MODELO_CONFIGURACION_FLUJO_FORMULARIO,
    )
    configuracion_interfaz = apps.get_model(
        _APP_CONTENIDOS,
        _MODELO_CONFIGURACION_INTERFAZ,
    )

    if configuracion_flujo_formulario.objects.exists():
        return

    interfaz_activa = (
        configuracion_interfaz.objects.filter(
            esta_activa=True,
            esta_eliminado=False,
        )
        .order_by("-fecha_modificacion")
        .first()
    )

    configuracion_flujo_formulario.objects.create(
        configuracion_interfaz=interfaz_activa,
        esta_activa=True,
        modal_salir_titulo="¿Salir sin guardar?",
        modal_salir_p1=(
            "Si abandonas la encuesta ahora, perderás todas tus respuestas "
            "no guardadas."
        ),
        modal_salir_p2=(
            "Para conservar tu progreso y retomarlo más tarde, regístrate o "
            "inicia sesión antes de salir."
        ),
        modal_salir_btn_volver="Volver a la encuesta (mantenerme aquí)",
        modal_salir_btn_salir="Salir sin guardar (perder mi progreso)",
        modal_salir_link_sesion="Iniciar sesión",
        modal_sesion_titulo="Inicia sesión o regístrate",
        modal_sesion_parrafo=(
            "Para conservar tus respuestas y/o retomar encuestas en curso "
            "más tarde, regístrate o inicia sesión antes de salir."
        ),
        modal_sesion_btn_login="Iniciar sesión",
        modal_sesion_btn_registro="Registrarse",
        modal_sesion_link_cancelar="Cancelar",
        modal_guardado_titulo="Encuesta guardada con éxito",
        modal_guardado_parrafo=(
            "Para conservar tu progreso y retomarlo más tarde, regístrate o "
            "inicia sesión antes de salir."
        ),
        modal_guardado_btn_seguir="Seguir viendo",
        modal_guardado_btn_otras="Ver otras encuestas",
        terminos_titulo="Términos y Condiciones de Uso de AppDiversa",
        terminos_p1=(
            "Al acceder a esta aplicación, se entenderá que Usted ha dado su "
            "autorización para el tratamiento de datos personales, de "
            "conformidad con lo establecido en la Ley 1581 de 2012 y las "
            "normas que la reglamentan."
        ),
        terminos_p2=(
            "La información que Usted suministre será gestionada por el DANE, "
            "y sus datos personales serán tratados de manera confidencial y "
            "segura, de acuerdo con la Política de Protección de Datos "
            "Personales implementada por la entidad."
        ),
        terminos_p3=(
            "De acuerdo con los objetivos de esta aplicación, se advierte que "
            "algunas de las interacciones pueden implicar el suministro de "
            "datos sensibles, los cuales contarán con un nivel de seguridad "
            "alto, en garantía de sus derechos constitucionales."
        ),
        terminos_url_ley=(
            "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981"
        ),
        terminos_url_politica_datos=(
            "https://www.dane.gov.co/files/images/ventana-unica/documentos/"
            "politicadedatosdane.pdf"
        ),
        terminos_email_soporte="",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("contenidos", "0008_configuracionflujoformulario"),
    ]

    operations = [
        migrations.RunPython(
            cargar_configuracion_flujo_formulario_inicial,
            migrations.RunPython.noop,
        ),
    ]
