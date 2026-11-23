from types import SimpleNamespace

import pytest
import yt_dlp
from src.core import playlist as pl
from src.core.downloader import DownloadResult, Quality
from src.core.playlist import (
    PlaylistDownloader,
    PlaylistEntry,
    build_playlist_url,
    build_video_url,
    extract_playlist_id,
    has_video_reference,
    safe_folder_name,
)
from src.storage.database import DownloadRecord

VID = "abcdefghijk"  # 11 caracteres


@pytest.mark.parametrize("url,expected", [
    ("https://www.youtube.com/playlist?list=PLabc123", "PLabc123"),
    ("https://www.youtube.com/watch?v=abcdefghijk&list=PLabc123&index=2", "PLabc123"),
    ("https://youtu.be/abcdefghijk?list=PLabc123", "PLabc123"),
    ("https://music.youtube.com/playlist?list=OLAK5uy_x", "OLAK5uy_x"),
])
def test_extract_playlist_id_ok(url, expected):
    assert extract_playlist_id(url) == expected


@pytest.mark.parametrize("url", [
    "https://www.youtube.com/watch?v=abcdefghijk",
    "https://www.youtube.com/watch?v=abcdefghijk&list=RDabcdefghijk",  # mix automático
    "https://evil.com/playlist?list=PLabc123",
    "https://www.tiktok.com/@u?list=PLabc123",
    "https://www.youtube.com/playlist?list=../etc",
    "https://www.youtube.com/playlist?list=",
    "not a url",
])
def test_extract_playlist_id_rejected(url):
    assert extract_playlist_id(url) is None


def test_has_video_reference():
    assert has_video_reference("https://www.youtube.com/watch?v=abcdefghijk&list=PLx")
    assert has_video_reference("https://youtu.be/abcdefghijk?list=PLx")
    assert not has_video_reference("https://www.youtube.com/playlist?list=PLx")


def test_build_urls():
    assert build_playlist_url("PLx") == "https://www.youtube.com/playlist?list=PLx"
    assert build_video_url(VID) == f"https://www.youtube.com/watch?v={VID}"
    with pytest.raises(ValueError):
        build_video_url("short")
    with pytest.raises(ValueError):
        build_video_url("abc&list=hack!")


def test_safe_folder_name():
    assert "/" not in safe_folder_name("../../etc/passwd", "PLx")
    assert not safe_folder_name("...", "PLx").startswith(".")
    assert safe_folder_name("", "PLfallback") == "PLfallback"
    assert "/" not in safe_folder_name("///", "PLfallback")
    assert len(safe_folder_name("a" * 500, "PLx")) <= pl.MAX_FOLDER_NAME_LENGTH


class FakeYDL:
    data: dict = {}
    error: Exception | None = None

    def __init__(self, opts):
        FakeYDL.opts = opts

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def extract_info(self, url, download=True):
        if FakeYDL.error:
            raise FakeYDL.error
        return FakeYDL.data


class FakeDownloader:
    """Sustituye a MediaDownloader: resultados programados por video_id."""

    def __init__(self, db, outcomes, tmp_path):
        self.database = db
        self.cookie_manager = SimpleNamespace(get_ydl_opts=lambda _p: {})
        self.outcomes = outcomes
        self.calls = []
        self.tmp_path = tmp_path

    def download(self, url, quality, output_path, platform, download_thumbnail=False):
        self.calls.append(url)
        outcome = self.outcomes.get(url.split("=")[-1], "ok")
        if outcome == "interrupt":
            raise KeyboardInterrupt
        if outcome == "ok":
            f = self.tmp_path / f"{len(self.calls)}.mp4"
            f.write_bytes(b"x")
            return DownloadResult(success=True, file_path=f, title="t")
        return DownloadResult(success=False, error_message=f"{outcome}\nmás detalle")


def _entries(n):
    return [PlaylistEntry(i, f"{i:011d}", f"Video {i}") for i in range(1, n + 1)]


@pytest.fixture
def pd(db, console, tmp_path):
    def make(outcomes=None):
        return PlaylistDownloader(FakeDownloader(db, outcomes or {}, tmp_path), console)
    return make


def test_fetch_info_marks_unavailable(pd, monkeypatch):
    monkeypatch.setattr(yt_dlp, "YoutubeDL", FakeYDL)
    FakeYDL.error = None
    FakeYDL.data = {"title": "Mi Lista", "entries": [
        {"id": VID, "title": "Ok"},
        {"id": "zzzzzzzzzzz", "title": "[Private video]"},
        {"id": "yyyyyyyyyyy", "title": "[Deleted video]"},
        None,
        {"id": "bad", "title": "Id roto"},
    ]}
    info = pd().fetch_info("https://www.youtube.com/playlist?list=PLabc")
    assert info.title == "Mi Lista" and len(info.entries) == 5
    assert [e.skip_reason is None for e in info.entries] == [True, False, False, False, False]
    assert len(info.downloadable) == 1
    assert FakeYDL.opts["extract_flat"] == "in_playlist"


def test_fetch_info_truncates(pd, monkeypatch):
    monkeypatch.setattr(yt_dlp, "YoutubeDL", FakeYDL)
    FakeYDL.error = None
    FakeYDL.data = {"title": "Grande", "entries": [
        {"id": f"{i:011d}", "title": f"v{i}"} for i in range(pl.MAX_PLAYLIST_ITEMS + 1)
    ]}
    info = pd().fetch_info("https://www.youtube.com/playlist?list=PLabc")
    assert info.truncated and len(info.entries) == pl.MAX_PLAYLIST_ITEMS


def test_fetch_info_errors(pd, monkeypatch):
    monkeypatch.setattr(yt_dlp, "YoutubeDL", FakeYDL)
    FakeYDL.error = yt_dlp.utils.DownloadError("playlist privada")
    assert pd().fetch_info("https://www.youtube.com/playlist?list=PLabc") is None
    assert pd().fetch_info("https://example.com/x") is None


def test_one_failure_does_not_stop_the_rest(pd, tmp_path):
    entries = _entries(3)
    d = pd({entries[1].video_id: "HTTP 403"})
    summary = d.download_entries(entries, Quality.AUDIO, tmp_path)
    assert [o.status for o in summary.outcomes] == ["success", "failed", "success"]
    assert summary.failed[0].message == "HTTP 403"
    assert len(d.downloader.calls) == 3


def test_skips_unavailable_and_already_downloaded(pd, db, tmp_path):
    entries = _entries(3)
    entries[0].skip_reason = "video privado o eliminado"
    existing = tmp_path / "old.mp4"
    existing.write_bytes(b"x")
    db.add_download(DownloadRecord(
        id=None, date="2026-01-01", platform="YouTube", title="t",
        url=build_video_url(entries[1].video_id), format="mp4",
        file_path=str(existing), duration=1, status="success",
    ))
    d = pd()
    summary = d.download_entries(entries, Quality.AUDIO, tmp_path)
    assert [o.status for o in summary.outcomes] == ["skipped", "skipped", "success"]
    assert summary.skipped[1].message == "ya descargado"
    assert len(d.downloader.calls) == 1


def test_stops_after_consecutive_failures(pd, tmp_path):
    entries = _entries(pl.MAX_CONSECUTIVE_FAILURES + 3)
    outcomes = {e.video_id: "HTTP 429" for e in entries}
    d = pd(outcomes)
    summary = d.download_entries(entries, Quality.AUDIO, tmp_path)
    assert summary.stopped_by_failures
    assert len(summary.failed) == pl.MAX_CONSECUTIVE_FAILURES
    assert len(summary.aborted) == 3
    assert len(d.downloader.calls) == pl.MAX_CONSECUTIVE_FAILURES


def test_success_resets_failure_counter(pd, tmp_path):
    entries = _entries(pl.MAX_CONSECUTIVE_FAILURES * 2)
    outcomes = {e.video_id: "boom" for e in entries}
    outcomes[entries[pl.MAX_CONSECUTIVE_FAILURES - 1].video_id] = "ok"
    summary = pd(outcomes).download_entries(entries, Quality.AUDIO, tmp_path)
    assert len(summary.succeeded) == 1
    assert summary.stopped_by_failures  # segunda racha completa


def test_keyboard_interrupt_returns_partial_summary(pd, tmp_path):
    entries = _entries(4)
    summary = pd({entries[2].video_id: "interrupt"}).download_entries(entries, Quality.AUDIO, tmp_path)
    assert summary.interrupted
    assert [o.status for o in summary.outcomes] == ["success", "success", "aborted", "aborted"]


def test_callback_error_does_not_stop_list(pd, tmp_path):
    seen = []

    def cb(result):
        seen.append(result.file_path)
        raise OSError("disco lleno")

    summary = pd().download_entries(_entries(2), Quality.AUDIO, tmp_path, on_success=cb)
    assert len(summary.succeeded) == 2 and len(seen) == 2


def test_output_dir_stays_inside_base(pd, tmp_path):
    info = pl.PlaylistInfo("PLx", "../../escape", [])
    out = pd().output_dir_for(info, tmp_path)
    assert out.resolve().is_relative_to(tmp_path.resolve())
