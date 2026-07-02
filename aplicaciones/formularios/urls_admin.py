"""
Rutas administrativas del motor de formularios bajo /api/v1/admin/.
"""

from django.urls import include, path

from aplicaciones.formularios.api.v1 import urls_admin

urlpatterns = [
    path("formularios/", include(urls_admin)),
    path("versiones/", include(urls_admin.urlpatterns_versiones)),
    path("secciones/", include(urls_admin.urlpatterns_secciones)),
    path("preguntas/", include(urls_admin.urlpatterns_preguntas)),
    path("opciones/", include(urls_admin.urlpatterns_opciones)),
    path("textos/", include(urls_admin.urlpatterns_textos)),
    path("reglas/", include(urls_admin.urlpatterns_reglas)),
]
