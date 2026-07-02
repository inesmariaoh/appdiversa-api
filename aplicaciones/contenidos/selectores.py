"""
Selectores de consulta para contenidos e interfaz.
"""

from aplicaciones.contenidos.models import ConfiguracionInterfaz, ConfiguracionFlujoFormulario, LogoInterfaz


def obtener_configuracion_interfaz_activa() -> ConfiguracionInterfaz | None:
    """Retorna la configuracion de interfaz activa si existe."""
    return ConfiguracionInterfaz.objects.filter(esta_activa=True).first()


def obtener_configuracion_flujo_formulario_activa() -> ConfiguracionFlujoFormulario | None:
    """Retorna la configuracion de textos de flujo activa."""
    return ConfiguracionFlujoFormulario.objects.filter(
        esta_activa=True,
        esta_eliminado=False,
    ).first()


def _consultar_logos_activos(
    *,
    solo_activos: bool,
) -> list[LogoInterfaz]:
    """Retorna logos ordenados por fecha de modificacion descendente."""
    consulta = LogoInterfaz.objects.select_related(
        "archivo_repositorio",
        "configuracion_interfaz",
    )
    if solo_activos:
        consulta = consulta.filter(esta_activo=True)
    return list(consulta.order_by("-fecha_modificacion"))


def obtener_mapa_logos_interfaz(
    configuracion: ConfiguracionInterfaz | None = None,
    *,
    solo_activos: bool = True,
) -> dict[str, LogoInterfaz]:
    """Retorna un mapa codigo -> logo priorizando la configuracion indicada."""
    logos = _consultar_logos_activos(solo_activos=solo_activos)
    mapa: dict[str, LogoInterfaz] = {}
    config_id = configuracion.pk if configuracion is not None else None

    if config_id is not None:
        for logo in logos:
            if logo.configuracion_interfaz_id == config_id and logo.codigo not in mapa:
                mapa[logo.codigo] = logo

    for logo in logos:
        if logo.codigo not in mapa:
            mapa[logo.codigo] = logo

    return mapa


def obtener_logos_interfaz_por_configuracion(
    configuracion: ConfiguracionInterfaz,
    *,
    solo_activos: bool = True,
) -> list[LogoInterfaz]:
    """Retorna los logos resueltos para una configuracion de interfaz."""
    mapa = obtener_mapa_logos_interfaz(configuracion, solo_activos=solo_activos)
    return sorted(mapa.values(), key=lambda logo: (logo.orden, logo.codigo))
