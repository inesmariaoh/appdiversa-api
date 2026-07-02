"""
Servicios de fachada para rutas administrativas centradas en formulario.

Adapta el contrato del panel (codigos de entidad) al motor existente por identificadores.
"""

from collections.abc import Callable
from typing import Any

from django.db import transaction

from aplicaciones.catalogos.models import Catalogo
from aplicaciones.formularios.constantes_admin import MensajesFormularioAdmin
from aplicaciones.formularios.excepciones_admin import (
    FormularioAdminNoEncontradoError,
    OpcionAdminNoEncontradaError,
    PreguntaAdminNoEncontradaError,
    ReglaAdminNoEncontradaError,
    SeccionAdminNoEncontradaError,
    ValidacionFormularioAdminError,
    VersionAdminNoEncontradaError,
)
from aplicaciones.formularios.models import (
    Formulario,
    FormularioVersion,
    OpcionRespuesta,
    Pregunta,
    ReglaPregunta,
    SeccionFormulario,
    TextoFormulario,
)
from aplicaciones.formularios.selectores_admin import (
    listar_reglas_formulario_admin,
    obtener_formulario_admin_por_id,
    obtener_opcion_por_codigo_en_formulario,
    obtener_pregunta_por_codigo_en_formulario,
    obtener_regla_en_formulario,
    obtener_seccion_por_codigo_en_formulario,
    obtener_version_admin_para_edicion,
    obtener_version_borrador_editable,
)
from aplicaciones.formularios.validadores_admin import validar_version_editable
from aplicaciones.formularios.servicios_admin import (
    actualizar_opcion_admin,
    actualizar_pregunta_admin,
    actualizar_regla_admin,
    actualizar_seccion_admin,
    actualizar_texto_admin,
    cerrar_version_admin,
    crear_opcion_admin,
    crear_pregunta_admin,
    crear_regla_admin,
    crear_seccion_admin,
    duplicar_pregunta_admin,
    eliminar_opcion_admin,
    eliminar_pregunta_admin,
    eliminar_regla_admin,
    eliminar_seccion_admin,
    publicar_version_admin,
    reordenar_opciones_admin,
    reordenar_preguntas_admin,
    reordenar_secciones_admin,
)


def _obtener_version_edicion_o_error(formulario_id: int) -> FormularioVersion:
    """Retorna la version administrativa del formulario o lanza error funcional."""
    version = obtener_version_admin_para_edicion(formulario_id)
    if version is None:
        raise FormularioAdminNoEncontradoError()
    return version


def _resolver_catalogo_id(codigo_catalogo: str | None) -> int | None:
    """Resuelve el identificador de catalogo a partir de su codigo."""
    if not codigo_catalogo:
        return None
    catalogo = Catalogo.objects.filter(
        codigo=codigo_catalogo,
        esta_activo=True,
    ).first()
    if catalogo is None:
        raise ValidacionFormularioAdminError(
            MensajesFormularioAdmin.CATALOGO_INCONSISTENTE,
        )
    return catalogo.pk


def _resolver_pregunta_objeto(
    formulario_id: int,
    codigo_pregunta: str | None,
) -> Pregunta | None:
    """Resuelve una pregunta por codigo dentro del formulario."""
    if not codigo_pregunta:
        return None
    pregunta = obtener_pregunta_por_codigo_en_formulario(formulario_id, codigo_pregunta)
    if pregunta is None:
        raise PreguntaAdminNoEncontradaError()
    return pregunta


def _resolver_seccion_objeto(
    formulario_id: int,
    codigo_seccion: str | None,
) -> SeccionFormulario | None:
    """Resuelve una seccion por codigo dentro del formulario."""
    if not codigo_seccion:
        return None
    seccion = obtener_seccion_por_codigo_en_formulario(formulario_id, codigo_seccion)
    if seccion is None:
        raise SeccionAdminNoEncontradaError()
    return seccion


def _preparar_datos_pregunta_frontend(
    formulario_id: int,
    datos: dict[str, Any],
) -> tuple[int, dict[str, Any]]:
    """Traduce la entrada del panel a datos del servicio de preguntas."""
    seccion_codigo = datos.get("seccion_codigo")
    if not seccion_codigo:
        raise ValidacionFormularioAdminError(
            MensajesFormularioAdmin.SECCION_NO_ENCONTRADA,
        )
    seccion = _resolver_seccion_objeto(formulario_id, seccion_codigo)
    if seccion is None:
        raise SeccionAdminNoEncontradaError()

    datos_servicio = {
        clave: valor
        for clave, valor in datos.items()
        if clave not in {"seccion_codigo", "catalogo_asociado", "pregunta_padre_catalogo"}
    }
    if "catalogo_asociado" in datos:
        datos_servicio["catalogo_asociado"] = _resolver_catalogo_id(
            datos.get("catalogo_asociado"),
        )
    if "pregunta_padre_catalogo" in datos:
        padre = _resolver_pregunta_objeto(
            formulario_id,
            datos.get("pregunta_padre_catalogo"),
        )
        datos_servicio["pregunta_padre_catalogo"] = padre.pk if padre else None
    return seccion.pk, datos_servicio


def serializar_regla_frontend(regla: ReglaPregunta) -> dict[str, Any]:
    """Serializa una regla con codigos legibles para el panel administrativo."""
    return {
        "id": regla.pk,
        "pregunta_origen": regla.pregunta_origen.codigo,
        "operador": regla.operador,
        "valor_esperado": regla.valor_esperado,
        "accion": regla.accion,
        "pregunta_destino": (
            regla.pregunta_destino.codigo if regla.pregunta_destino else None
        ),
        "seccion_destino": (
            regla.seccion_destino.codigo if regla.seccion_destino else None
        ),
        "mensaje": regla.mensaje,
        "esta_activa": regla.esta_activa,
    }


def _preparar_datos_regla_frontend(
    formulario_id: int,
    datos: dict[str, Any],
) -> dict[str, Any]:
    """Traduce destinos por codigo al formato del servicio de reglas."""
    return {
        "operador": datos["operador"],
        "valor_esperado": datos["valor_esperado"],
        "accion": datos["accion"],
        "mensaje": datos.get("mensaje", ""),
        "esta_activa": datos.get("esta_activa", True),
        "pregunta_destino": _resolver_pregunta_objeto(
            formulario_id,
            datos.get("pregunta_destino"),
        ),
        "seccion_destino": _resolver_seccion_objeto(
            formulario_id,
            datos.get("seccion_destino"),
        ),
    }


def _items_reordenamiento_por_codigos(
    formulario_id: int,
    codigos: list[str],
    resolver: Callable[[int, str], Any],
    error_no_encontrado: type[Exception],
) -> list[dict[str, int]]:
    """Construye items id/orden a partir de una lista ordenada de codigos."""
    items: list[dict[str, int]] = []
    for orden, codigo in enumerate(codigos, start=1):
        entidad = resolver(formulario_id, codigo)
        if entidad is None:
            raise error_no_encontrado()
        items.append({"id": entidad.pk, "orden": orden})
    return items


def crear_seccion_formulario_admin(
    formulario_id: int,
    datos: dict[str, Any],
) -> SeccionFormulario:
    """Crea una seccion en la version administrativa del formulario."""
    version = _obtener_version_edicion_o_error(formulario_id)
    return crear_seccion_admin(version.pk, datos)


def actualizar_seccion_formulario_admin(
    formulario_id: int,
    codigo_seccion: str,
    datos: dict[str, Any],
) -> SeccionFormulario:
    """Actualiza una seccion identificada por codigo."""
    seccion = obtener_seccion_por_codigo_en_formulario(formulario_id, codigo_seccion)
    if seccion is None:
        raise SeccionAdminNoEncontradaError()
    return actualizar_seccion_admin(seccion.pk, datos)


def eliminar_seccion_formulario_admin(
    formulario_id: int,
    codigo_seccion: str,
) -> SeccionFormulario:
    """Elimina una seccion identificada por codigo."""
    seccion = obtener_seccion_por_codigo_en_formulario(formulario_id, codigo_seccion)
    if seccion is None:
        raise SeccionAdminNoEncontradaError()
    return eliminar_seccion_admin(seccion.pk)


def reordenar_secciones_formulario_admin(
    formulario_id: int,
    codigos: list[str],
) -> None:
    """Reordena secciones a partir de codigos en el orden indicado."""
    items = _items_reordenamiento_por_codigos(
        formulario_id,
        codigos,
        obtener_seccion_por_codigo_en_formulario,
        SeccionAdminNoEncontradaError,
    )
    reordenar_secciones_admin(items)


def crear_pregunta_formulario_admin(
    formulario_id: int,
    datos: dict[str, Any],
) -> Pregunta:
    """Crea una pregunta en la seccion indicada por codigo."""
    seccion_id, datos_servicio = _preparar_datos_pregunta_frontend(formulario_id, datos)
    return crear_pregunta_admin(seccion_id, datos_servicio)


def actualizar_pregunta_formulario_admin(
    formulario_id: int,
    codigo_pregunta: str,
    datos: dict[str, Any],
) -> Pregunta:
    """Actualiza una pregunta identificada por codigo."""
    pregunta = obtener_pregunta_por_codigo_en_formulario(formulario_id, codigo_pregunta)
    if pregunta is None:
        raise PreguntaAdminNoEncontradaError()
    _, datos_servicio = _preparar_datos_pregunta_frontend(formulario_id, datos)
    return actualizar_pregunta_admin(pregunta.pk, datos_servicio)


def eliminar_pregunta_formulario_admin(
    formulario_id: int,
    codigo_pregunta: str,
) -> Pregunta:
    """Elimina una pregunta identificada por codigo."""
    pregunta = obtener_pregunta_por_codigo_en_formulario(formulario_id, codigo_pregunta)
    if pregunta is None:
        raise PreguntaAdminNoEncontradaError()
    return eliminar_pregunta_admin(pregunta.pk)


def duplicar_pregunta_formulario_admin(
    formulario_id: int,
    codigo_pregunta: str,
) -> Pregunta:
    """Duplica una pregunta identificada por codigo."""
    pregunta = obtener_pregunta_por_codigo_en_formulario(formulario_id, codigo_pregunta)
    if pregunta is None:
        raise PreguntaAdminNoEncontradaError()
    return duplicar_pregunta_admin(pregunta.pk)


def reordenar_preguntas_formulario_admin(
    formulario_id: int,
    codigos: list[str],
) -> None:
    """Reordena preguntas a partir de codigos en el orden indicado."""
    items = _items_reordenamiento_por_codigos(
        formulario_id,
        codigos,
        obtener_pregunta_por_codigo_en_formulario,
        PreguntaAdminNoEncontradaError,
    )
    reordenar_preguntas_admin(items)


def crear_opcion_formulario_admin(
    formulario_id: int,
    codigo_pregunta: str,
    datos: dict[str, Any],
) -> OpcionRespuesta:
    """Crea una opcion en la pregunta indicada por codigo."""
    pregunta = obtener_pregunta_por_codigo_en_formulario(formulario_id, codigo_pregunta)
    if pregunta is None:
        raise PreguntaAdminNoEncontradaError()
    return crear_opcion_admin(pregunta.pk, datos)


def actualizar_opcion_formulario_admin(
    formulario_id: int,
    codigo_opcion: str,
    datos: dict[str, Any],
) -> OpcionRespuesta:
    """Actualiza una opcion identificada por codigo."""
    opcion = obtener_opcion_por_codigo_en_formulario(formulario_id, codigo_opcion)
    if opcion is None:
        raise OpcionAdminNoEncontradaError()
    return actualizar_opcion_admin(opcion.pk, datos)


def eliminar_opcion_formulario_admin(
    formulario_id: int,
    codigo_opcion: str,
) -> OpcionRespuesta:
    """Elimina una opcion identificada por codigo."""
    opcion = obtener_opcion_por_codigo_en_formulario(formulario_id, codigo_opcion)
    if opcion is None:
        raise OpcionAdminNoEncontradaError()
    return eliminar_opcion_admin(opcion.pk)


def reordenar_opciones_formulario_admin(
    formulario_id: int,
    codigo_pregunta: str,
    codigos: list[str],
) -> None:
    """Reordena opciones de una pregunta a partir de codigos."""
    pregunta = obtener_pregunta_por_codigo_en_formulario(formulario_id, codigo_pregunta)
    if pregunta is None:
        raise PreguntaAdminNoEncontradaError()

    items: list[dict[str, int]] = []
    for orden, codigo in enumerate(codigos, start=1):
        opcion = OpcionRespuesta.objects.filter(
            pregunta_id=pregunta.pk,
            codigo=codigo,
            esta_eliminado=False,
        ).first()
        if opcion is None:
            raise OpcionAdminNoEncontradaError()
        items.append({"id": opcion.pk, "orden": orden})
    reordenar_opciones_admin(items)


def listar_reglas_formulario_admin_serializadas(
    formulario_id: int,
) -> list[dict[str, Any]]:
    """Lista reglas del formulario en formato del panel."""
    return [
        serializar_regla_frontend(regla)
        for regla in listar_reglas_formulario_admin(formulario_id)
    ]


def crear_regla_formulario_admin(
    formulario_id: int,
    datos: dict[str, Any],
) -> ReglaPregunta:
    """Crea una regla a partir de codigos de origen y destino."""
    origen = _resolver_pregunta_objeto(formulario_id, datos.get("pregunta_origen"))
    if origen is None:
        raise PreguntaAdminNoEncontradaError()
    datos_servicio = _preparar_datos_regla_frontend(formulario_id, datos)
    return crear_regla_admin(origen.pk, datos_servicio)


def actualizar_regla_formulario_admin(
    formulario_id: int,
    regla_id: int,
    datos: dict[str, Any],
) -> ReglaPregunta:
    """Actualiza una regla del formulario."""
    regla = obtener_regla_en_formulario(formulario_id, regla_id)
    if regla is None:
        raise ReglaAdminNoEncontradaError()

    datos_servicio: dict[str, Any] = {}
    for campo in ("operador", "valor_esperado", "accion", "mensaje", "esta_activa"):
        if campo in datos:
            datos_servicio[campo] = datos[campo]
    if "pregunta_destino" in datos:
        datos_servicio["pregunta_destino"] = _resolver_pregunta_objeto(
            formulario_id,
            datos.get("pregunta_destino"),
        )
    if "seccion_destino" in datos:
        datos_servicio["seccion_destino"] = _resolver_seccion_objeto(
            formulario_id,
            datos.get("seccion_destino"),
        )
    return actualizar_regla_admin(regla_id, datos_servicio)


def eliminar_regla_formulario_admin(
    formulario_id: int,
    regla_id: int,
) -> ReglaPregunta:
    """Elimina una regla del formulario."""
    regla = obtener_regla_en_formulario(formulario_id, regla_id)
    if regla is None:
        raise ReglaAdminNoEncontradaError()
    return eliminar_regla_admin(regla_id)


@transaction.atomic
def actualizar_textos_formulario_admin(
    formulario_id: int,
    textos: list[dict[str, Any]],
) -> list[TextoFormulario]:
    """Actualiza o crea textos por tipo en la version administrativa."""
    version = _obtener_version_edicion_o_error(formulario_id)
    resultados: list[TextoFormulario] = []
    for indice, entrada in enumerate(textos, start=1):
        existente = TextoFormulario.objects.filter(
            formulario_version_id=version.pk,
            tipo=entrada["tipo"],
            esta_eliminado=False,
        ).first()
        if existente is not None:
            resultados.append(
                actualizar_texto_admin(
                    existente.pk,
                    {
                        "contenido": entrada.get("contenido", ""),
                        "titulo": entrada.get("titulo", existente.titulo),
                    },
                ),
            )
            continue
        validar_version_editable(version)
        resultados.append(
            TextoFormulario.objects.create(
                formulario_version=version,
                tipo=entrada["tipo"],
                titulo=entrada.get("titulo", ""),
                contenido=entrada.get("contenido", ""),
                orden=indice,
            ),
        )
    return resultados


def publicar_formulario_admin(formulario_id: int) -> Formulario:
    """Publica la version borrador editable del formulario."""
    _obtener_formulario_admin_o_error(formulario_id)
    version = obtener_version_borrador_editable(formulario_id)
    if version is None:
        version = (
            FormularioVersion.objects.filter(
                formulario_id=formulario_id,
                es_publicada=False,
            )
            .order_by("-numero_version")
            .first()
        )
    if version is None:
        raise ValidacionFormularioAdminError(
            MensajesFormularioAdmin.SIN_VERSION_PARA_PUBLICAR,
        )
    publicar_version_admin(formulario_id, version.pk)
    formulario = obtener_formulario_admin_por_id(formulario_id)
    if formulario is None:
        raise FormularioAdminNoEncontradoError()
    return formulario


def cerrar_formulario_admin(formulario_id: int) -> Formulario:
    """Cierra la version publicada mas reciente del formulario."""
    _obtener_formulario_admin_o_error(formulario_id)
    version = (
        FormularioVersion.objects.filter(
            formulario_id=formulario_id,
            es_publicada=True,
        )
        .order_by("-numero_version")
        .first()
    )
    if version is None:
        raise VersionAdminNoEncontradaError()
    cerrar_version_admin(formulario_id, version.pk)
    formulario = obtener_formulario_admin_por_id(formulario_id)
    if formulario is None:
        raise FormularioAdminNoEncontradoError()
    return formulario


def _obtener_formulario_admin_o_error(formulario_id: int) -> Formulario:
    """Retorna el formulario o lanza error funcional."""
    formulario = obtener_formulario_admin_por_id(formulario_id)
    if formulario is None:
        raise FormularioAdminNoEncontradoError()
    return formulario
