"""
Constantes del modulo de internacionalizacion.
"""

from uuid import UUID

NAMESPACE_UUID_ENTIDAD = UUID("a1b2c3d4-e5f6-4789-a012-3456789abcde")

IDIOMA_PREDETERMINADO_CODIGO = "es"


class DireccionTexto:
    """Direcciones de escritura soportadas."""

    LTR = "LTR"
    RTL = "RTL"

    OPCIONES = (LTR, RTL)


class EntidadTraducible:
    """Entidades del sistema que admiten traducciones de contenido."""

    FORMULARIO = "Formulario"
    SECCION_FORMULARIO = "SeccionFormulario"
    PREGUNTA = "Pregunta"
    OPCION_RESPUESTA = "OpcionRespuesta"
    TEXTO_FORMULARIO = "TextoFormulario"
    REGLA_PREGUNTA = "ReglaPregunta"
    CATALOGO = "Catalogo"
    ITEM_CATALOGO = "ItemCatalogo"
    CONFIGURACION_INTERFAZ = "ConfiguracionInterfaz"
    CONFIGURACION_FLUJO_FORMULARIO = "ConfiguracionFlujoFormulario"


class CamposTraducibles:
    """Campos traducibles por entidad."""

    NOMBRE = "nombre"
    DESCRIPCION = "descripcion"
    TITULO = "titulo"
    TEXTO = "texto"
    TOOLTIP = "tooltip"
    MENSAJE_ERROR = "mensaje_error"
    CONTENIDO = "contenido"
    MENSAJE = "mensaje"
    ETIQUETA = "etiqueta"
    INTRODUCCION = "introduccion"
    OBJETIVO = "objetivo"
    TEXTO_AYUDA = "texto_ayuda"
    NOMBRE_APLICATIVO = "nombre_aplicativo"
    DESCRIPCION_APLICATIVO = "descripcion_aplicativo"
    TEXTO_PIE_PAGINA = "texto_pie_pagina"
