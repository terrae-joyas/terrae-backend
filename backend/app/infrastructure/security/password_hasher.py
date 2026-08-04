"""Hashing y verificación de contraseñas (bcrypt vía passlib)."""

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password_plano: str) -> str:
    return _pwd_context.hash(password_plano)


def verificar_password(password_plano: str, hashed_password: str) -> bool:
    return _pwd_context.verify(password_plano, hashed_password)
