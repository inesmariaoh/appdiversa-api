"""
Rutas de la API v1 del modulo de usuarios.
"""

from django.urls import path

from aplicaciones.usuarios.api.v1.admin_views import (
    GruposAdminListView,
    PermisosAdminListView,
    UsuarioAdminActivarView,
    UsuarioAdminAsignarGruposView,
    UsuarioAdminDesactivarView,
    UsuarioAdminDetalleView,
    UsuariosAdminListCreateView,
)
from aplicaciones.usuarios.api.v1.views import (
    CambiarPasswordView,
    ContactoView,
    CsrfCookieView,
    EliminarCuentaView,
    LoginView,
    LogoutView,
    MeView,
    MisRespuestasExportarView,
    MisRespuestasView,
    PerfilView,
    ReenviarVerificacionView,
    RegistroCorreoView,
    RegistroView,
    RestaurarPasswordView,
    SolicitarRestaurarPasswordView,
    VerificarCorreoView,
)

urlpatterns_auth = [
    path("csrf/", CsrfCookieView.as_view(), name="auth-csrf"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("perfil/", PerfilView.as_view(), name="auth-perfil"),
    path("mis-respuestas/", MisRespuestasView.as_view(), name="auth-mis-respuestas"),
    path(
        "mis-respuestas/<uuid:uuid_sesion>/exportar/",
        MisRespuestasExportarView.as_view(),
        name="auth-mis-respuestas-exportar",
    ),
    path("cambiar-password/", CambiarPasswordView.as_view(), name="auth-cambiar-password"),
    path("eliminar-cuenta/", EliminarCuentaView.as_view(), name="auth-eliminar-cuenta"),
    path("registro/", RegistroView.as_view(), name="auth-registro"),
    path("registro/correo/", RegistroCorreoView.as_view(), name="auth-registro-correo"),
    path(
        "solicitar-restaurar-password/",
        SolicitarRestaurarPasswordView.as_view(),
        name="auth-solicitar-restaurar-password",
    ),
    path(
        "restaurar-password/",
        RestaurarPasswordView.as_view(),
        name="auth-restaurar-password",
    ),
    path(
        "verificar-correo/",
        VerificarCorreoView.as_view(),
        name="auth-verificar-correo",
    ),
    path(
        "reenviar-verificacion/",
        ReenviarVerificacionView.as_view(),
        name="auth-reenviar-verificacion",
    ),
]

urlpatterns_admin = [
    path("usuarios/", UsuariosAdminListCreateView.as_view(), name="admin-usuarios-list"),
    path(
        "usuarios/<int:usuario_id>/",
        UsuarioAdminDetalleView.as_view(),
        name="admin-usuarios-detalle",
    ),
    path(
        "usuarios/<int:usuario_id>/activar/",
        UsuarioAdminActivarView.as_view(),
        name="admin-usuarios-activar",
    ),
    path(
        "usuarios/<int:usuario_id>/desactivar/",
        UsuarioAdminDesactivarView.as_view(),
        name="admin-usuarios-desactivar",
    ),
    path(
        "usuarios/<int:usuario_id>/asignar-grupos/",
        UsuarioAdminAsignarGruposView.as_view(),
        name="admin-usuarios-asignar-grupos",
    ),
    path("grupos/", GruposAdminListView.as_view(), name="admin-grupos-list"),
    path("permisos/", PermisosAdminListView.as_view(), name="admin-permisos-list"),
]

urlpatterns_contacto = [
    path("", ContactoView.as_view(), name="contacto"),
]
