"""Excepciones de la capa de aplicación — el router HTTP las traduce a
códigos de estado apropiados (ver api/v1/routers/auth.py)."""


class CorreoYaRegistradoError(Exception):
    pass


class CredencialesInvalidasError(Exception):
    pass


class UsuarioInactivoError(Exception):
    pass


class UsuarioNoEncontradoError(Exception):
    pass
