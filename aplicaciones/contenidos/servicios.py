"""
Servicios de negocio para contenidos e interfaz.
"""

from typing import Any

from django.db import transaction

from aplicaciones.contenidos.constantes import (
    ValoresPorDefectoAccesibilidad,
    ValoresPorDefectoInterfaz,
)
from aplicaciones.contenidos.models import ConfiguracionInterfaz, LogoInterfaz
from aplicaciones.comun.utilidades_media import construir_url_absoluta_desde_solicitud
from aplicaciones.contenidos.selectores import (
    obtener_configuracion_interfaz_activa,
    obtener_logos_interfaz_por_configuracion,
    obtener_mapa_logos_interfaz,
)
from aplicaciones.contenidos.servicios_flujo_formulario import (
    construir_flujo_formulario_por_defecto,
)


def activar_configuracion_interfaz(
    configuracion: ConfiguracionInterfaz,
) -> ConfiguracionInterfaz:
    """Activa una configuracion y desactiva las demas en una sola transaccion."""
    with transaction.atomic():
        configuracion.esta_activa = True
        configuracion.save()
        ConfiguracionInterfaz.objects.exclude(pk=configuracion.pk).update(
            esta_activa=False,
        )
    return configuracion


def construir_bloque_accesibilidad(
    configuracion: ConfiguracionInterfaz | None = None,
) -> dict[str, str | bool]:
    """Construye el bloque de banderas de accesibilidad expuesto al frontend."""
    if configuracion is None:
        return {
            "lectura_voz_habilitada": (
                ValoresPorDefectoAccesibilidad.LECTURA_VOZ_HABILITADA
            ),
            "comandos_voz_habilitada": (
                ValoresPorDefectoAccesibilidad.COMANDOS_VOZ_HABILITADA
            ),
            "lengua_senas_habilitada": (
                ValoresPorDefectoAccesibilidad.LENGUA_SENAS_HABILITADA
            ),
            "fuente_dislexia_habilitada": (
                ValoresPorDefectoAccesibilidad.FUENTE_DISLEXIA_HABILITADA
            ),
            "tema_por_defecto": ValoresPorDefectoAccesibilidad.TEMA_POR_DEFECTO,
        }
    return {
        "lectura_voz_habilitada": configuracion.accesibilidad_lectura_voz_habilitada,
        "comandos_voz_habilitada": configuracion.accesibilidad_comandos_voz_habilitada,
        "lengua_senas_habilitada": configuracion.accion_lengua_senas_habilitada,
        "fuente_dislexia_habilitada": (
            configuracion.accesibilidad_fuente_dislexia_habilitada
        ),
        "tema_por_defecto": configuracion.accesibilidad_tema_por_defecto,
    }


def construir_configuracion_por_defecto() -> dict[str, str | bool | None | list | dict]:
    """Construye los valores por defecto de la configuracion de interfaz."""
    return {
        "nombre_aplicativo": ValoresPorDefectoInterfaz.NOMBRE_APLICATIVO,
        "nombre_corto": ValoresPorDefectoInterfaz.NOMBRE_CORTO,
        "descripcion_aplicativo": ValoresPorDefectoInterfaz.DESCRIPCION_APLICATIVO,
        "texto_pie_pagina": ValoresPorDefectoInterfaz.TEXTO_PIE_PAGINA,
        "texto_titulo_seccion_encuestas": (
            ValoresPorDefectoInterfaz.TEXTO_TITULO_SECCION_ENCUESTAS
        ),
        "texto_descripcion_seccion_encuestas": (
            ValoresPorDefectoInterfaz.TEXTO_DESCRIPCION_SECCION_ENCUESTAS
        ),
        "email_soporte": ValoresPorDefectoInterfaz.EMAIL_SOPORTE,
        "texto_terminos_condiciones": ValoresPorDefectoInterfaz.TEXTO_TERMINOS_CONDICIONES,
        "texto_autorizacion_datos": ValoresPorDefectoInterfaz.TEXTO_AUTORIZACION_DATOS,
        "texto_verificacion_exitosa_titulo": (
            ValoresPorDefectoInterfaz.TEXTO_VERIFICACION_EXITOSA_TITULO
        ),
        "texto_verificacion_exitosa_cuerpo": (
            ValoresPorDefectoInterfaz.TEXTO_VERIFICACION_EXITOSA_CUERPO
        ),
        "texto_confirmacion_envio_titulo": (
            ValoresPorDefectoInterfaz.TEXTO_CONFIRMACION_ENVIO_TITULO
        ),
        "texto_confirmacion_envio_subtitulo": (
            ValoresPorDefectoInterfaz.TEXTO_CONFIRMACION_ENVIO_SUBTITULO
        ),
        "meta_titulo_seo": ValoresPorDefectoInterfaz.META_TITULO_SEO,
        "meta_descripcion_seo": ValoresPorDefectoInterfaz.META_DESCRIPCION_SEO,
        "accion_lengua_senas_habilitada": False,
        "url_lengua_senas": ValoresPorDefectoInterfaz.URL_LENGUA_SENAS,
        "texto_lengua_senas": ValoresPorDefectoInterfaz.TEXTO_LENGUA_SENAS,
        "logo_principal": None,
        "logo_secundario": None,
        "logo_institucional": None,
        "favicon": None,
        "logo_principal_alt": "",
        "logo_secundario_alt": "",
        "logo_institucional_alt": "",
        "favicon_alt": "",
        "logos": [],
        "color_primario": ValoresPorDefectoInterfaz.COLOR_PRIMARIO,
        "color_secundario": ValoresPorDefectoInterfaz.COLOR_SECUNDARIO,
        "color_acento": ValoresPorDefectoInterfaz.COLOR_ACENTO,
        "accesibilidad": construir_bloque_accesibilidad(),
        "flujo_formulario": construir_flujo_formulario_por_defecto(),
    }


def obtener_configuracion_interfaz_publica() -> ConfiguracionInterfaz | None:
    """Retorna la configuracion activa para exposicion publica."""
    return obtener_configuracion_interfaz_activa()


def resolver_url_logo_interfaz(
    logo: LogoInterfaz,
    solicitud: Any = None,
) -> str | None:
    """Construye la URL de un logo parametrizado desde imagen o repositorio."""
    if logo.archivo_repositorio_id is not None:
        from aplicaciones.archivos.servicios import construir_url

        return construir_url(logo.archivo_repositorio, solicitud)

    if logo.imagen:
        return construir_url_absoluta_desde_solicitud(logo.imagen.url, solicitud)

    return None


def construir_lista_logos_publica(
    configuracion: ConfiguracionInterfaz,
    solicitud: Any = None,
) -> list[dict[str, str | None]]:
    """Construye la lista parametrizable de logos expuesta al frontend."""
    logos = obtener_logos_interfaz_por_configuracion(configuracion)
    return [
        {
            "codigo": logo.codigo,
            "nombre": logo.nombre,
            "url": resolver_url_logo_interfaz(logo, solicitud),
            "texto_alternativo": logo.texto_alternativo,
        }
        for logo in logos
    ]


def resolver_url_imagen_configuracion_legacy(
    configuracion: ConfiguracionInterfaz,
    campo: str,
    solicitud: Any = None,
) -> str | None:
    """Resuelve la URL de un campo de imagen legacy en ConfiguracionInterfaz."""
    mapeo_repositorio = {
        "logo_principal": "logo_principal_repositorio",
        "logo_secundario": "logo_secundario_repositorio",
        "logo_institucional": "logo_institucional_repositorio",
        "favicon": "favicon_repositorio",
    }
    campo_repositorio = mapeo_repositorio.get(campo)
    if campo_repositorio:
        archivo_repositorio = getattr(configuracion, campo_repositorio, None)
        if archivo_repositorio is not None:
            from aplicaciones.archivos.servicios import construir_url

            return construir_url(archivo_repositorio, solicitud)

    archivo_imagen = getattr(configuracion, campo)
    if not archivo_imagen:
        return None
    return construir_url_absoluta_desde_solicitud(archivo_imagen.url, solicitud)


def resolver_url_imagen_configuracion(
    configuracion: ConfiguracionInterfaz,
    campo: str,
    solicitud: Any = None,
    mapa_logos: dict[str, LogoInterfaz] | None = None,
) -> str | None:
    """Resuelve la URL de una imagen priorizando logos parametrizados."""
    mapa = mapa_logos or obtener_mapa_logos_interfaz(configuracion)
    logo = mapa.get(campo)
    if logo is not None:
        url_logo = resolver_url_logo_interfaz(logo, solicitud)
        if url_logo is not None:
            return url_logo
        return None
    return resolver_url_imagen_configuracion_legacy(configuracion, campo, solicitud)


def resolver_texto_alternativo_logo(
    configuracion: ConfiguracionInterfaz,
    campo: str,
    mapa_logos: dict[str, LogoInterfaz] | None = None,
) -> str:
    """Retorna el texto alternativo parametrizado de un logo."""
    mapa = mapa_logos or obtener_mapa_logos_interfaz(configuracion)
    logo = mapa.get(campo)
    if logo is None:
        return ""
    return logo.texto_alternativo
