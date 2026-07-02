"""
Servicios de negocio de la API administrativa de formularios.
"""

from copy import deepcopy
from typing import Any

from django.db import transaction
from django.utils import timezone

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import crear_snapshot_modelo, registrar_auditoria
from aplicaciones.formularios.excepciones_admin import (
    FormularioAdminNoEncontradoError,
    OpcionAdminNoEncontradaError,
    PreguntaAdminNoEncontradaError,
    ReglaAdminNoEncontradaError,
    SeccionAdminNoEncontradaError,
    TextoAdminNoEncontradoError,
    ValidacionFormularioAdminError,
    VersionAdminNoEncontradaError,
)
from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    OpcionRespuesta,
    Pregunta,
    ReglaPregunta,
    SeccionFormulario,
    TextoFormulario,
)
from aplicaciones.formularios.selectores_admin import (
    listar_formularios_admin,
    listar_opciones_pregunta,
    listar_preguntas_seccion,
    listar_reglas_pregunta,
    listar_secciones_version,
    listar_textos_formulario,
    listar_versiones_formulario,
    obtener_formulario_admin_por_id,
    obtener_opcion_admin_por_id,
    obtener_pregunta_admin_por_id,
    obtener_regla_admin_por_id,
    obtener_seccion_admin_por_id,
    obtener_texto_admin_por_id,
    obtener_version_admin_por_id,
    obtener_version_borrador_editable,
)
from aplicaciones.formularios.validadores_admin import (
    validar_codigo_formulario_unico,
    validar_codigo_pregunta_unico,
    validar_codigo_seccion_unico,
    validar_pregunta_catalogo,
    validar_publicacion_version,
    validar_regla_destino,
    validar_version_editable,
)
from aplicaciones.formularios.validadores_tooltip import (
    validar_y_normalizar_tooltip_admin,
)

_CAMPOS_FORMULARIO = (
    "codigo",
    "nombre",
    "descripcion",
    "introduccion",
    "objetivo",
    "tipo_formulario",
    "tiempo_estimado_minutos",
    "estado",
    "permite_anonimo",
    "permite_registro_final",
    "permite_multiples_respuestas",
    "permite_offline",
    "fecha_inicio",
    "fecha_fin",
    "orden",
)


def _registrar_auditoria_entidad(
    instancia: Any,
    accion: str,
    valor_anterior: dict | None = None,
    valor_nuevo: dict | None = None,
    descripcion: str = "",
) -> None:
    """Registra auditoria sobre una entidad del motor de formularios."""
    registrar_auditoria(
        entidad=instancia.__class__.__name__,
        entidad_id=str(instancia.pk),
        accion=accion,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        descripcion=descripcion,
    )


def _aplicar_campos(instancia: Any, datos: dict, campos: tuple[str, ...]) -> list[str]:
    """Aplica campos permitidos sobre una instancia de modelo."""
    actualizados: list[str] = []
    for campo in campos:
        if campo in datos:
            setattr(instancia, campo, datos[campo])
            actualizados.append(campo)
    return actualizados


def _preparar_tooltip_en_datos(
    datos: dict,
    instancia: Pregunta | OpcionRespuesta | None = None,
) -> dict:
    """Normaliza y valida la configuracion de tooltip antes de persistir."""
    tiene_tooltip = datos.get("tiene_tooltip")
    tooltip = datos.get("tooltip")
    if tiene_tooltip is None:
        tiene_tooltip = instancia.tiene_tooltip if instancia is not None else False
    if tooltip is None:
        tooltip = instancia.tooltip if instancia is not None else ""
    tiene_tooltip, tooltip = validar_y_normalizar_tooltip_admin(tiene_tooltip, tooltip)
    datos["tiene_tooltip"] = tiene_tooltip
    datos["tooltip"] = tooltip
    return datos


def _obtener_formulario_o_error(formulario_id: int) -> Formulario:
    """Obtiene formulario o lanza excepcion funcional."""
    formulario = obtener_formulario_admin_por_id(formulario_id)
    if formulario is None:
        raise FormularioAdminNoEncontradoError()
    return formulario


def _obtener_version_o_error(version_id: int) -> FormularioVersion:
    """Obtiene version o lanza excepcion funcional."""
    version = obtener_version_admin_por_id(version_id)
    if version is None:
        raise VersionAdminNoEncontradaError()
    return version


def _obtener_seccion_o_error(seccion_id: int) -> SeccionFormulario:
    """Obtiene seccion o lanza excepcion funcional."""
    seccion = obtener_seccion_admin_por_id(seccion_id)
    if seccion is None:
        raise SeccionAdminNoEncontradaError()
    return seccion


def _obtener_pregunta_o_error(pregunta_id: int) -> Pregunta:
    """Obtiene pregunta o lanza excepcion funcional."""
    pregunta = obtener_pregunta_admin_por_id(pregunta_id)
    if pregunta is None:
        raise PreguntaAdminNoEncontradaError()
    return pregunta


def listar_formularios() -> list[Formulario]:
    """Lista formularios para administracion."""
    return list(listar_formularios_admin())


@transaction.atomic
def crear_formulario_admin(datos: dict) -> Formulario:
    """Crea un formulario nuevo en estado borrador."""
    validar_codigo_formulario_unico(datos["codigo"])
    formulario = Formulario.objects.create(**{
        campo: datos[campo]
        for campo in _CAMPOS_FORMULARIO
        if campo in datos
    })
    FormularioVersion.objects.create(
        formulario=formulario,
        numero_version=1,
        estado=EstadoFormulario.BORRADOR,
    )
    formulario.version_actual = 1
    formulario.save(update_fields=["version_actual"])
    _registrar_auditoria_entidad(
        formulario,
        AccionAuditoria.CREAR,
        valor_nuevo=crear_snapshot_modelo(formulario),
        descripcion="Creacion de formulario desde administracion.",
    )
    return formulario


@transaction.atomic
def actualizar_formulario_admin(formulario_id: int, datos: dict) -> Formulario:
    """Actualiza campos de un formulario existente."""
    formulario = _obtener_formulario_o_error(formulario_id)
    if "codigo" in datos:
        validar_codigo_formulario_unico(datos["codigo"], formulario.pk)
    valor_anterior = crear_snapshot_modelo(formulario)
    campos = _aplicar_campos(formulario, datos, _CAMPOS_FORMULARIO)
    if campos:
        formulario.save(update_fields=[*campos, "fecha_modificacion"])
        _registrar_auditoria_entidad(
            formulario,
            AccionAuditoria.EDITAR,
            valor_anterior=valor_anterior,
            valor_nuevo=crear_snapshot_modelo(formulario),
            descripcion="Actualizacion de formulario desde administracion.",
        )
    return formulario


@transaction.atomic
def eliminar_formulario_admin(formulario_id: int) -> Formulario:
    """Elimina logicamente un formulario."""
    formulario = _obtener_formulario_o_error(formulario_id)
    formulario.eliminar_logicamente()
    return formulario


def listar_versiones_admin(formulario_id: int) -> list[FormularioVersion]:
    """Lista versiones de un formulario."""
    _obtener_formulario_o_error(formulario_id)
    return list(listar_versiones_formulario(formulario_id))


@transaction.atomic
def crear_version_admin(formulario_id: int, datos: dict | None = None) -> FormularioVersion:
    """Crea una nueva version borrador incrementando el numero de version."""
    formulario = _obtener_formulario_o_error(formulario_id)
    ultima = formulario.versiones.order_by("-numero_version").first()
    numero = (ultima.numero_version + 1) if ultima else 1
    version = FormularioVersion.objects.create(
        formulario=formulario,
        numero_version=numero,
        estado=EstadoFormulario.BORRADOR,
        descripcion_cambio=(datos or {}).get("descripcion_cambio", ""),
    )
    formulario.version_actual = numero
    formulario.save(update_fields=["version_actual"])
    _registrar_auditoria_entidad(
        version,
        AccionAuditoria.VERSIONAR,
        valor_nuevo=crear_snapshot_modelo(version),
        descripcion="Creacion de nueva version de formulario.",
    )
    return version


@transaction.atomic
def publicar_version_admin(formulario_id: int, version_id: int) -> FormularioVersion:
    """Publica una version tras validar estructura minima."""
    _obtener_formulario_o_error(formulario_id)
    version = _obtener_version_o_error(version_id)
    if version.formulario_id != formulario_id:
        raise VersionAdminNoEncontradaError()
    validar_publicacion_version(version)
    valor_anterior = crear_snapshot_modelo(version)
    version.estado = EstadoFormulario.PUBLICADO
    version.es_publicada = True
    version.fecha_publicacion = timezone.now()
    version.save(
        update_fields=[
            "estado",
            "es_publicada",
            "fecha_publicacion",
            "fecha_modificacion",
        ],
    )
    formulario = version.formulario
    formulario.estado = EstadoFormulario.PUBLICADO
    formulario.save(update_fields=["estado", "fecha_modificacion"])
    _registrar_auditoria_entidad(
        version,
        AccionAuditoria.PUBLICAR,
        valor_anterior=valor_anterior,
        valor_nuevo=crear_snapshot_modelo(version),
        descripcion="Publicacion de version de formulario.",
    )
    return version


@transaction.atomic
def cerrar_version_admin(formulario_id: int, version_id: int) -> FormularioVersion:
    """Cierra una version publicada."""
    _obtener_formulario_o_error(formulario_id)
    version = _obtener_version_o_error(version_id)
    if version.formulario_id != formulario_id:
        raise VersionAdminNoEncontradaError()
    valor_anterior = crear_snapshot_modelo(version)
    version.estado = EstadoFormulario.CERRADO
    version.save(update_fields=["estado", "fecha_modificacion"])
    _registrar_auditoria_entidad(
        version,
        AccionAuditoria.CERRAR,
        valor_anterior=valor_anterior,
        valor_nuevo=crear_snapshot_modelo(version),
        descripcion="Cierre de version de formulario.",
    )
    return version


def listar_secciones_admin(version_id: int) -> list[SeccionFormulario]:
    """Lista secciones de una version."""
    _obtener_version_o_error(version_id)
    return list(listar_secciones_version(version_id))


@transaction.atomic
def crear_seccion_admin(version_id: int, datos: dict) -> SeccionFormulario:
    """Crea una seccion en una version borrador."""
    version = _obtener_version_o_error(version_id)
    validar_version_editable(version)
    validar_codigo_seccion_unico(version_id, datos["codigo"])
    seccion = SeccionFormulario.objects.create(
        formulario_version=version,
        codigo=datos["codigo"],
        titulo=datos["titulo"],
        descripcion=datos.get("descripcion", ""),
        texto_ayuda=datos.get("texto_ayuda", ""),
        orden=datos["orden"],
        es_visible=datos.get("es_visible", True),
        esta_activo=datos.get("esta_activo", True),
    )
    _registrar_auditoria_entidad(
        seccion,
        AccionAuditoria.CREAR,
        valor_nuevo=crear_snapshot_modelo(seccion),
        descripcion="Creacion de seccion desde administracion.",
    )
    return seccion


@transaction.atomic
def actualizar_seccion_admin(seccion_id: int, datos: dict) -> SeccionFormulario:
    """Actualiza una seccion existente."""
    seccion = _obtener_seccion_o_error(seccion_id)
    validar_version_editable(seccion.formulario_version)
    if "codigo" in datos:
        validar_codigo_seccion_unico(
            seccion.formulario_version_id,
            datos["codigo"],
            seccion.pk,
        )
    valor_anterior = crear_snapshot_modelo(seccion)
    campos = _aplicar_campos(
        seccion,
        datos,
        ("codigo", "titulo", "descripcion", "texto_ayuda", "orden", "es_visible", "esta_activo"),
    )
    if campos:
        seccion.save(update_fields=[*campos, "fecha_modificacion"])
        _registrar_auditoria_entidad(
            seccion,
            AccionAuditoria.EDITAR,
            valor_anterior=valor_anterior,
            valor_nuevo=crear_snapshot_modelo(seccion),
            descripcion="Actualizacion de seccion desde administracion.",
        )
    return seccion


@transaction.atomic
def eliminar_seccion_admin(seccion_id: int) -> SeccionFormulario:
    """Elimina logicamente una seccion."""
    seccion = _obtener_seccion_o_error(seccion_id)
    validar_version_editable(seccion.formulario_version)
    seccion.eliminar_logicamente()
    return seccion


def listar_preguntas_admin(seccion_id: int) -> list[Pregunta]:
    """Lista preguntas de una seccion."""
    _obtener_seccion_o_error(seccion_id)
    return list(listar_preguntas_seccion(seccion_id))


@transaction.atomic
def crear_pregunta_admin(seccion_id: int, datos: dict) -> Pregunta:
    """Crea una pregunta en una seccion."""
    seccion = _obtener_seccion_o_error(seccion_id)
    validar_version_editable(seccion.formulario_version)
    validar_codigo_pregunta_unico(seccion_id, datos["codigo"])
    datos = _preparar_tooltip_en_datos(dict(datos))
    pregunta = Pregunta.objects.create(
        seccion=seccion,
        codigo=datos["codigo"],
        texto=datos["texto"],
        descripcion=datos.get("descripcion", ""),
        tooltip=datos.get("tooltip", ""),
        tiene_tooltip=datos.get("tiene_tooltip", False),
        tipo_pregunta=datos["tipo_pregunta"],
        es_obligatoria=datos.get("es_obligatoria", False),
        es_pregunta_filtro=datos.get("es_pregunta_filtro", False),
        tipo_validacion_filtro=datos.get("tipo_validacion_filtro", ""),
        valor_filtro_esperado=datos.get("valor_filtro_esperado"),
        bloquea_continuacion_si_no_cumple=datos.get(
            "bloquea_continuacion_si_no_cumple",
            True,
        ),
        mensaje_no_cumple=datos.get("mensaje_no_cumple", ""),
        permite_otro=datos.get("permite_otro", False),
        permite_observacion=datos.get("permite_observacion", False),
        orden=datos["orden"],
        longitud_minima=datos.get("longitud_minima"),
        longitud_maxima=datos.get("longitud_maxima"),
        valor_minimo=datos.get("valor_minimo"),
        valor_maximo=datos.get("valor_maximo"),
        expresion_regular=datos.get("expresion_regular", ""),
        mensaje_error=datos.get("mensaje_error", ""),
        esta_activa=datos.get("esta_activa", True),
        usa_catalogo=datos.get("usa_catalogo", False),
        catalogo_asociado_id=datos.get("catalogo_asociado"),
        pregunta_padre_catalogo_id=datos.get("pregunta_padre_catalogo"),
        campo_codigo_padre_catalogo=datos.get("campo_codigo_padre_catalogo", "codigo"),
        permite_busqueda_catalogo=datos.get("permite_busqueda_catalogo", False),
        limite_items_catalogo=datos.get("limite_items_catalogo"),
    )
    validar_pregunta_catalogo(pregunta)
    _registrar_auditoria_entidad(
        pregunta,
        AccionAuditoria.CREAR,
        valor_nuevo=crear_snapshot_modelo(pregunta),
        descripcion="Creacion de pregunta desde administracion.",
    )
    return pregunta


@transaction.atomic
def actualizar_pregunta_admin(pregunta_id: int, datos: dict) -> Pregunta:
    """Actualiza una pregunta existente."""
    pregunta = _obtener_pregunta_o_error(pregunta_id)
    validar_version_editable(pregunta.seccion.formulario_version)
    if "codigo" in datos:
        validar_codigo_pregunta_unico(
            pregunta.seccion_id,
            datos["codigo"],
            pregunta.pk,
        )
    valor_anterior = crear_snapshot_modelo(pregunta)
    if "tiene_tooltip" in datos or "tooltip" in datos:
        datos = _preparar_tooltip_en_datos(dict(datos), instancia=pregunta)
    campos = _aplicar_campos(
        pregunta,
        datos,
        (
            "codigo",
            "texto",
            "descripcion",
            "tooltip",
            "tiene_tooltip",
            "tipo_pregunta",
            "es_obligatoria",
            "es_pregunta_filtro",
            "tipo_validacion_filtro",
            "valor_filtro_esperado",
            "bloquea_continuacion_si_no_cumple",
            "mensaje_no_cumple",
            "permite_otro",
            "permite_observacion",
            "orden",
            "longitud_minima",
            "longitud_maxima",
            "valor_minimo",
            "valor_maximo",
            "expresion_regular",
            "mensaje_error",
            "esta_activa",
            "usa_catalogo",
            "catalogo_asociado",
            "pregunta_padre_catalogo",
            "campo_codigo_padre_catalogo",
            "permite_busqueda_catalogo",
            "limite_items_catalogo",
        ),
    )
    if campos:
        pregunta.save(update_fields=[*campos, "fecha_modificacion"])
        validar_pregunta_catalogo(pregunta)
        _registrar_auditoria_entidad(
            pregunta,
            AccionAuditoria.EDITAR,
            valor_anterior=valor_anterior,
            valor_nuevo=crear_snapshot_modelo(pregunta),
            descripcion="Actualizacion de pregunta desde administracion.",
        )
    return pregunta


@transaction.atomic
def eliminar_pregunta_admin(pregunta_id: int) -> Pregunta:
    """Elimina logicamente una pregunta."""
    pregunta = _obtener_pregunta_o_error(pregunta_id)
    validar_version_editable(pregunta.seccion.formulario_version)
    pregunta.eliminar_logicamente()
    return pregunta


@transaction.atomic
def duplicar_pregunta_admin(pregunta_id: int) -> Pregunta:
    """Duplica una pregunta con nuevo codigo en la misma seccion."""
    original = _obtener_pregunta_o_error(pregunta_id)
    validar_version_editable(original.seccion.formulario_version)
    nuevo_codigo = f"{original.codigo}_copia"
    contador = 1
    while codigo_pregunta_duplicado_existe(original.seccion_id, nuevo_codigo):
        contador += 1
        nuevo_codigo = f"{original.codigo}_copia_{contador}"
    datos = crear_snapshot_modelo(original)
    datos.pop("id", None)
    datos.pop("fecha_creacion", None)
    datos.pop("fecha_modificacion", None)
    copia = Pregunta.objects.create(
        seccion=original.seccion,
        codigo=nuevo_codigo,
        texto=original.texto,
        descripcion=original.descripcion,
        tooltip=original.tooltip,
        tiene_tooltip=original.tiene_tooltip,
        tipo_pregunta=original.tipo_pregunta,
        es_obligatoria=original.es_obligatoria,
        es_pregunta_filtro=original.es_pregunta_filtro,
        tipo_validacion_filtro=original.tipo_validacion_filtro,
        valor_filtro_esperado=original.valor_filtro_esperado,
        bloquea_continuacion_si_no_cumple=original.bloquea_continuacion_si_no_cumple,
        mensaje_no_cumple=original.mensaje_no_cumple,
        permite_otro=original.permite_otro,
        permite_observacion=original.permite_observacion,
        orden=original.orden + 1,
        longitud_minima=original.longitud_minima,
        longitud_maxima=original.longitud_maxima,
        valor_minimo=original.valor_minimo,
        valor_maximo=original.valor_maximo,
        expresion_regular=original.expresion_regular,
        mensaje_error=original.mensaje_error,
        esta_activa=original.esta_activa,
        usa_catalogo=original.usa_catalogo,
        catalogo_asociado=original.catalogo_asociado,
        pregunta_padre_catalogo=original.pregunta_padre_catalogo,
        campo_codigo_padre_catalogo=original.campo_codigo_padre_catalogo,
        permite_busqueda_catalogo=original.permite_busqueda_catalogo,
        limite_items_catalogo=original.limite_items_catalogo,
    )
    for opcion in original.opciones.filter(esta_eliminado=False):
        OpcionRespuesta.objects.create(
            pregunta=copia,
            codigo=opcion.codigo,
            etiqueta=opcion.etiqueta,
            valor=opcion.valor,
            tooltip=opcion.tooltip,
            tiene_tooltip=opcion.tiene_tooltip,
            orden=opcion.orden,
            es_excluyente=opcion.es_excluyente,
            activa_otro=opcion.activa_otro,
            esta_activa=opcion.esta_activa,
        )
    _registrar_auditoria_entidad(
        copia,
        AccionAuditoria.CREAR,
        valor_nuevo=crear_snapshot_modelo(copia),
        descripcion="Duplicacion de pregunta desde administracion.",
    )
    return copia


def codigo_pregunta_duplicado_existe(seccion_id: int, codigo: str) -> bool:
    """Indica si ya existe una pregunta con el codigo en la seccion."""
    from aplicaciones.formularios.selectores_admin import codigo_pregunta_activo_duplicado

    return codigo_pregunta_activo_duplicado(seccion_id, codigo)


@transaction.atomic
def reordenar_preguntas_admin(items: list[dict]) -> None:
    """Actualiza el orden de multiples preguntas."""
    for item in items:
        pregunta = _obtener_pregunta_o_error(item["id"])
        validar_version_editable(pregunta.seccion.formulario_version)
        valor_anterior = crear_snapshot_modelo(pregunta)
        pregunta.orden = item["orden"]
        pregunta.save(update_fields=["orden", "fecha_modificacion"])
        _registrar_auditoria_entidad(
            pregunta,
            AccionAuditoria.EDITAR,
            valor_anterior=valor_anterior,
            valor_nuevo=crear_snapshot_modelo(pregunta),
            descripcion="Reordenamiento de preguntas desde administracion.",
        )


@transaction.atomic
def reordenar_secciones_admin(items: list[dict]) -> None:
    """Actualiza el orden de multiples secciones."""
    for item in items:
        seccion = _obtener_seccion_o_error(item["id"])
        validar_version_editable(seccion.formulario_version)
        valor_anterior = crear_snapshot_modelo(seccion)
        seccion.orden = item["orden"]
        seccion.save(update_fields=["orden", "fecha_modificacion"])
        _registrar_auditoria_entidad(
            seccion,
            AccionAuditoria.EDITAR,
            valor_anterior=valor_anterior,
            valor_nuevo=crear_snapshot_modelo(seccion),
            descripcion="Reordenamiento de secciones desde administracion.",
        )


@transaction.atomic
def reordenar_opciones_admin(items: list[dict]) -> None:
    """Actualiza el orden de multiples opciones."""
    for item in items:
        opcion = obtener_opcion_admin_por_id(item["id"])
        if opcion is None:
            raise OpcionAdminNoEncontradaError()
        validar_version_editable(opcion.pregunta.seccion.formulario_version)
        valor_anterior = crear_snapshot_modelo(opcion)
        opcion.orden = item["orden"]
        opcion.save(update_fields=["orden", "fecha_modificacion"])
        _registrar_auditoria_entidad(
            opcion,
            AccionAuditoria.EDITAR,
            valor_anterior=valor_anterior,
            valor_nuevo=crear_snapshot_modelo(opcion),
            descripcion="Reordenamiento de opciones desde administracion.",
        )


def listar_opciones_admin(pregunta_id: int) -> list[OpcionRespuesta]:
    """Lista opciones de una pregunta."""
    _obtener_pregunta_o_error(pregunta_id)
    return list(listar_opciones_pregunta(pregunta_id))


@transaction.atomic
def crear_opcion_admin(pregunta_id: int, datos: dict) -> OpcionRespuesta:
    """Crea una opcion de respuesta."""
    pregunta = _obtener_pregunta_o_error(pregunta_id)
    validar_version_editable(pregunta.seccion.formulario_version)
    datos = _preparar_tooltip_en_datos(dict(datos))
    opcion = OpcionRespuesta.objects.create(
        pregunta=pregunta,
        codigo=datos["codigo"],
        etiqueta=datos["etiqueta"],
        valor=datos["valor"],
        tooltip=datos.get("tooltip", ""),
        tiene_tooltip=datos.get("tiene_tooltip", False),
        orden=datos["orden"],
        es_excluyente=datos.get("es_excluyente", False),
        activa_otro=datos.get("activa_otro", False),
        esta_activa=datos.get("esta_activa", True),
    )
    _registrar_auditoria_entidad(
        opcion,
        AccionAuditoria.CREAR,
        valor_nuevo=crear_snapshot_modelo(opcion),
        descripcion="Creacion de opcion desde administracion.",
    )
    return opcion


@transaction.atomic
def actualizar_opcion_admin(opcion_id: int, datos: dict) -> OpcionRespuesta:
    """Actualiza una opcion existente."""
    opcion = obtener_opcion_admin_por_id(opcion_id)
    if opcion is None:
        raise OpcionAdminNoEncontradaError()
    validar_version_editable(opcion.pregunta.seccion.formulario_version)
    valor_anterior = crear_snapshot_modelo(opcion)
    if "tiene_tooltip" in datos or "tooltip" in datos:
        datos = _preparar_tooltip_en_datos(dict(datos), instancia=opcion)
    campos = _aplicar_campos(
        opcion,
        datos,
        (
            "codigo",
            "etiqueta",
            "valor",
            "tooltip",
            "tiene_tooltip",
            "orden",
            "es_excluyente",
            "activa_otro",
            "esta_activa",
        ),
    )
    if campos:
        opcion.save(update_fields=[*campos, "fecha_modificacion"])
        _registrar_auditoria_entidad(
            opcion,
            AccionAuditoria.EDITAR,
            valor_anterior=valor_anterior,
            valor_nuevo=crear_snapshot_modelo(opcion),
            descripcion="Actualizacion de opcion desde administracion.",
        )
    return opcion


@transaction.atomic
def eliminar_opcion_admin(opcion_id: int) -> OpcionRespuesta:
    """Elimina logicamente una opcion."""
    opcion = obtener_opcion_admin_por_id(opcion_id)
    if opcion is None:
        raise OpcionAdminNoEncontradaError()
    validar_version_editable(opcion.pregunta.seccion.formulario_version)
    opcion.eliminar_logicamente()
    return opcion


def listar_textos_admin(formulario_id: int) -> list[TextoFormulario]:
    """Lista textos de un formulario."""
    _obtener_formulario_o_error(formulario_id)
    return list(listar_textos_formulario(formulario_id))


@transaction.atomic
def crear_texto_admin(formulario_id: int, datos: dict) -> TextoFormulario:
    """Crea un texto en la version borrador editable del formulario."""
    _obtener_formulario_o_error(formulario_id)
    version = obtener_version_borrador_editable(formulario_id)
    if version is None:
        raise ValidacionFormularioAdminError(
            "No existe una version borrador editable para agregar textos.",
        )
    validar_version_editable(version)
    texto = TextoFormulario.objects.create(
        formulario_version=version,
        tipo=datos["tipo"],
        titulo=datos.get("titulo", ""),
        contenido=datos["contenido"],
        orden=datos.get("orden", 1),
        esta_activo=datos.get("esta_activo", True),
    )
    _registrar_auditoria_entidad(
        texto,
        AccionAuditoria.CREAR,
        valor_nuevo=crear_snapshot_modelo(texto),
        descripcion="Creacion de texto desde administracion.",
    )
    return texto


@transaction.atomic
def actualizar_texto_admin(texto_id: int, datos: dict) -> TextoFormulario:
    """Actualiza un texto existente."""
    texto = obtener_texto_admin_por_id(texto_id)
    if texto is None:
        raise TextoAdminNoEncontradoError()
    validar_version_editable(texto.formulario_version)
    valor_anterior = crear_snapshot_modelo(texto)
    campos = _aplicar_campos(
        texto,
        datos,
        ("tipo", "titulo", "contenido", "orden", "esta_activo"),
    )
    if campos:
        texto.save(update_fields=[*campos, "fecha_modificacion"])
        _registrar_auditoria_entidad(
            texto,
            AccionAuditoria.EDITAR,
            valor_anterior=valor_anterior,
            valor_nuevo=crear_snapshot_modelo(texto),
            descripcion="Actualizacion de texto desde administracion.",
        )
    return texto


@transaction.atomic
def eliminar_texto_admin(texto_id: int) -> TextoFormulario:
    """Elimina logicamente un texto."""
    texto = obtener_texto_admin_por_id(texto_id)
    if texto is None:
        raise TextoAdminNoEncontradoError()
    validar_version_editable(texto.formulario_version)
    texto.eliminar_logicamente()
    return texto


def listar_reglas_admin(pregunta_id: int) -> list[ReglaPregunta]:
    """Lista reglas de una pregunta origen."""
    _obtener_pregunta_o_error(pregunta_id)
    return list(listar_reglas_pregunta(pregunta_id))


@transaction.atomic
def crear_regla_admin(pregunta_id: int, datos: dict) -> ReglaPregunta:
    """Crea una regla condicional."""
    pregunta = _obtener_pregunta_o_error(pregunta_id)
    validar_version_editable(pregunta.seccion.formulario_version)
    destino_pregunta = datos.get("pregunta_destino")
    destino_seccion = datos.get("seccion_destino")
    regla = ReglaPregunta.objects.create(
        pregunta_origen=pregunta,
        operador=datos["operador"],
        valor_esperado=datos["valor_esperado"],
        pregunta_destino=destino_pregunta,
        seccion_destino=destino_seccion,
        accion=datos["accion"],
        mensaje=datos.get("mensaje", ""),
        esta_activa=datos.get("esta_activa", True),
    )
    validar_regla_destino(regla)
    _registrar_auditoria_entidad(
        regla,
        AccionAuditoria.CREAR,
        valor_nuevo=crear_snapshot_modelo(regla),
        descripcion="Creacion de regla desde administracion.",
    )
    return regla


@transaction.atomic
def actualizar_regla_admin(regla_id: int, datos: dict) -> ReglaPregunta:
    """Actualiza una regla existente."""
    regla = obtener_regla_admin_por_id(regla_id)
    if regla is None:
        raise ReglaAdminNoEncontradaError()
    validar_version_editable(regla.pregunta_origen.seccion.formulario_version)
    valor_anterior = deepcopy(crear_snapshot_modelo(regla))
    campos = _aplicar_campos(
        regla,
        datos,
        (
            "operador",
            "valor_esperado",
            "pregunta_destino",
            "seccion_destino",
            "accion",
            "mensaje",
            "esta_activa",
        ),
    )
    if campos:
        regla.save(update_fields=[*campos, "fecha_modificacion"])
        validar_regla_destino(regla)
        _registrar_auditoria_entidad(
            regla,
            AccionAuditoria.EDITAR,
            valor_anterior=valor_anterior,
            valor_nuevo=crear_snapshot_modelo(regla),
            descripcion="Actualizacion de regla desde administracion.",
        )
    return regla


@transaction.atomic
def eliminar_regla_admin(regla_id: int) -> ReglaPregunta:
    """Elimina logicamente una regla."""
    regla = obtener_regla_admin_por_id(regla_id)
    if regla is None:
        raise ReglaAdminNoEncontradaError()
    validar_version_editable(regla.pregunta_origen.seccion.formulario_version)
    regla.eliminar_logicamente()
    return regla
