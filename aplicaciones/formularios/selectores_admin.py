"""
Selectores de consulta para la API administrativa de formularios.
"""

from django.db.models import QuerySet

from aplicaciones.formularios.models import (
    Formulario,
    FormularioVersion,
    OpcionRespuesta,
    Pregunta,
    ReglaPregunta,
    SeccionFormulario,
    TextoFormulario,
)
from aplicaciones.formularios.selectores import (
    FormularioEstructuraDatos,
    _cargar_version_con_estructura,
)
from aplicaciones.respuestas.models import Respuesta


def listar_formularios_admin() -> QuerySet[Formulario]:
    """Lista todos los formularios activos para administracion."""
    return Formulario.objects.all().order_by("orden", "nombre")


def obtener_formulario_admin_por_id(formulario_id: int) -> Formulario | None:
    """Obtiene un formulario por identificador numerico."""
    return Formulario.objects.filter(pk=formulario_id).first()


def listar_versiones_formulario(formulario_id: int) -> QuerySet[FormularioVersion]:
    """Lista versiones de un formulario."""
    return FormularioVersion.objects.filter(
        formulario_id=formulario_id,
    ).order_by("-numero_version")


def obtener_version_admin_por_id(version_id: int) -> FormularioVersion | None:
    """Obtiene una version por identificador."""
    return FormularioVersion.objects.filter(pk=version_id).first()


def obtener_version_borrador_editable(
    formulario_id: int,
) -> FormularioVersion | None:
    """Retorna la version borrador mas reciente de un formulario."""
    return (
        FormularioVersion.objects.filter(
            formulario_id=formulario_id,
            estado="borrador",
            es_publicada=False,
        )
        .order_by("-numero_version")
        .first()
    )


def obtener_version_admin_para_edicion(
    formulario_id: int,
) -> FormularioVersion | None:
    """Resuelve la version editable o consultable en el panel administrativo."""
    borrador = obtener_version_borrador_editable(formulario_id)
    if borrador is not None:
        return borrador

    publicada = (
        FormularioVersion.objects.filter(
            formulario_id=formulario_id,
            es_publicada=True,
        )
        .order_by("-numero_version")
        .first()
    )
    if publicada is not None:
        return publicada

    return (
        FormularioVersion.objects.filter(formulario_id=formulario_id)
        .order_by("-numero_version")
        .first()
    )


def obtener_estructura_formulario_admin(
    formulario_id: int,
) -> FormularioEstructuraDatos | None:
    """Retorna la estructura completa del formulario para administracion."""
    formulario = obtener_formulario_admin_por_id(formulario_id)
    if formulario is None:
        return None

    version = obtener_version_admin_para_edicion(formulario_id)
    if version is None:
        return None

    version_con_estructura = _cargar_version_con_estructura(version.pk)
    return FormularioEstructuraDatos(
        formulario=formulario,
        version=version_con_estructura,
    )


def obtener_seccion_por_codigo_en_formulario(
    formulario_id: int,
    codigo_seccion: str,
) -> SeccionFormulario | None:
    """Obtiene una seccion activa por codigo dentro del formulario."""
    version = obtener_version_admin_para_edicion(formulario_id)
    if version is None:
        return None
    return SeccionFormulario.objects.filter(
        formulario_version_id=version.pk,
        codigo=codigo_seccion,
        esta_eliminado=False,
    ).first()


def obtener_pregunta_por_codigo_en_formulario(
    formulario_id: int,
    codigo_pregunta: str,
) -> Pregunta | None:
    """Obtiene una pregunta activa por codigo dentro del formulario."""
    version = obtener_version_admin_para_edicion(formulario_id)
    if version is None:
        return None
    return (
        Pregunta.objects.filter(
            seccion__formulario_version_id=version.pk,
            codigo=codigo_pregunta,
            esta_eliminado=False,
        )
        .select_related("seccion__formulario_version")
        .first()
    )


def obtener_opcion_por_codigo_en_formulario(
    formulario_id: int,
    codigo_opcion: str,
) -> OpcionRespuesta | None:
    """Obtiene una opcion activa por codigo dentro del formulario."""
    version = obtener_version_admin_para_edicion(formulario_id)
    if version is None:
        return None
    return (
        OpcionRespuesta.objects.filter(
            pregunta__seccion__formulario_version_id=version.pk,
            codigo=codigo_opcion,
            esta_eliminado=False,
        )
        .select_related("pregunta__seccion__formulario_version")
        .first()
    )


def listar_reglas_formulario_admin(formulario_id: int) -> QuerySet[ReglaPregunta]:
    """Lista reglas activas de la version administrativa del formulario."""
    version = obtener_version_admin_para_edicion(formulario_id)
    if version is None:
        return ReglaPregunta.objects.none()
    return (
        ReglaPregunta.objects.filter(
            pregunta_origen__seccion__formulario_version_id=version.pk,
            esta_eliminado=False,
        )
        .select_related(
            "pregunta_origen",
            "pregunta_destino",
            "seccion_destino",
        )
        .order_by("pregunta_origen__orden", "pk")
    )


def obtener_regla_en_formulario(
    formulario_id: int,
    regla_id: int,
) -> ReglaPregunta | None:
    """Obtiene una regla si pertenece a la version administrativa del formulario."""
    return listar_reglas_formulario_admin(formulario_id).filter(pk=regla_id).first()


def listar_secciones_version(version_id: int) -> QuerySet[SeccionFormulario]:
    """Lista secciones activas de una version."""
    return SeccionFormulario.objects.filter(
        formulario_version_id=version_id,
    ).order_by("orden")


def obtener_seccion_admin_por_id(seccion_id: int) -> SeccionFormulario | None:
    """Obtiene una seccion por identificador."""
    return SeccionFormulario.objects.filter(pk=seccion_id).first()


def listar_preguntas_seccion(seccion_id: int) -> QuerySet[Pregunta]:
    """Lista preguntas activas de una seccion."""
    return Pregunta.objects.filter(seccion_id=seccion_id).order_by("orden")


def obtener_pregunta_admin_por_id(pregunta_id: int) -> Pregunta | None:
    """Obtiene una pregunta por identificador."""
    return Pregunta.objects.select_related(
        "seccion__formulario_version",
    ).filter(pk=pregunta_id).first()


def listar_opciones_pregunta(pregunta_id: int) -> QuerySet[OpcionRespuesta]:
    """Lista opciones de una pregunta."""
    return OpcionRespuesta.objects.filter(pregunta_id=pregunta_id).order_by("orden")


def obtener_opcion_admin_por_id(opcion_id: int) -> OpcionRespuesta | None:
    """Obtiene una opcion por identificador."""
    return OpcionRespuesta.objects.filter(pk=opcion_id).first()


def listar_reglas_pregunta(pregunta_id: int) -> QuerySet[ReglaPregunta]:
    """Lista reglas de una pregunta origen."""
    return ReglaPregunta.objects.filter(
        pregunta_origen_id=pregunta_id,
    ).order_by("pk")


def obtener_regla_admin_por_id(regla_id: int) -> ReglaPregunta | None:
    """Obtiene una regla por identificador."""
    return ReglaPregunta.objects.filter(pk=regla_id).first()


def listar_textos_formulario(formulario_id: int) -> QuerySet[TextoFormulario]:
    """Lista textos de todas las versiones de un formulario."""
    return TextoFormulario.objects.filter(
        formulario_version__formulario_id=formulario_id,
    ).order_by("formulario_version__numero_version", "orden")


def obtener_texto_admin_por_id(texto_id: int) -> TextoFormulario | None:
    """Obtiene un texto por identificador."""
    return TextoFormulario.objects.filter(pk=texto_id).first()


def version_tiene_respuestas(version_id: int) -> bool:
    """Indica si existen respuestas asociadas a preguntas de la version."""
    return Respuesta.objects.filter(
        pregunta__seccion__formulario_version_id=version_id,
        esta_eliminado=False,
    ).exists()


def codigo_formulario_activo_duplicado(
    codigo: str,
    excluir_id: int | None = None,
) -> bool:
    """Valida unicidad de codigo de formulario entre registros activos."""
    queryset = Formulario.objects.filter(codigo=codigo, esta_eliminado=False)
    if excluir_id is not None:
        queryset = queryset.exclude(pk=excluir_id)
    return queryset.exists()


def codigo_seccion_activo_duplicado(
    version_id: int,
    codigo: str,
    excluir_id: int | None = None,
) -> bool:
    """Valida unicidad de codigo de seccion en una version."""
    queryset = SeccionFormulario.objects.filter(
        formulario_version_id=version_id,
        codigo=codigo,
        esta_eliminado=False,
    )
    if excluir_id is not None:
        queryset = queryset.exclude(pk=excluir_id)
    return queryset.exists()


def codigo_pregunta_activo_duplicado(
    seccion_id: int,
    codigo: str,
    excluir_id: int | None = None,
) -> bool:
    """Valida unicidad de codigo de pregunta en una seccion."""
    queryset = Pregunta.objects.filter(
        seccion_id=seccion_id,
        codigo=codigo,
        esta_eliminado=False,
    )
    if excluir_id is not None:
        queryset = queryset.exclude(pk=excluir_id)
    return queryset.exists()
