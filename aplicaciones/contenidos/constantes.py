"""
Mensajes y valores por defecto de la configuracion de interfaz.
"""


class ValoresPorDefectoInterfaz:
    """Valores seguros cuando no existe configuracion activa."""

    NOMBRE_APLICATIVO = "AppDiversa"
    NOMBRE_CORTO = "AppDiversa"
    DESCRIPCION_APLICATIVO = ""
    TEXTO_PIE_PAGINA = ""
    TEXTO_TITULO_SECCION_ENCUESTAS = ""
    TEXTO_DESCRIPCION_SECCION_ENCUESTAS = ""
    EMAIL_SOPORTE = ""
    TEXTO_TERMINOS_CONDICIONES = ""
    TEXTO_AUTORIZACION_DATOS = ""
    TEXTO_VERIFICACION_EXITOSA_TITULO = ""
    TEXTO_VERIFICACION_EXITOSA_CUERPO = ""
    TEXTO_CONFIRMACION_ENVIO_TITULO = ""
    TEXTO_CONFIRMACION_ENVIO_SUBTITULO = ""
    META_TITULO_SEO = ""
    META_DESCRIPCION_SEO = ""
    URL_LENGUA_SENAS = ""
    TEXTO_LENGUA_SENAS = ""
    COLOR_PRIMARIO = ""
    COLOR_SECUNDARIO = ""
    COLOR_ACENTO = ""


class ValoresPorDefectoFlujoFormulario:
    """Textos por defecto de modales y terminos del flujo de formularios."""

    MODAL_SALIR_TITULO = "¿Salir sin guardar?"
    MODAL_SALIR_P1 = (
        "Si abandonas la encuesta ahora, perderás todas tus respuestas no guardadas."
    )
    MODAL_SALIR_P2 = (
        "Para conservar tu progreso y retomarlo más tarde, regístrate o "
        "inicia sesión antes de salir."
    )
    MODAL_SALIR_BTN_VOLVER = "Volver a la encuesta (mantenerme aquí)"
    MODAL_SALIR_BTN_SALIR = "Salir sin guardar (perder mi progreso)"
    MODAL_SALIR_LINK_SESION = "Iniciar sesión"

    MODAL_SESION_TITULO = "Inicia sesión o regístrate"
    MODAL_SESION_PARRAFO = (
        "Para conservar tus respuestas y/o retomar encuestas en curso más tarde, "
        "regístrate o inicia sesión antes de salir."
    )
    MODAL_SESION_BTN_LOGIN = "Iniciar sesión"
    MODAL_SESION_BTN_REGISTRO = "Registrarse"
    MODAL_SESION_LINK_CANCELAR = "Cancelar"

    MODAL_GUARDADO_TITULO = "Encuesta guardada con éxito"
    MODAL_GUARDADO_PARRAFO = (
        "Para conservar tu progreso y retomarlo más tarde, regístrate o "
        "inicia sesión antes de salir."
    )
    MODAL_GUARDADO_BTN_SEGUIR = "Seguir viendo"
    MODAL_GUARDADO_BTN_OTRAS = "Ver otras encuestas"

    TERMINOS_TITULO = "Términos y Condiciones de Uso de AppDiversa"
    TERMINOS_P1 = (
        "Al acceder a esta aplicación, se entenderá que Usted ha dado su "
        "autorización para el tratamiento de datos personales, de conformidad "
        "con lo establecido en la Ley 1581 de 2012 y las normas que la reglamentan."
    )
    TERMINOS_P2 = (
        "La información que Usted suministre será gestionada por el DANE, y sus "
        "datos personales serán tratados de manera confidencial y segura, de acuerdo "
        "con la Política de Protección de Datos Personales implementada por la entidad."
    )
    TERMINOS_P3 = (
        "De acuerdo con los objetivos de esta aplicación, se advierte que algunas "
        "de las interacciones pueden implicar el suministro de datos sensibles, los "
        "cuales contarán con un nivel de seguridad alto, en garantía de sus derechos "
        "constitucionales."
    )
    TERMINOS_URL_LEY = (
        "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981"
    )
    TERMINOS_URL_POLITICA_DATOS = (
        "https://www.dane.gov.co/files/images/ventana-unica/documentos/"
        "politicadedatosdane.pdf"
    )
    TERMINOS_EMAIL_SOPORTE = ""
    TERMINOS_BOTON_ACEPTAR = "Aceptar y comenzar la encuesta"
    TERMINOS_BOTON_CERRAR = "Cerrar"
    TERMINOS_ENLACE = "Términos y condiciones"
    TERMINOS_ENLACE_LEY = "Consultar Ley 1581 de 2012"
    TERMINOS_ENLACE_POLITICA_DATOS = (
        "Política de Protección de Datos Personales"
    )


class CodigosLogoInterfaz:
    """Identificadores tecnicos reutilizables para logos de interfaz."""

    PRINCIPAL = "logo_principal"
    SECUNDARIO = "logo_secundario"
    INSTITUCIONAL = "logo_institucional"
    FAVICON = "favicon"


LOGOS_INTERFAZ_PREDEFINIDOS: tuple[tuple[str, str, int], ...] = (
    (CodigosLogoInterfaz.PRINCIPAL, "Logo principal", 1),
    (CodigosLogoInterfaz.SECUNDARIO, "Logo secundario", 2),
    (CodigosLogoInterfaz.INSTITUCIONAL, "Logo institucional", 3),
    (CodigosLogoInterfaz.FAVICON, "Favicon", 4),
)

RUTA_CARGA_FAVICON_INTERFAZ = "interfaz/favicon/"
