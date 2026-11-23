"""Validación y normalización de entradas del usuario para la CLI."""

import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

MAX_USERNAME_LENGTH = 32
_USERNAME_RE = re.compile(r"[\w .-]+", re.UNICODE)
_ALLOWED_SCHEMES = {"http", "https"}


def normalize_url(raw: str) -> Optional[str]:
    """Limpia una URL ingresada y valida que sea http(s).

    Args:
        raw: Texto ingresado por el usuario.

    Returns:
        La URL sin espacios (con ``https://`` si faltaba el esquema), o None si es inválida.
    """
    url = raw.strip().strip("'\"")
    if not url or any(ch.isspace() for ch in url):
        return None
    if "://" not in url:
        url = f"https://{url}"
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES or not parsed.hostname or "." not in parsed.hostname:
        return None
    return url


def normalize_username(raw: str) -> Optional[str]:
    """Valida un nombre de usuario (sin separadores de ruta ni caracteres de control).

    Args:
        raw: Texto ingresado por el usuario.

    Returns:
        El nombre limpio, o None si es inválido.
    """
    name = raw.strip()
    if not name or len(name) > MAX_USERNAME_LENGTH:
        return None
    if not _USERNAME_RE.fullmatch(name):
        return None
    return name


def normalize_user_path(raw: str) -> Optional[Path]:
    """Convierte una ruta ingresada en Path absoluto (quita comillas, expande ``~``).

    Args:
        raw: Texto ingresado por el usuario.

    Returns:
        Path resuelto, o None si el texto está vacío.
    """
    text = raw.strip().strip("'\"")
    if not text:
        return None
    return Path(text).expanduser().resolve()
