"""
Selectores de consulta para el motor de formularios parametrizables.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from django.db.models import Prefetch, Q, QuerySet
from django.utils import timezone

from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    OpcionRespuesta,
    Pregunta,
    PreguntaMatrizColumna,
    PreguntaMatrizFila,
    ReglaPregunta,
    SeccionFormulario,
    TextoFormulario,
)


@dataclass(frozen=True)
class FormularioEstructuraDatos:
    """Agrupa el formulario vigente con su version publicada y datos relacionados."""

    formulario: Formulario
    version: FormularioVersion


def _construir_filtro_formulario_publicado_no_vencido(ahora: datetime) -> Q:
    """Construye filtro de formularios publicados que no han vencido."""
    return Q(estado=EstadoFormulario.PUBLICADO) & (
        Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=ahora)
    )


def _construir_filtro_formulario_iniciable(ahora: datetime) -> Q:
    """Construye filtro de formularios publicados que pueden iniciarse ahora."""
    return _construir_filtro_formulario_publicado_no_vencido(ahora) & (
        Q(fecha_inicio__isnull=True) | Q(fecha_inicio__lte=ahora)
    )


def _construir_filtro_formulario_vigente(ahora: datetime) -> Q:
    """Construye el filtro de formularios publicados iniciables en el instante dado."""
    return _construir_filtro_formulario_iniciable(ahora)


def _obtener_queryset_preguntas_activas() -> QuerySet[Pregunta]:
    """Retorna preguntas activas con relaciones necesarias para la estructura."""
    return (
        Pregunta.objects.filter(esta_activa=True)
        .select_related(
            "catalogo_asociado",
            "pregunta_padre_catalogo",
            "pregunta_origen_flujo",
        )
        .order_by("orden")
        .prefetch_related(
            Prefetch(
                "opciones",
                queryset=OpcionRespuesta.objects.filter(esta_activa=True)
                .select_related("pregunta")
                .order_by(
                    "orden",
                ),
            ),
            Prefetch(
                "filas_matriz",
                queryset=PreguntaMatrizFila.objects.filter(esta_activa=True).order_by(
                    "orden",
                ),
            ),
            Prefetch(
                "columnas_matriz",
                queryset=PreguntaMatrizColumna.objects.filter(
                    esta_activa=True,
                ).order_by("orden"),
            ),
            Prefetch(
                "reglas_origen",
                queryset=ReglaPregunta.objects.filter(esta_activa=True),
            ),
            Prefetch(
                "preguntas_dependientes_catalogo",
                queryset=Pregunta.objects.filter(
                    esta_activa=True,
                    esta_eliminado=False,
                )
                .select_related("catalogo_asociado", "pregunta_padre_catalogo")
                .order_by("orden"),
            ),
        )
    )


def _cargar_version_con_estructura(version_id: int) -> FormularioVersion:
    """Carga una version con textos, secciones y preguntas optimizadas."""
    preguntas_activas = _obtener_queryset_preguntas_activas()
    secciones_activas = (
        SeccionFormulario.objects.filter(esta_activo=True, es_visible=True)
        .order_by("orden")
        .prefetch_related(Prefetch("preguntas", queryset=preguntas_activas))
    )
    textos_activos = TextoFormulario.objects.filter(esta_activo=True).order_by("orden")

    return (
        FormularioVersion.objects.select_related("formulario")
        .prefetch_related(
            Prefetch("textos", queryset=textos_activos, to_attr="textos_activos"),
            Prefetch(
                "secciones",
                queryset=secciones_activas,
                to_attr="secciones_activas",
            ),
        )
        .get(pk=version_id)
    )


def obtener_reglas_activas_version(
    version_formulario: FormularioVersion,
) -> QuerySet[ReglaPregunta]:
    """Retorna reglas activas de una version con relaciones necesarias."""
    return (
        ReglaPregunta.objects.filter(
            pregunta_origen__seccion__formulario_version=version_formulario,
            esta_activa=True,
            esta_eliminado=False,
        )
        .select_related(
            "pregunta_origen",
            "pregunta_destino",
            "seccion_destino",
            "pregunta_origen__seccion",
        )
        .order_by("pregunta_origen__orden", "pk")
    )


def obtener_reglas_activas_por_pregunta_origen(
    version_formulario: FormularioVersion,
    codigo_pregunta: str,
) -> QuerySet[ReglaPregunta]:
    """Retorna reglas activas cuya pregunta origen coincide con el codigo."""
    return obtener_reglas_activas_version(version_formulario).filter(
        pregunta_origen__codigo=codigo_pregunta,
    )


def obtener_formularios_disponibles() -> QuerySet[Formulario]:
    """Retorna formularios publicados no vencidos, incluidos los de inicio futuro."""
    ahora = timezone.now()
    return Formulario.objects.filter(
        _construir_filtro_formulario_publicado_no_vencido(ahora),
    ).order_by("orden", "nombre")


def obtener_formulario_por_uuid(uuid_formulario: UUID) -> Formulario | None:
    """Retorna un formulario publicado que puede iniciarse en el instante actual."""
    return obtener_formulario_iniciable_por_uuid(uuid_formulario)


def obtener_formulario_iniciable_por_uuid(uuid_formulario: UUID) -> Formulario | None:
    """Retorna un formulario publicado iniciable identificado por su uuid."""
    ahora = timezone.now()
    return Formulario.objects.filter(
        uuid=uuid_formulario,
    ).filter(
        _construir_filtro_formulario_iniciable(ahora),
    ).first()


def obtener_formulario_publicado_listado_por_uuid(
    uuid_formulario: UUID,
) -> Formulario | None:
    """Retorna un formulario publicado no vencido, aunque tenga fecha de inicio futura."""
    ahora = timezone.now()
    return Formulario.objects.filter(
        uuid=uuid_formulario,
    ).filter(
        _construir_filtro_formulario_publicado_no_vencido(ahora),
    ).first()


def obtener_version_publicada(formulario: Formulario) -> FormularioVersion | None:
    """Retorna la version publicada activa de un formulario."""
    return FormularioVersion.objects.filter(
        formulario=formulario,
        es_publicada=True,
        estado=EstadoFormulario.PUBLICADO,
    ).first()


def obtener_estructura_formulario(
    uuid_formulario: UUID,
) -> FormularioEstructuraDatos | None:
    """Retorna el formulario vigente con su estructura completa prefetcheada."""
    formulario = obtener_formulario_por_uuid(uuid_formulario)
    if formulario is None:
        return None

    version_publicada = obtener_version_publicada(formulario)
    if version_publicada is None:
        return None

    version_con_estructura = _cargar_version_con_estructura(version_publicada.pk)
    return FormularioEstructuraDatos(
        formulario=version_con_estructura.formulario,
        version=version_con_estructura,
    )
