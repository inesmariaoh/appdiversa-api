"""
Excepciones funcionales del modulo de usuarios.
"""

from aplicaciones.usuarios.constantes import MensajesAuth, MensajesUsuariosAdmin


class CredencialesInvalidasError(Exception):
    """Indica que las credenciales de autenticacion no son validas."""

    def __init__(self) -> None:
        super().__init__(MensajesAuth.CREDENCIALES_INVALIDAS)
        self.mensaje = MensajesAuth.CREDENCIALES_INVALIDAS


class UsuarioInactivoError(Exception):
    """Indica que el usuario existe pero esta inactivo."""

    def __init__(self) -> None:
        super().__init__(MensajesAuth.USUARIO_INACTIVO)
        self.mensaje = MensajesAuth.USUARIO_INACTIVO


class UsuarioNoEncontradoError(Exception):
    """Indica que el usuario solicitado no existe."""

    def __init__(self) -> None:
        super().__init__(MensajesUsuariosAdmin.USUARIO_NO_ENCONTRADO)
        self.mensaje = MensajesUsuariosAdmin.USUARIO_NO_ENCONTRADO


class GruposInvalidosError(Exception):
    """Indica que uno o mas grupos indicados no existen."""

    def __init__(self) -> None:
        super().__init__(MensajesUsuariosAdmin.GRUPOS_INVALIDOS)
        self.mensaje = MensajesUsuariosAdmin.GRUPOS_INVALIDOS


class ContrasenaActualIncorrectaError(Exception):
    """Indica que la contrasena actual no coincide."""

    def __init__(self) -> None:
        super().__init__(MensajesAuth.CONTRASENA_ACTUAL_INCORRECTA)
        self.mensaje = MensajesAuth.CONTRASENA_ACTUAL_INCORRECTA


class UsernameDuplicadoError(Exception):
    """Indica que el nombre de usuario ya existe."""

    def __init__(self) -> None:
        super().__init__(MensajesAuth.USERNAME_DUPLICADO)
        self.mensaje = MensajesAuth.USERNAME_DUPLICADO


class EmailDuplicadoError(Exception):
    """Indica que el correo electronico ya existe."""

    def __init__(self) -> None:
        super().__init__(MensajesAuth.EMAIL_DUPLICADO)
        self.mensaje = MensajesAuth.EMAIL_DUPLICADO


class ContrasenasNoCoincidenError(Exception):
    """Indica que las contrasenas no coinciden."""

    def __init__(self) -> None:
        super().__init__(MensajesAuth.CONTRASENAS_NO_COINCIDEN)
        self.mensaje = MensajesAuth.CONTRASENAS_NO_COINCIDEN


class ContrasenaInvalidaError(Exception):
    """Indica que la contrasena no cumple los validadores de Django."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class TokenRestaurarInvalidoError(Exception):
    """Indica que el token de restauracion no es valido."""

    def __init__(self) -> None:
        super().__init__(MensajesAuth.TOKEN_RESTAURAR_INVALIDO)
        self.mensaje = MensajesAuth.TOKEN_RESTAURAR_INVALIDO
