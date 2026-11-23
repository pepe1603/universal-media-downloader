from types import SimpleNamespace

import pytest
import yt_dlp
from src.core import downloader as dl
from src.core.dependencies import DependencyStatus
from src.core.downloader import MediaDownloader, Quality


class FakeYDL:
    info = {"title": "T", "duration": 10, "uploader": "U", "upload_date": "20260102"}
    error = None

    def __init__(self, opts):
        self.opts = opts

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def extract_info(self, url, download=True):
        if self.error:
            raise self.error
        return self.info

    def prepare_filename(self, info):
        return "/tmp/x/T.webm"


@pytest.fixture
def mdl(tmp_path, console, db, monkeypatch):
    monkeypatch.setattr(
        dl.DependencyChecker, "check_ffmpeg",
        staticmethod(lambda: DependencyStatus(name="FFmpeg", installed=True)),
    )
    monkeypatch.setattr(yt_dlp, "YoutubeDL", FakeYDL)
    FakeYDL.error = None
    return MediaDownloader(tmp_path, console=console, database=db)


def test_download_success_audio(mdl, tmp_path, db):
    res = mdl.download("https://youtu.be/x", Quality.AUDIO, tmp_path, "YouTube")
    assert res.success and res.file_path.suffix == ".mp3"
    assert res.upload_date == "2026-01-02"
    assert db.get_total_downloads() == 1


def test_download_success_video(mdl, tmp_path):
    res = mdl.download("https://youtu.be/x", Quality.MAXIMUM, tmp_path, "YouTube")
    assert res.success and res.file_path.suffix == ".webm"


def test_download_without_ffmpeg(mdl, tmp_path, monkeypatch):
    monkeypatch.setattr(
        dl.DependencyChecker, "check_ffmpeg",
        staticmethod(lambda: DependencyStatus(name="FFmpeg", installed=False, message="no")),
    )
    res = mdl.download("u", Quality.AUDIO, tmp_path, "YouTube")
    assert not res.success and "FFmpeg" in res.error_message


def test_download_error_403_records_failure(mdl, tmp_path, db):
    FakeYDL.error = yt_dlp.utils.DownloadError("HTTP Error 403: Forbidden")
    res = mdl.download("u", Quality.AUDIO, tmp_path, "YouTube")
    assert not res.success and "403" in res.error_message
    assert len(db.get_failed_downloads()) == 1


def test_download_auth_error_suggests_cookies(mdl, tmp_path):
    FakeYDL.error = yt_dlp.utils.DownloadError("Sign in to confirm")
    res = mdl.download("u", Quality.AUDIO, tmp_path, "YouTube")
    assert "cookies" in res.error_message.lower()


def test_download_unexpected_error(mdl, tmp_path):
    FakeYDL.error = RuntimeError("boom")
    res = mdl.download("u", Quality.AUDIO, tmp_path, "YouTube")
    assert not res.success and "boom" in res.error_message


def test_get_video_info(mdl):
    assert mdl.get_video_info("u")["title"] == "T"
    FakeYDL.error = RuntimeError("x")
    assert mdl.get_video_info("u") is None


def test_progress_hook_updates():
    calls = []
    progress = SimpleNamespace(
        tasks={0: SimpleNamespace(description="Conectando")},
        update=lambda tid, **kw: calls.append(kw),
    )
    MediaDownloader._progress_hook(
        {"status": "downloading", "downloaded_bytes": 5, "total_bytes": 10}, progress, 0
    )
    MediaDownloader._progress_hook({"status": "finished"}, progress, 0)
    assert calls[-1]["description"].endswith("Procesando...")
    assert any(c.get("total") == 10 for c in calls)


def test_ydl_opts_per_quality(mdl, tmp_path):
    for q in Quality:
        opts = mdl._get_ydl_opts(q, tmp_path, "YouTube", download_thumbnail=True)
        assert "outtmpl" in opts
