"""
Utilidades para pruebas de la API administrativa de formularios.
"""

from aplicaciones.formularios.models import (
    AccionRegla,
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    OperadorRegla,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.usuarios.tests.helpers import inicializar_entorno_usuarios

URL_ADMIN_FORMULARIOS = "/api/v1/admin/formularios/"


def crear_formulario_admin_prueba(codigo: str = "form_admin") -> Formulario:
    """Crea formulario con version borrador para pruebas admin."""
    formulario = Formulario.objects.create(
        codigo=codigo,
        nombre=f"Formulario {codigo}",
        tipo_formulario=TipoFormulario.ENCUESTA,
        estado=EstadoFormulario.BORRADOR,
    )
    FormularioVersion.objects.create(
        formulario=formulario,
        numero_version=1,
        estado=EstadoFormulario.BORRADOR,
    )
    formulario.version_actual = 1
    formulario.save(update_fields=["version_actual"])
    return formulario


def crear_seccion_prueba(version: FormularioVersion, codigo: str = "sec1") -> SeccionFormulario:
    """Crea seccion minima en una version."""
    return SeccionFormulario.objects.create(
        formulario_version=version,
        codigo=codigo,
        titulo="Seccion prueba",
        orden=1,
    )


def crear_pregunta_prueba(seccion: SeccionFormulario, codigo: str = "p1") -> Pregunta:
    """Crea pregunta minima en una seccion."""
    return Pregunta.objects.create(
        seccion=seccion,
        codigo=codigo,
        texto="Pregunta prueba",
        tipo_pregunta=TipoPregunta.TEXTO_CORTO,
        orden=1,
    )


def preparar_entorno_admin() -> None:
    """Inicializa grupos del sistema para pruebas admin."""
    inicializar_entorno_usuarios()
