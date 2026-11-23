from pathlib import Path

import pytest

from src.core.environment import EnvironmentDetector, EnvironmentInfo, EnvironmentType


@pytest.fixture(autouse=True)
def _clean_android_env(monkeypatch):
    for var in ("TERMUX_VERSION", "ANDROID_ROOT", "ANDROID_DATA"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr("shutil.which", lambda _name: None)


def test_detect_returns_environment_info():
    info = EnvironmentDetector.detect()
    assert isinstance(info, EnvironmentInfo)
    assert isinstance(info.home_path, Path)
    assert isinstance(info.env_type, EnvironmentType)


def test_termux_detected_by_env_var(monkeypatch):
    monkeypatch.setenv("TERMUX_VERSION", "0.118")
    assert EnvironmentDetector._is_termux() is True
    assert EnvironmentDetector.detect().env_type is EnvironmentType.TERMUX


def test_android_root_detected_as_termux(monkeypatch):
    monkeypatch.setenv("ANDROID_ROOT", "/system")
    assert EnvironmentDetector._is_termux() is True


def test_not_termux_without_markers():
    assert EnvironmentDetector._is_termux() is False


@pytest.mark.parametrize(
    "system,expected",
    [
        ("Windows", EnvironmentType.WINDOWS),
        ("Darwin", EnvironmentType.MACOS),
        ("Linux", EnvironmentType.LINUX),
    ],
)
def test_detect_by_platform_system(monkeypatch, system, expected):
    monkeypatch.setattr("platform.system", lambda: system)
    info = EnvironmentDetector.detect()
    assert info.env_type is expected
    assert info.is_mobile is False
