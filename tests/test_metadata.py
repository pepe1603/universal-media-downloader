from pathlib import Path

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
