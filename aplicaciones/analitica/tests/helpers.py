"""
Helpers compartidos para pruebas de analitica.
"""

import uuid
from decimal import Decimal

from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.respuestas.models import Respuesta
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima


def crear_datos_analitica(
    codigo_formulario: str = "DISC-001",
    estado_sesion: str = EstadoSesionAnonima.FINALIZADA,
) -> tuple[SesionAnonima, Pregunta, Respuesta]:
    """Crea sesion, pregunta y respuesta para pruebas de analitica."""
    formulario = Formulario.objects.create(
        codigo=codigo_formulario,
        nombre="Encuesta de Discriminacion",
        tipo_formulario=TipoFormulario.ENCUESTA,
        estado=EstadoFormulario.PUBLICADO,
    )
    version = FormularioVersion.objects.create(
        formulario=formulario,
        numero_version=1,
        estado=EstadoFormulario.PUBLICADO,
        es_publicada=True,
    )
    sesion = SesionAnonima.objects.create(
        uuid_sesion=uuid.uuid4(),
        formulario=formulario,
        version_formulario=version,
        estado=estado_sesion,
        es_offline=False,
    )
    seccion = SeccionFormulario.objects.create(
        formulario_version=version,
        codigo="CAP-I",
        titulo="Capitulo I - Identificacion",
        orden=1,
    )
    pregunta = Pregunta.objects.create(
        seccion=seccion,
        codigo="P1",
        texto="Cuantos anos cumplidos tiene?",
        tipo_pregunta=TipoPregunta.NUMERO,
        orden=1,
    )
    respuesta = Respuesta.objects.create(
        sesion=sesion,
        pregunta=pregunta,
        valor_numero=Decimal("25"),
    )
    return sesion, pregunta, respuesta
