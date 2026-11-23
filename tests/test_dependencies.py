import shutil
import subprocess
from types import SimpleNamespace

from src.core import dependencies
from src.core.dependencies import DependencyChecker


def test_ffmpeg_missing(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _n: None)
    status = DependencyChecker.check_ffmpeg()
    assert status.installed is False


def test_ffmpeg_installed(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _n: "/usr/bin/ffmpeg")
    monkeypatch.setattr(
        subprocess, "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="ffmpeg version 6.1 Copyright\n"),
    )
    status = DependencyChecker.check_ffmpeg()
    assert status.installed is True and status.version == "6.1"


def test_ffmpeg_timeout(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _n: "/usr/bin/ffmpeg")

    def boom(*a, **k):
        raise subprocess.TimeoutExpired(cmd="ffmpeg", timeout=5)

    monkeypatch.setattr(subprocess, "run", boom)
    assert DependencyChecker.check_ffmpeg().installed is False


def test_ytdlp_installed():
    assert DependencyChecker.check_ytdlp().installed is True


def test_check_all_and_show_status(console):
    assert set(DependencyChecker.check_all()) == {"ffmpeg", "ytdlp"}
    DependencyChecker.show_status(console)
    assert dependencies.DependencyStatus
