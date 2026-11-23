import shutil
import subprocess
from pathlib import Path

import pytest
from mutagen.wave import WAVE
from src.core.metadata import AudioMetadata, MetadataHandler


def test_missing_file(console, tmp_path):
    handler = MetadataHandler(console)
    assert handler.embed_metadata(tmp_path / "no.mp3", AudioMetadata(title="x")) is False


def test_unsupported_extension(console, tmp_path):
    f = tmp_path / "a.xyz"
    f.write_bytes(b"x")
    assert MetadataHandler(console).embed_metadata(f, AudioMetadata(title="x")) is False


def test_defaults():
    meta = AudioMetadata(title="T")
    assert meta.artist == "Desconocido" and meta.album == "Single"


def test_embed_wav(console, wav_file):
    meta = AudioMetadata(title="Título ñ", artist="Artista", album="Álbum")
    assert MetadataHandler(console).embed_metadata(wav_file, meta) is True
    tags = WAVE(wav_file).tags
    assert str(tags["TIT2"]) == "Título ñ"
    assert str(tags["TPE1"]) == "Artista"


needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="requiere ffmpeg")


def _encode(src: Path, dest: Path) -> Path:
    codec_args = ["-c:a", "libvorbis"] if dest.suffix == ".ogg" else []  # el códec por defecto de .ogg varía
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), *codec_args, str(dest)],
        capture_output=True,
    )
    if result.returncode != 0:
        pytest.skip(f"ffmpeg no puede generar {dest.suffix} en este entorno")
    return dest


@needs_ffmpeg
@pytest.mark.parametrize("ext", ["mp3", "flac", "ogg", "m4a"])
def test_embed_encoded_formats(console, wav_file, tmp_path, ext):
    audio = _encode(wav_file, tmp_path / f"s.{ext}")
    meta = AudioMetadata(title="Tít", artist="Art", album="Alb", date="2026", genre="Pop")
    assert MetadataHandler(console).embed_metadata(audio, meta) is True


@needs_ffmpeg
def test_embed_mp3_with_cover(console, wav_file, tmp_path):
    audio = _encode(wav_file, tmp_path / "s.mp3")
    cover = tmp_path / "cover.jpg"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=red:s=16x16", "-frames:v", "1", str(cover)],
        check=True, capture_output=True,
    )
    meta = AudioMetadata(title="T", cover_path=cover)
    assert MetadataHandler(console).embed_metadata(audio, meta) is True
