"""
Servicio de revision y correccion segura de textos en espanol parametrizables.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from django.db import models

CORRECCIONES_FRASES: tuple[tuple[str, str], ...] = (
    ("inicia sesion", "inicia sesión"),
    ("Inicia sesion", "Inicia sesión"),
    ("cerrar sesion", "cerrar sesión"),
    ("Cerrar sesion", "Cerrar sesión"),
    ("iniciar sesion", "iniciar sesión"),
    ("Iniciar sesion", "Iniciar sesión"),
    ("sesion anonima", "sesión anónima"),
    ("Sesion anonima", "Sesión anónima"),
    (" la sesion ", " la sesión "),
    (" La sesion ", " La sesión "),
    (" de sesion ", " de sesión "),
    (" De sesion ", " De sesión "),
    ("terminos y condiciones", "términos y condiciones"),
    ("Terminos y condiciones", "Términos y condiciones"),
    ("Terminos y Condiciones", "Términos y Condiciones"),
    (
        "Politica de Proteccion de Datos Personales",
        "Política de Protección de Datos Personales",
    ),
)

CORRECCIONES_PALABRAS: tuple[tuple[str, str], ...] = (
    ("registrate", "regístrate"),
    ("Registrate", "Regístrate"),
    ("exito", "éxito"),
    ("Exito", "Éxito"),
    ("aqui", "aquí"),
    ("Aqui", "Aquí"),
    ("aplicacion", "aplicación"),
    ("Aplicacion", "Aplicación"),
    ("informacion", "información"),
    ("Informacion", "Información"),
    ("autorizacion", "autorización"),
    ("Autorizacion", "Autorización"),
    ("contrasena", "contraseña"),
    ("Contrasena", "Contraseña"),
    ("electronico", "electrónico"),
    ("Electronico", "Electrónico"),
    ("configuracion", "configuración"),
    ("Configuracion", "Configuración"),
    ("finalizacion", "finalización"),
    ("Finalizacion", "Finalización"),
    ("proximamente", "próximamente"),
    ("Proximamente", "Próximamente"),
    ("notificacion", "notificación"),
    ("Notificacion", "Notificación"),
    ("analitica", "analítica"),
    ("Analitica", "Analítica"),
    ("sincronizacion", "sincronización"),
    ("Sincronizacion", "Sincronización"),
    ("auditoria", "auditoría"),
    ("Auditoria", "Auditoría"),
)

_LIMITE_PALABRA = r"a-zA-ZáéíóúñüÁÉÍÓÚÑÜ0-9_"

CAMPOS_EXCLUIDOS = frozenset(
    {
        "codigo",
        "slug",
        "tipo",
        "estado",
        "canal",
        "formato",
        "uuid",
        "uuid_sesion",
        "variables_disponibles",
        "variables_utilizadas",
        "respuesta_proveedor",
        "parametros",
        "checksum",
        "token_cliente",
        "user_agent",
        "direccion_ip",
        "zona_horaria",
        "idioma",
        "color_primario",
        "color_secundario",
        "color_acento",
        "terminos_url_ley",
        "terminos_url_politica_datos",
        "url_lengua_senas",
    },
)


@dataclass(frozen=True)
class ConfiguracionTablaTextos:
    """Describe una tabla parametrizable revisable por el comando."""

    etiqueta: str
    modelo: type[models.Model]
    campos: tuple[str, ...]


@dataclass
class CambioTextoPropuesto:
    """Representa una correccion propuesta sobre un registro."""

    tabla: str
    registro_id: int | str
    campo: str
    valor_anterior: str
    valor_nuevo: str


@dataclass
class ReporteRevisionTextos:
    """Resultado agregado de una revision de textos."""

    cambios: list[CambioTextoPropuesto] = field(default_factory=list)
    registros_revisados: int = 0
    tablas_revisadas: list[str] = field(default_factory=list)

    @property
    def total_cambios(self) -> int:
        """Retorna la cantidad de correcciones detectadas o aplicadas."""
        return len(self.cambios)


def _reemplazar_palabra_completa(texto: str, origen: str, destino: str) -> str:
    """Sustituye una palabra solo cuando aparece delimitada como token independiente."""
    patron = re.compile(
        rf"(?<![{_LIMITE_PALABRA}]){re.escape(origen)}(?![{_LIMITE_PALABRA}])",
    )
    return patron.sub(destino, texto)


def aplicar_correcciones_seguras(texto: str) -> str | None:
    """Aplica sustituciones seguras y retorna el texto corregido si hubo cambios."""
    if not texto or not isinstance(texto, str):
        return None

    texto_corregido = texto
    for origen, destino in CORRECCIONES_FRASES:
        if origen in texto_corregido:
            texto_corregido = texto_corregido.replace(origen, destino)

    for origen, destino in CORRECCIONES_PALABRAS:
        texto_corregido = _reemplazar_palabra_completa(texto_corregido, origen, destino)

    if texto_corregido == texto:
        return None
    return texto_corregido


def _obtener_configuraciones_tablas() -> tuple[ConfiguracionTablaTextos, ...]:
    """Construye la lista de tablas parametrizables revisables."""
    from aplicaciones.contenidos.models import (
        ConfiguracionFlujoFormulario,
        ConfiguracionInterfaz,
        LogoInterfaz,
    )
    from aplicaciones.formularios.models import (
        Formulario,
        OpcionRespuesta,
        Pregunta,
        SeccionFormulario,
        TextoFormulario,
    )
    from aplicaciones.internacionalizacion.models import TraduccionContenido
    from aplicaciones.notificaciones.models import PlantillaNotificacion

    return (
        ConfiguracionTablaTextos(
            etiqueta="contenidos_configuracioninterfaz",
            modelo=ConfiguracionInterfaz,
            campos=(
                "nombre_aplicativo",
                "nombre_corto",
                "descripcion_aplicativo",
                "texto_pie_pagina",
                "texto_titulo_seccion_encuestas",
                "texto_descripcion_seccion_encuestas",
                "texto_terminos_condiciones",
                "texto_autorizacion_datos",
                "texto_verificacion_exitosa_titulo",
                "texto_verificacion_exitosa_cuerpo",
                "texto_confirmacion_envio_titulo",
                "texto_confirmacion_envio_subtitulo",
                "meta_titulo_seo",
                "meta_descripcion_seo",
                "texto_lengua_senas",
            ),
        ),
        ConfiguracionTablaTextos(
            etiqueta="contenidos_configuracionflujoformulario",
            modelo=ConfiguracionFlujoFormulario,
            campos=(
                "modal_salir_titulo",
                "modal_salir_p1",
                "modal_salir_p2",
                "modal_salir_btn_volver",
                "modal_salir_btn_salir",
                "modal_salir_link_sesion",
                "modal_sesion_titulo",
                "modal_sesion_parrafo",
                "modal_sesion_btn_login",
                "modal_sesion_btn_registro",
                "modal_sesion_link_cancelar",
                "modal_guardado_titulo",
                "modal_guardado_parrafo",
                "modal_guardado_btn_seguir",
                "modal_guardado_btn_otras",
                "terminos_titulo",
                "terminos_contenido",
                "terminos_p1",
                "terminos_p2",
                "terminos_p3",
                "terminos_boton_aceptar",
                "terminos_boton_cerrar",
                "terminos_enlace",
                "terminos_enlace_ley",
                "terminos_enlace_politica_datos",
            ),
        ),
        ConfiguracionTablaTextos(
            etiqueta="contenidos_logointerfaz",
            modelo=LogoInterfaz,
            campos=("nombre", "texto_alternativo"),
        ),
        ConfiguracionTablaTextos(
            etiqueta="notificaciones_plantillanotificacion",
            modelo=PlantillaNotificacion,
            campos=("nombre", "asunto", "contenido_html", "contenido_texto", "descripcion"),
        ),
        ConfiguracionTablaTextos(
            etiqueta="formularios_formulario",
            modelo=Formulario,
            campos=("nombre", "descripcion"),
        ),
        ConfiguracionTablaTextos(
            etiqueta="formularios_textoformulario",
            modelo=TextoFormulario,
            campos=("contenido",),
        ),
        ConfiguracionTablaTextos(
            etiqueta="formularios_seccionformulario",
            modelo=SeccionFormulario,
            campos=("titulo", "descripcion"),
        ),
        ConfiguracionTablaTextos(
            etiqueta="formularios_pregunta",
            modelo=Pregunta,
            campos=("texto", "descripcion", "tooltip", "mensaje_error"),
        ),
        ConfiguracionTablaTextos(
            etiqueta="formularios_opcionrespuesta",
            modelo=OpcionRespuesta,
            campos=("etiqueta",),
        ),
        ConfiguracionTablaTextos(
            etiqueta="internacionalizacion_traduccioncontenido",
            modelo=TraduccionContenido,
            campos=("valor_traducido", "lectura_facil", "texto_alternativo", "transcripcion"),
        ),
    )


def _filtrar_queryset_activo(modelo: type[models.Model]) -> models.QuerySet:
    """Retorna registros no eliminados logicamente cuando el modelo lo soporta."""
    queryset = modelo.objects.all()
    if hasattr(modelo, "esta_eliminado"):
        return queryset.filter(esta_eliminado=False)
    return queryset


def _revisar_registro(
    configuracion: ConfiguracionTablaTextos,
    fila: dict[str, object],
    aplicar: bool,
    cambios: list[CambioTextoPropuesto],
) -> None:
    """Evalua y opcionalmente corrige los campos textuales de un registro."""
    registro_id = fila["pk"]
    campos_actualizar: dict[str, str] = {}

    for nombre_campo in configuracion.campos:
        if nombre_campo in CAMPOS_EXCLUIDOS:
            continue
        valor = fila.get(nombre_campo)
        if not isinstance(valor, str) or not valor.strip():
            continue
        valor_nuevo = aplicar_correcciones_seguras(valor)
        if valor_nuevo is None:
            continue
        cambios.append(
            CambioTextoPropuesto(
                tabla=configuracion.etiqueta,
                registro_id=registro_id,
                campo=nombre_campo,
                valor_anterior=valor,
                valor_nuevo=valor_nuevo,
            ),
        )
        if aplicar:
            campos_actualizar[nombre_campo] = valor_nuevo

    if aplicar and campos_actualizar:
        configuracion.modelo.objects.filter(pk=registro_id).update(**campos_actualizar)


def ejecutar_revision_textos(aplicar: bool = False) -> ReporteRevisionTextos:
    """Revisa tablas parametrizables y aplica correcciones seguras si corresponde."""
    reporte = ReporteRevisionTextos()

    for configuracion in _obtener_configuraciones_tablas():
        queryset = _filtrar_queryset_activo(configuracion.modelo)
        reporte.tablas_revisadas.append(configuracion.etiqueta)
        campos_consulta = ("pk", *configuracion.campos)

        for fila in queryset.values(*campos_consulta).iterator():
            reporte.registros_revisados += 1
            _revisar_registro(
                configuracion,
                fila,
                aplicar,
                reporte.cambios,
            )

    return reporte


def formatear_reporte_revision(reporte: ReporteRevisionTextos) -> str:
    """Genera un resumen legible del resultado de la revision."""
    lineas = [
        f"Tablas revisadas: {len(reporte.tablas_revisadas)}",
        f"Registros revisados: {reporte.registros_revisados}",
        f"Cambios detectados: {reporte.total_cambios}",
        "",
    ]

    if not reporte.cambios:
        lineas.append("No se encontraron textos para corregir.")
        return "\n".join(lineas)

    for cambio in reporte.cambios:
        lineas.append(
            f"- [{cambio.tabla}#{cambio.registro_id}.{cambio.campo}] "
            f"\"{cambio.valor_anterior}\" -> \"{cambio.valor_nuevo}\"",
        )

    return "\n".join(lineas)
