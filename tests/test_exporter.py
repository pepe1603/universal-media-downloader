import json

import pytest

from src.core.exporter import HistoryExporter
from src.storage.database import DownloadRecord


@pytest.fixture
def records():
    return [
        DownloadRecord(
            id=1, date="2026-01-01", platform="youtube", title="Canción ñ",
            url="https://youtu.be/x", format="mp3", file_path="/tmp/a.mp3",
            duration=125, status="success", artist="Yo",
        ),
        DownloadRecord(
            id=2, date="2026-01-02", platform="tiktok", title="Clip",
            url="https://tiktok.com/x", format="mp4", file_path="/tmp/b.mp4",
            duration=None, status="success",
        ),
    ]


@pytest.mark.parametrize("method,ext", [
    ("export_to_txt", "txt"), ("export_to_markdown", "md"), ("export_to_json", "json"),
])
def test_export_creates_file(console, records, tmp_path, method, ext):
    out = tmp_path / f"h.{ext}"
    assert getattr(HistoryExporter(console), method)(records, out) is True
    assert "Canción ñ" in out.read_text(encoding="utf-8") or ext == "json"


def test_export_json_is_valid(console, records, tmp_path):
    out = tmp_path / "h.json"
    HistoryExporter(console).export_to_json(records, out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["total_downloads"] == 2


@pytest.mark.parametrize("method", ["export_to_txt", "export_to_markdown", "export_to_json"])
def test_export_failure_returns_false(console, records, tmp_path, method):
    bad = tmp_path / "missing_dir" / "x.out"
    assert getattr(HistoryExporter(console), method)(records, bad) is False
