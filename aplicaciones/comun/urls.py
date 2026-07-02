"""
Rutas de la API bajo el prefijo /api/v1/.
"""

from django.urls import include, path

from .views import verificar_salud

urlpatterns = [
    path("salud/", verificar_salud, name="verificar-salud"),
    path("formularios/", include("aplicaciones.formularios.urls")),
    path("respuestas/", include("aplicaciones.respuestas.urls")),
    path("sesiones/", include("aplicaciones.sesiones_anonimas.urls")),
    path("sincronizacion/", include("aplicaciones.sincronizacion.urls")),
    path("auditoria/", include("aplicaciones.auditoria.urls")),
    path("interfaz/", include("aplicaciones.contenidos.urls")),
    path("analitica/", include("aplicaciones.analitica.urls")),
    path("catalogos/", include("aplicaciones.catalogos.urls")),
    path("internacionalizacion/", include("aplicaciones.internacionalizacion.urls")),
    path("archivos/", include("aplicaciones.archivos.urls")),
    path("notificaciones/", include("aplicaciones.notificaciones.urls")),
    path("exportaciones/", include("aplicaciones.exportaciones.urls")),
    path("", include("aplicaciones.usuarios.urls")),
    path("contacto/", include("aplicaciones.usuarios.api.v1.urls_contacto")),
    path("admin/", include("aplicaciones.comun.admin_urls")),
]
