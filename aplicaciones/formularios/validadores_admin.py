"""
Validadores de negocio para la API administrativa de formularios.
"""

from aplicaciones.formularios.constantes_admin import MensajesFormularioAdmin
from aplicaciones.formularios.excepciones_admin import ValidacionFormularioAdminError
from aplicaciones.formularios.models import (
    AccionRegla,
    FormularioVersion,
    Pregunta,
    ReglaPregunta,
    SeccionFormulario,
)
from aplicaciones.formularios.selectores_admin import (
    codigo_formulario_activo_duplicado,
    codigo_pregunta_activo_duplicado,
    codigo_seccion_activo_duplicado,
    version_tiene_respuestas,
)

_ACCIONES_REQUIEREN_PREGUNTA_DESTINO = frozenset(
    {
        AccionRegla.MOSTRAR,
        AccionRegla.OCULTAR,
        AccionRegla.HABILITAR,
        AccionRegla.DESHABILITAR,
        AccionRegla.HACER_OBLIGATORIA,
        AccionRegla.HACER_OPCIONAL,
        AccionRegla.SALTAR_A_PREGUNTA,
    },
)


def validar_codigo_formulario_unico(
    codigo: str,
    excluir_id: int | None = None,
) -> None:
    """Valida unicidad de codigo de formulario entre activos."""
    if codigo_formulario_activo_duplicado(codigo, excluir_id):
        raise ValidacionFormularioAdminError(MensajesFormularioAdmin.CODIGO_DUPLICADO)


def validar_codigo_seccion_unico(
    version_id: int,
    codigo: str,
    excluir_id: int | None = None,
) -> None:
    """Valida unicidad de codigo de seccion en la version."""
    if codigo_seccion_activo_duplicado(version_id, codigo, excluir_id):
        raise ValidacionFormularioAdminError(MensajesFormularioAdmin.CODIGO_DUPLICADO)


def validar_codigo_pregunta_unico(
    seccion_id: int,
    codigo: str,
    excluir_id: int | None = None,
) -> None:
    """Valida unicidad de codigo de pregunta en la seccion."""
    if codigo_pregunta_activo_duplicado(seccion_id, codigo, excluir_id):
        raise ValidacionFormularioAdminError(MensajesFormularioAdmin.CODIGO_DUPLICADO)


def validar_pregunta_catalogo(pregunta: Pregunta) -> None:
    """Valida consistencia entre usa_catalogo y catalogo_asociado."""
    if pregunta.catalogo_asociado_id is not None and not pregunta.usa_catalogo:
        raise ValidacionFormularioAdminError(
            MensajesFormularioAdmin.CATALOGO_INCONSISTENTE,
        )
    if pregunta.usa_catalogo and pregunta.catalogo_asociado_id is None:
        raise ValidacionFormularioAdminError(
            MensajesFormularioAdmin.CATALOGO_INCONSISTENTE,
        )


def validar_regla_destino(regla: ReglaPregunta) -> None:
    """Valida destino de regla segun la accion configurada."""
    if regla.accion == AccionRegla.SALTAR_A_SECCION:
        if regla.seccion_destino_id is None:
            raise ValidacionFormularioAdminError(
                MensajesFormularioAdmin.REGLA_DESTINO_INVALIDA,
            )
        return

    if regla.accion in _ACCIONES_REQUIEREN_PREGUNTA_DESTINO:
        if regla.pregunta_destino_id is None:
            raise ValidacionFormularioAdminError(
                MensajesFormularioAdmin.REGLA_DESTINO_INVALIDA,
            )


def validar_version_editable(version: FormularioVersion) -> None:
    """Impide editar versiones publicadas con respuestas registradas."""
    if version.es_publicada and version_tiene_respuestas(version.pk):
        raise ValidacionFormularioAdminError(
            MensajesFormularioAdmin.VERSION_PUBLICADA_CON_RESPUESTAS,
        )


def validar_publicacion_version(version: FormularioVersion) -> None:
    """Valida requisitos para publicar una version de formulario."""
    secciones = SeccionFormulario.objects.filter(
        formulario_version=version,
        esta_activo=True,
        esta_eliminado=False,
    )
    if not secciones.exists():
        raise ValidacionFormularioAdminError(
            MensajesFormularioAdmin.VERSION_SIN_SECCIONES,
        )

    for seccion in secciones:
        tiene_preguntas = Pregunta.objects.filter(
            seccion=seccion,
            esta_activa=True,
            esta_eliminado=False,
        ).exists()
        if not tiene_preguntas:
            raise ValidacionFormularioAdminError(
                MensajesFormularioAdmin.SECCION_SIN_PREGUNTAS,
            )
