"""Fixtures compartidas de la suite de tests."""

import wave
from pathlib import Path

import pytest
from rich.console import Console

from src.storage.database import Database


@pytest.fixture
def console() -> Console:
    """Consola Rich silenciosa para tests."""
    return Console(quiet=True)


@pytest.fixture
def db(tmp_path: Path, console: Console) -> Database:
    """Base de datos SQLite temporal."""
    return Database(db_path=tmp_path / "umd.db", console=console)


@pytest.fixture
def wav_file(tmp_path: Path) -> Path:
    """Archivo WAV mínimo válido (0.1 s de silencio)."""
    path = tmp_path / "sample.wav"
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"\x00\x00" * 800)
    return path


@pytest.fixture
def netscape_cookies(tmp_path: Path) -> Path:
    """Archivo cookies.txt en formato Netscape válido."""
    path = tmp_path / "cookies.txt"
    path.write_text(
        "# Netscape HTTP Cookie File\n"
        ".example.com\tTRUE\t/\tFALSE\t0\tname\tvalue\n",
        encoding="utf-8",
    )
    return path
