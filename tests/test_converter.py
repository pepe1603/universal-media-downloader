import shutil
from pathlib import Path

import pytest

from src.core.converter import AudioConverter, AudioFormat


@pytest.fixture
def conv(console):
    return AudioConverter(console)


@pytest.mark.parametrize("fmt", list(AudioFormat))
def test_command_shape(conv, fmt, tmp_path):
    cmd = conv._build_ffmpeg_command(tmp_path / "in.m4a", tmp_path / "out", fmt)
    assert cmd[0] == "ffmpeg" and cmd[1] == "-i"
    assert cmd[-1] == str(tmp_path / "out")
    assert "-codec:a" in cmd


def test_supported_formats(conv):
    assert conv.get_supported_formats() == list(AudioFormat)


def test_descriptions_and_bitrates():
    for fmt in AudioFormat:
        assert fmt.description


def test_convert_without_ffmpeg(conv, monkeypatch, tmp_path):
    monkeypatch.setattr(shutil, "which", lambda _n: None)
    res = conv.convert(tmp_path / "a.wav", AudioFormat.MP3)
    assert res.success is False and "FFmpeg" in res.error_message


def test_convert_missing_input(conv, monkeypatch, tmp_path):
    monkeypatch.setattr(shutil, "which", lambda _n: "/usr/bin/ffmpeg")
    res = conv.convert(tmp_path / "missing.wav", AudioFormat.MP3)
    assert res.success is False and "no encontrado" in res.error_message


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="requiere ffmpeg")
def test_convert_wav_to_flac_real(conv, wav_file, tmp_path):
    res = conv.convert(wav_file, AudioFormat.FLAC, output_dir=tmp_path / "out")
    assert res.success is True
    assert Path(res.output_path).suffix == ".flac"
    assert Path(res.output_path).stat().st_size > 0
