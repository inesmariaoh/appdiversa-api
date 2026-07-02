"""
Servicios de parametrizacion de textos del flujo de formularios.
"""

from typing import Any
from uuid import UUID

from django.db import transaction

from aplicaciones.contenidos.constantes import ValoresPorDefectoFlujoFormulario
from aplicaciones.contenidos.models import (
    ConfiguracionFlujoFormulario,
    ConfiguracionInterfaz,
)
from aplicaciones.contenidos.selectores import obtener_configuracion_flujo_formulario_activa
from aplicaciones.internacionalizacion.servicios import aplicar_texto_traducido

ENTIDAD_FLUJO_FORMULARIO = "ConfiguracionFlujoFormulario"


def activar_configuracion_flujo_formulario(
    configuracion: ConfiguracionFlujoFormulario,
) -> ConfiguracionFlujoFormulario:
    """Activa una configuracion de flujo y desactiva las demas."""
    with transaction.atomic():
        configuracion.esta_activa = True
        configuracion.save(update_fields=["esta_activa", "fecha_modificacion"])
        ConfiguracionFlujoFormulario.objects.exclude(pk=configuracion.pk).update(
            esta_activa=False,
        )
    return configuracion


def _valor_campo(
    instancia: ConfiguracionFlujoFormulario | None,
    campo: str,
    valor_defecto: str,
) -> str:
    """Retorna el valor del campo o el defecto si la instancia no existe o esta vacia."""
    if instancia is None:
        return valor_defecto
    valor = getattr(instancia, campo, "") or ""
    return valor if valor.strip() else valor_defecto


def _resolver_email_soporte_terminos(
    flujo: ConfiguracionFlujoFormulario | None,
    interfaz: ConfiguracionInterfaz | None,
) -> str:
    """Resuelve el correo de soporte para terminos desde flujo o interfaz activa."""
    if flujo is not None and flujo.terminos_email_soporte:
        return flujo.terminos_email_soporte
    if interfaz is not None and interfaz.email_soporte:
        return interfaz.email_soporte
    return ValoresPorDefectoFlujoFormulario.TERMINOS_EMAIL_SOPORTE


def _valor_campo_traducido(
    instancia: ConfiguracionFlujoFormulario | None,
    campo: str,
    valor_defecto: str,
    mapa_traducciones: dict,
    uuid_entidad: UUID | None,
) -> str:
    """Retorna el valor del campo aplicando traduccion cuando corresponde."""
    valor = _valor_campo(instancia, campo, valor_defecto)
    if uuid_entidad is None:
        return valor
    return aplicar_texto_traducido(
        mapa_traducciones,
        ENTIDAD_FLUJO_FORMULARIO,
        uuid_entidad,
        campo,
        valor,
    )


def _construir_modal_salir(
    flujo: ConfiguracionFlujoFormulario | None,
    mapa_traducciones: dict,
    uuid_entidad: UUID | None,
) -> dict[str, str]:
    """Construye el bloque publico del modal salir sin guardar."""
    defecto = ValoresPorDefectoFlujoFormulario
    return {
        "titulo": _valor_campo_traducido(
            flujo, "modal_salir_titulo", defecto.MODAL_SALIR_TITULO,
            mapa_traducciones, uuid_entidad,
        ),
        "parrafo_1": _valor_campo_traducido(
            flujo, "modal_salir_p1", defecto.MODAL_SALIR_P1,
            mapa_traducciones, uuid_entidad,
        ),
        "parrafo_2": _valor_campo_traducido(
            flujo, "modal_salir_p2", defecto.MODAL_SALIR_P2,
            mapa_traducciones, uuid_entidad,
        ),
        "boton_volver": _valor_campo_traducido(
            flujo, "modal_salir_btn_volver", defecto.MODAL_SALIR_BTN_VOLVER,
            mapa_traducciones, uuid_entidad,
        ),
        "boton_salir": _valor_campo_traducido(
            flujo, "modal_salir_btn_salir", defecto.MODAL_SALIR_BTN_SALIR,
            mapa_traducciones, uuid_entidad,
        ),
        "link_sesion": _valor_campo_traducido(
            flujo, "modal_salir_link_sesion", defecto.MODAL_SALIR_LINK_SESION,
            mapa_traducciones, uuid_entidad,
        ),
    }


def _construir_modal_sesion(
    flujo: ConfiguracionFlujoFormulario | None,
    mapa_traducciones: dict,
    uuid_entidad: UUID | None,
) -> dict[str, str]:
    """Construye el bloque publico del modal iniciar sesion o registro."""
    defecto = ValoresPorDefectoFlujoFormulario
    return {
        "titulo": _valor_campo_traducido(
            flujo, "modal_sesion_titulo", defecto.MODAL_SESION_TITULO,
            mapa_traducciones, uuid_entidad,
        ),
        "parrafo": _valor_campo_traducido(
            flujo, "modal_sesion_parrafo", defecto.MODAL_SESION_PARRAFO,
            mapa_traducciones, uuid_entidad,
        ),
        "boton_login": _valor_campo_traducido(
            flujo, "modal_sesion_btn_login", defecto.MODAL_SESION_BTN_LOGIN,
            mapa_traducciones, uuid_entidad,
        ),
        "boton_registro": _valor_campo_traducido(
            flujo, "modal_sesion_btn_registro", defecto.MODAL_SESION_BTN_REGISTRO,
            mapa_traducciones, uuid_entidad,
        ),
        "link_cancelar": _valor_campo_traducido(
            flujo, "modal_sesion_link_cancelar", defecto.MODAL_SESION_LINK_CANCELAR,
            mapa_traducciones, uuid_entidad,
        ),
    }


def _construir_modal_guardado(
    flujo: ConfiguracionFlujoFormulario | None,
    mapa_traducciones: dict,
    uuid_entidad: UUID | None,
) -> dict[str, str]:
    """Construye el bloque publico del modal encuesta guardada."""
    defecto = ValoresPorDefectoFlujoFormulario
    return {
        "titulo": _valor_campo_traducido(
            flujo, "modal_guardado_titulo", defecto.MODAL_GUARDADO_TITULO,
            mapa_traducciones, uuid_entidad,
        ),
        "parrafo": _valor_campo_traducido(
            flujo, "modal_guardado_parrafo", defecto.MODAL_GUARDADO_PARRAFO,
            mapa_traducciones, uuid_entidad,
        ),
        "boton_seguir": _valor_campo_traducido(
            flujo, "modal_guardado_btn_seguir", defecto.MODAL_GUARDADO_BTN_SEGUIR,
            mapa_traducciones, uuid_entidad,
        ),
        "boton_otras": _valor_campo_traducido(
            flujo, "modal_guardado_btn_otras", defecto.MODAL_GUARDADO_BTN_OTRAS,
            mapa_traducciones, uuid_entidad,
        ),
    }


def _construir_terminos(
    flujo: ConfiguracionFlujoFormulario | None,
    interfaz: ConfiguracionInterfaz | None,
    mapa_traducciones: dict,
    uuid_entidad: UUID | None,
) -> dict[str, str | None]:
    """Construye el bloque publico de terminos y condiciones."""
    defecto = ValoresPorDefectoFlujoFormulario
    contenido_raw = ""
    if flujo is not None:
        contenido_raw = (flujo.terminos_contenido or "").strip()
    contenido_traducido = None
    if contenido_raw:
        contenido_traducido = _valor_campo_traducido(
            flujo,
            "terminos_contenido",
            contenido_raw,
            mapa_traducciones,
            uuid_entidad,
        )
    return {
        "titulo": _valor_campo_traducido(
            flujo, "terminos_titulo", defecto.TERMINOS_TITULO,
            mapa_traducciones, uuid_entidad,
        ),
        "contenido": contenido_traducido,
        "parrafo_1": _valor_campo_traducido(
            flujo, "terminos_p1", defecto.TERMINOS_P1,
            mapa_traducciones, uuid_entidad,
        ),
        "parrafo_2": _valor_campo_traducido(
            flujo, "terminos_p2", defecto.TERMINOS_P2,
            mapa_traducciones, uuid_entidad,
        ),
        "parrafo_3": _valor_campo_traducido(
            flujo, "terminos_p3", defecto.TERMINOS_P3,
            mapa_traducciones, uuid_entidad,
        ),
        "url_ley": _valor_campo(flujo, "terminos_url_ley", defecto.TERMINOS_URL_LEY),
        "url_politica_datos": _valor_campo(
            flujo,
            "terminos_url_politica_datos",
            defecto.TERMINOS_URL_POLITICA_DATOS,
        ),
        "email_soporte": _resolver_email_soporte_terminos(flujo, interfaz),
        "boton_aceptar": _valor_campo_traducido(
            flujo,
            "terminos_boton_aceptar",
            defecto.TERMINOS_BOTON_ACEPTAR,
            mapa_traducciones,
            uuid_entidad,
        ),
        "boton_cerrar": _valor_campo_traducido(
            flujo,
            "terminos_boton_cerrar",
            defecto.TERMINOS_BOTON_CERRAR,
            mapa_traducciones,
            uuid_entidad,
        ),
        "enlace_terminos": _valor_campo_traducido(
            flujo,
            "terminos_enlace",
            defecto.TERMINOS_ENLACE,
            mapa_traducciones,
            uuid_entidad,
        ),
        "texto_enlace_ley": _valor_campo_traducido(
            flujo,
            "terminos_enlace_ley",
            defecto.TERMINOS_ENLACE_LEY,
            mapa_traducciones,
            uuid_entidad,
        ),
        "texto_enlace_politica_datos": _valor_campo_traducido(
            flujo,
            "terminos_enlace_politica_datos",
            defecto.TERMINOS_ENLACE_POLITICA_DATOS,
            mapa_traducciones,
            uuid_entidad,
        ),
    }


def _resolver_url_imagen_exito(
    flujo: ConfiguracionFlujoFormulario | None,
    solicitud: Any,
) -> str | None:
    """Resuelve la URL publica de la imagen de la pantalla de envio exitoso."""
    if flujo is None or flujo.img_enc_enviada_exito_id is None:
        return None
    from aplicaciones.archivos.servicios import construir_url

    return construir_url(flujo.img_enc_enviada_exito, solicitud)


def _construir_envio_exitoso(
    flujo: ConfiguracionFlujoFormulario | None,
    solicitud: Any,
    mapa_traducciones: dict,
    uuid_entidad: UUID | None,
) -> dict[str, str | None]:
    """Construye el bloque publico de la pantalla de envio exitoso."""
    defecto = ValoresPorDefectoFlujoFormulario
    return {
        "imagen_url": _resolver_url_imagen_exito(flujo, solicitud),
        "imagen_alt": _valor_campo_traducido(
            flujo,
            "img_enc_enviada_exito_alt",
            defecto.ENVIO_EXITO_IMAGEN_ALT,
            mapa_traducciones,
            uuid_entidad,
        ),
    }


def construir_flujo_formulario_por_defecto(
    interfaz: ConfiguracionInterfaz | None = None,
) -> dict[str, dict]:
    """Construye el bloque flujo_formulario con valores por defecto."""
    return construir_bloque_flujo_formulario_publico(
        flujo=None,
        interfaz=interfaz,
        mapa_traducciones={},
        uuid_entidad=None,
    )


def construir_bloque_flujo_formulario_publico(
    flujo: ConfiguracionFlujoFormulario | None = None,
    interfaz: ConfiguracionInterfaz | None = None,
    mapa_traducciones: dict | None = None,
    uuid_entidad: UUID | None = None,
    solicitud: Any = None,
) -> dict[str, dict]:
    """Construye el bloque flujo_formulario expuesto al frontend."""
    if flujo is None:
        flujo = obtener_configuracion_flujo_formulario_activa()
    traducciones = mapa_traducciones or {}
    uuid_flujo = uuid_entidad or (flujo.uuid if flujo is not None else None)
    return {
        "modal_salir": _construir_modal_salir(flujo, traducciones, uuid_flujo),
        "modal_sesion": _construir_modal_sesion(flujo, traducciones, uuid_flujo),
        "modal_guardado": _construir_modal_guardado(flujo, traducciones, uuid_flujo),
        "terminos": _construir_terminos(flujo, interfaz, traducciones, uuid_flujo),
        "envio_exitoso": _construir_envio_exitoso(
            flujo, solicitud, traducciones, uuid_flujo,
        ),
    }
