from pathlib import Path

from src.core.file_organizer import DestinationFolder, FileOrganizer


def _touch(path: Path, data: bytes = b"x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def test_move_missing_file(tmp_path, console):
    res = FileOrganizer(console).move_to_folder(
        tmp_path / "nope.mp3", DestinationFolder.MUSIC, tmp_path
    )
    assert res.success is False
    assert "no encontrado" in res.error_message


def test_move_to_music(tmp_path, console):
    src = _touch(tmp_path / "in" / "a.mp3")
    base = tmp_path / "storage"
    res = FileOrganizer(console).move_to_folder(src, DestinationFolder.MUSIC, base)
    assert res.success is True
    assert res.destination == base / "Music" / "UniversalDownloader" / "a.mp3"
    assert res.destination.exists() and not src.exists()


def test_move_collision_adds_suffix(tmp_path, console):
    base = tmp_path / "storage"
    org = FileOrganizer(console)
    first = org.move_to_folder(_touch(tmp_path / "a" / "x.mp4"), DestinationFolder.VIDEOS, base)
    second = org.move_to_folder(_touch(tmp_path / "b" / "x.mp4"), DestinationFolder.VIDEOS, base)
    assert first.destination.name == "x.mp4"
    assert second.destination.name == "x_1.mp4"


def test_list_downloaded_files_filters_and_handles_missing(tmp_path, console):
    org = FileOrganizer(console)
    assert org.list_downloaded_files(tmp_path / "missing") == []
    _touch(tmp_path / "a.mp3")
    _touch(tmp_path / "sub" / "b.mp4")
    _touch(tmp_path / "c.txt")
    names = {p.name for p in org.list_downloaded_files(tmp_path)}
    assert names == {"a.mp3", "b.mp4"}


def test_auto_organize_routes_by_extension(tmp_path, console):
    src = tmp_path / "dl"
    _touch(src / "song.mp3")
    _touch(src / "clip.mp4")
    storage = tmp_path / "storage"
    results = FileOrganizer(console).auto_organize(src, storage)
    assert all(r.success for r in results)
    assert (storage / "Music" / "UniversalDownloader" / "song.mp3").exists()
    assert (storage / "Movies" / "UniversalDownloader" / "clip.mp4").exists()
