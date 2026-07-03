"""
Pruebas de la API administrativa de banderas de accesibilidad de interfaz.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.contenidos.constantes import TemaInterfaz
from aplicaciones.contenidos.models import ConfiguracionInterfaz

URL_ADMIN_ACCESIBILIDAD = "/api/v1/interfaz/admin/accesibilidad/"
User = get_user_model()


class AccesibilidadAdminApiTests(TestCase):
    """Pruebas del endpoint administrativo de banderas de accesibilidad."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.administrador = User.objects.create_superuser(
            username="admin_config",
            email="admin_config@appdiversa.co",
            password="Clave-Segura-2026",
        )

    def test_requiere_autenticacion(self) -> None:
        respuesta = self.cliente.get(URL_ADMIN_ACCESIBILIDAD)

        self.assertIn(
            respuesta.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_usuario_sin_permiso_no_puede_actualizar(self) -> None:
        usuario = User.objects.create_user(
            username="encuestado",
            email="encuestado@appdiversa.co",
            password="Clave-Segura-2026",
        )
        self.cliente.force_login(usuario)

        respuesta = self.cliente.patch(
            URL_ADMIN_ACCESIBILIDAD,
            {"fuente_dislexia_habilitada": True},
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_retorna_valores_por_defecto_sin_configuracion(self) -> None:
        self.cliente.force_login(self.administrador)

        respuesta = self.cliente.get(URL_ADMIN_ACCESIBILIDAD)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertFalse(datos["fuente_dislexia_habilitada"])
        self.assertEqual(datos["tema_por_defecto"], TemaInterfaz.CLARO)

    def test_patch_crea_configuracion_y_actualiza_banderas(self) -> None:
        self.cliente.force_login(self.administrador)

        respuesta = self.cliente.patch(
            URL_ADMIN_ACCESIBILIDAD,
            {
                "fuente_dislexia_habilitada": True,
                "lengua_senas_habilitada": True,
                "tema_por_defecto": TemaInterfaz.ALTO_CONTRASTE,
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertTrue(datos["fuente_dislexia_habilitada"])
        self.assertTrue(datos["lengua_senas_habilitada"])
        self.assertEqual(datos["tema_por_defecto"], TemaInterfaz.ALTO_CONTRASTE)

        configuracion = ConfiguracionInterfaz.objects.get(esta_activa=True)
        self.assertTrue(configuracion.accesibilidad_fuente_dislexia_habilitada)
        self.assertTrue(configuracion.accion_lengua_senas_habilitada)
        self.assertEqual(
            configuracion.accesibilidad_tema_por_defecto,
            TemaInterfaz.ALTO_CONTRASTE,
        )

    def test_patch_actualiza_configuracion_activa_existente(self) -> None:
        ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="AppDiversa",
            esta_activa=True,
            accesibilidad_fuente_dislexia_habilitada=False,
        )
        self.cliente.force_login(self.administrador)

        respuesta = self.cliente.patch(
            URL_ADMIN_ACCESIBILIDAD,
            {"fuente_dislexia_habilitada": True},
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(ConfiguracionInterfaz.objects.filter(esta_activa=True).count(), 1)
        configuracion = ConfiguracionInterfaz.objects.get(esta_activa=True)
        self.assertTrue(configuracion.accesibilidad_fuente_dislexia_habilitada)

    def test_patch_rechaza_tema_invalido(self) -> None:
        self.cliente.force_login(self.administrador)

        respuesta = self.cliente.patch(
            URL_ADMIN_ACCESIBILIDAD,
            {"tema_por_defecto": "tema_inexistente"},
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_incluye_lengua_senas_y_centro_relevo(self) -> None:
        self.cliente.force_login(self.administrador)

        respuesta = self.cliente.get(URL_ADMIN_ACCESIBILIDAD)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertIn("url_lengua_senas", datos)
        self.assertIn("texto_lengua_senas", datos)
        self.assertIn("centro_relevo_habilitado", datos)
        self.assertIn("url_centro_relevo", datos)
        self.assertFalse(datos["centro_relevo_habilitado"])

    def test_patch_actualiza_lengua_senas_y_centro_relevo(self) -> None:
        self.cliente.force_login(self.administrador)

        respuesta = self.cliente.patch(
            URL_ADMIN_ACCESIBILIDAD,
            {
                "lengua_senas_habilitada": True,
                "url_lengua_senas": "https://videos.example.com/senas.mp4",
                "texto_lengua_senas": "Ver instrucciones en señas",
                "centro_relevo_habilitado": True,
                "url_centro_relevo": "https://centroderelevo.gov.co/",
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertEqual(
            datos["url_lengua_senas"],
            "https://videos.example.com/senas.mp4",
        )
        self.assertEqual(datos["texto_lengua_senas"], "Ver instrucciones en señas")
        self.assertTrue(datos["centro_relevo_habilitado"])
        self.assertEqual(datos["url_centro_relevo"], "https://centroderelevo.gov.co/")

        configuracion = ConfiguracionInterfaz.objects.get(esta_activa=True)
        self.assertTrue(configuracion.centro_relevo_habilitado)
        self.assertEqual(
            configuracion.url_centro_relevo,
            "https://centroderelevo.gov.co/",
        )
