"""
Pruebas del autorregistro de usuarios normales con correo y contrasena.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.usuarios.constantes import GrupoSistema
from aplicaciones.usuarios.tests.helpers import (
    CONTRASENA_PRUEBA,
    URL_REGISTRO_CORREO,
    inicializar_entorno_usuarios,
)

User = get_user_model()


class RegistroCorreoApiTests(TestCase):
    """Pruebas del endpoint de autorregistro con correo electronico."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()

    def _registrar(self, correo: str, contrasena: str = CONTRASENA_PRUEBA):
        """Envia una solicitud de autorregistro con correo."""
        return self.cliente.post(
            URL_REGISTRO_CORREO,
            {"correo": correo, "contrasena": contrasena},
            format="json",
        )

    def test_registro_correcto_asigna_rol_encuestado(self) -> None:
        respuesta = self._registrar("persona@example.com")
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        usuario = User.objects.get(email="persona@example.com")
        self.assertTrue(usuario.is_active)
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        self.assertTrue(
            usuario.groups.filter(name=GrupoSistema.ENCUESTADO).exists(),
        )

    def test_username_se_deriva_del_correo(self) -> None:
        self._registrar("Maria.Perez@example.com")
        self.assertTrue(User.objects.filter(username="maria.perez").exists())

    def test_correo_repetido_genera_username_unico(self) -> None:
        primera = self._registrar("juan@example.com")
        segunda = self._registrar("juan@otrodominio.com")
        self.assertEqual(primera.status_code, status.HTTP_201_CREATED)
        self.assertEqual(segunda.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username__startswith="juan").count(), 2)

    def test_email_duplicado_rechazado(self) -> None:
        User.objects.create_user(
            username="existente",
            email="repetido@example.com",
            password=CONTRASENA_PRUEBA,
        )
        respuesta = self._registrar("repetido@example.com")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_correo_invalido_rechazado(self) -> None:
        respuesta = self._registrar("correo-no-valido")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_debil_rechazado(self) -> None:
        respuesta = self._registrar("otra@example.com", contrasena="123")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registro_no_permite_roles_administradores(self) -> None:
        self._registrar("normal@example.com")
        usuario = User.objects.get(email="normal@example.com")
        grupos = set(usuario.groups.values_list("name", flat=True))
        self.assertEqual(grupos, {GrupoSistema.ENCUESTADO})
