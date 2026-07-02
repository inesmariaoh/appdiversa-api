"""
Selectores de consulta para respuestas.
"""

from uuid import UUID

from django.db.models import QuerySet

from aplicaciones.formularios.filtros.evaluador import evaluar_pregunta_filtro
from aplicaciones.formularios.models import FormularioVersion, Pregunta
from aplicaciones.formularios.reglas.evaluador import evaluar_reglas
from aplicaciones.formularios.reglas.flujo_visual import (
    construir_mapa_destino_origen_mostrar,
    ordenar_preguntas_flujo_visual,
)
from aplicaciones.formularios.reglas.normalizadores import normalizar_valor_respuesta
from aplicaciones.formularios.reglas.resultado import ResultadoReglas
from aplicaciones.formularios.reglas.visibilidad import (
    filtrar_preguntas_visibles,
    pregunta_obligatoria_efectiva,
)
from aplicaciones.formularios.selectores import obtener_reglas_activas_version
from aplicaciones.respuestas.models import Respuesta
from aplicaciones.sesiones_anonimas.models import SesionAnonima


def obtener_pregunta_por_codigo_en_version(
    version_formulario: FormularioVersion,
    codigo_pregunta: str,
) -> Pregunta | None:
    """Retorna una pregunta activa por codigo dentro de una version."""
    return (
        Pregunta.objects.select_related("seccion", "catalogo_asociado")
        .filter(
            seccion__formulario_version=version_formulario,
            codigo=codigo_pregunta,
            esta_activa=True,
        )
        .first()
    )


def obtener_respuesta(sesion: SesionAnonima, pregunta: Pregunta) -> Respuesta | None:
    """Retorna la respuesta asociada a una sesion y pregunta."""
    return Respuesta.objects.filter(sesion=sesion, pregunta=pregunta).first()


def obtener_respuestas_sesion(sesion: SesionAnonima) -> QuerySet[Respuesta]:
    """Retorna las respuestas de una sesion con relaciones necesarias."""
    return (
        Respuesta.objects.filter(sesion=sesion, esta_eliminado=False)
        .select_related("pregunta")
        .order_by("pregunta__orden")
    )


def obtener_todas_preguntas_activas_sesion(
    sesion: SesionAnonima,
) -> list[Pregunta]:
    """Retorna todas las preguntas activas de la version ordenadas por seccion y orden."""
    return list(
        Pregunta.objects.filter(
            seccion__formulario_version=sesion.version_formulario,
            esta_activa=True,
        )
        .select_related("seccion", "pregunta_origen_flujo", "catalogo_asociado")
        .order_by("seccion__orden", "orden"),
    )


def _construir_mapa_respuestas_por_codigo(sesion: SesionAnonima) -> dict[str, object]:
    """Construye un mapa de valores de respuesta indexado por codigo de pregunta."""
    respuestas = obtener_respuestas_sesion(sesion)
    mapa: dict[str, object] = {}
    for respuesta in respuestas:
        mapa[respuesta.pregunta.codigo] = normalizar_valor_respuesta(respuesta)
    return mapa


def obtener_preguntas_filtro_sesion(sesion: SesionAnonima) -> list[Pregunta]:
    """Retorna preguntas marcadas como filtro/preliminares de la sesion."""
    return [
        pregunta
        for pregunta in obtener_todas_preguntas_activas_sesion(sesion)
        if pregunta.es_pregunta_filtro
    ]


def obtener_preguntas_principales_sesion(sesion: SesionAnonima) -> list[Pregunta]:
    """Retorna preguntas principales excluyendo filtros preliminares."""
    return [
        pregunta
        for pregunta in obtener_todas_preguntas_activas_sesion(sesion)
        if not pregunta.es_pregunta_filtro
    ]


def evaluar_filtros_sesion(sesion: SesionAnonima) -> dict[str, object]:
    """Evalua si la sesion cumple todas las preguntas filtro configuradas."""
    preguntas_filtro = obtener_preguntas_filtro_sesion(sesion)
    mapa_respuestas = _construir_mapa_respuestas_por_codigo(sesion)
    detalle: list[dict[str, object]] = []
    cumple_todos = True

    for pregunta in preguntas_filtro:
        valor = mapa_respuestas.get(pregunta.codigo)
        cumple, mensaje = evaluar_pregunta_filtro(pregunta, valor)
        if not cumple:
            cumple_todos = False
        detalle.append(
            {
                "codigo": pregunta.codigo,
                "cumple": cumple,
                "mensaje": mensaje,
                "bloquea_continuacion": pregunta.bloquea_continuacion_si_no_cumple,
            },
        )

    return {
        "cumple_filtros": cumple_todos,
        "filtros": detalle,
    }


def evaluar_resultado_reglas_sesion(sesion: SesionAnonima) -> ResultadoReglas:
    """Evalua las reglas activas de la sesion y retorna el resultado agregado."""
    reglas = list(obtener_reglas_activas_version(sesion.version_formulario))
    mapa_respuestas = _construir_mapa_respuestas_por_codigo(sesion)
    return evaluar_reglas(reglas, mapa_respuestas)


def obtener_preguntas_flujo_visual_sesion(
    sesion: SesionAnonima,
    resultado: ResultadoReglas | None = None,
) -> list[Pregunta]:
    """Retorna preguntas visibles reordenadas para el flujo visual del formulario."""
    resultado_evaluado = resultado or evaluar_resultado_reglas_sesion(sesion)
    preguntas = obtener_preguntas_principales_sesion(sesion)
    visibles = filtrar_preguntas_visibles(preguntas, resultado_evaluado)
    codigos_visibles = frozenset(pregunta.codigo for pregunta in visibles)
    reglas = list(obtener_reglas_activas_version(sesion.version_formulario))
    mapa_destino_origen = construir_mapa_destino_origen_mostrar(reglas)
    return ordenar_preguntas_flujo_visual(preguntas, codigos_visibles, mapa_destino_origen)


def obtener_preguntas_obligatorias_efectivas_sesion(
    sesion: SesionAnonima,
    resultado: ResultadoReglas | None = None,
) -> list[Pregunta]:
    """Retorna preguntas obligatorias segun reglas y visibilidad efectiva."""
    resultado_evaluado = resultado or evaluar_resultado_reglas_sesion(sesion)
    preguntas_flujo = obtener_preguntas_flujo_visual_sesion(sesion, resultado_evaluado)
    return [
        pregunta
        for pregunta in preguntas_flujo
        if pregunta_obligatoria_efectiva(pregunta, resultado_evaluado)
    ]


def obtener_preguntas_obligatorias_sesion(
    sesion: SesionAnonima,
) -> QuerySet[Pregunta]:
    """Retorna preguntas obligatorias activas de la version del formulario."""
    return (
        Pregunta.objects.filter(
            seccion__formulario_version=sesion.version_formulario,
            esta_activa=True,
            es_obligatoria=True,
        )
        .select_related("seccion")
        .order_by("seccion__orden", "orden")
    )


def obtener_respuestas_por_pregunta_sesion(
    sesion: SesionAnonima,
) -> dict[int, Respuesta]:
    """Retorna un mapa de respuestas activas indexado por id de pregunta."""
    respuestas = Respuesta.objects.filter(
        sesion=sesion,
        esta_eliminado=False,
    )
    return {respuesta.pregunta_id: respuesta for respuesta in respuestas}


def obtener_resumen_respuestas_sesion(sesion: SesionAnonima) -> QuerySet[Respuesta]:
    """Retorna respuestas activas con pregunta y seccion optimizadas."""
    return (
        Respuesta.objects.filter(sesion=sesion, esta_eliminado=False)
        .select_related("pregunta", "pregunta__seccion")
        .prefetch_related(
            "pregunta__opciones",
            "pregunta__filas_matriz",
            "pregunta__columnas_matriz",
        )
        .order_by("pregunta__seccion__orden", "pregunta__orden")
    )


def obtener_respuesta_por_uuid_local(uuid_local: UUID) -> Respuesta | None:
    """Retorna una respuesta activa por su identificador local del dispositivo."""
    return (
        Respuesta.objects.select_related("pregunta", "sesion")
        .filter(uuid_local=uuid_local)
        .first()
    )


def obtener_respuesta_por_uuid_local_incluyendo_eliminadas(
    uuid_local: UUID,
) -> Respuesta | None:
    """Retorna una respuesta por uuid_local sin filtrar eliminaciones logicas."""
    return (
        Respuesta.todos.select_related("pregunta", "sesion")
        .filter(uuid_local=uuid_local)
        .first()
    )
