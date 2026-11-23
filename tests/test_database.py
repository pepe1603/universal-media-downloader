from src.storage.database import DownloadRecord, DownloadStatus


def _record(**kw) -> DownloadRecord:
    base = dict(
        id=None, date="2026-01-01", platform="youtube", title="Song",
        url="https://youtu.be/x", format="mp3", file_path="/tmp/x.mp3",
        duration=60, status=DownloadStatus.SUCCESS.value,
    )
    base.update(kw)
    return DownloadRecord(**base)


def test_add_and_get_by_id(db):
    rid = db.add_download(_record(title="Hello", artist="Me"))
    got = db.get_download_by_id(rid)
    assert got.title == "Hello" and got.artist == "Me"
    assert db.get_download_by_id(9999) is None


def test_find_successful_download(db):
    db.add_download(_record(url="https://x/1", status=DownloadStatus.FAILED.value))
    assert db.find_successful_download("https://x/1") is None
    rid = db.add_download(_record(url="https://x/1"))
    assert db.find_successful_download("https://x/1").id == rid
    assert db.find_successful_download("https://x/other") is None


def test_recent_and_total(db):
    for i in range(3):
        db.add_download(_record(title=f"t{i}"))
    assert db.get_total_downloads() == 3
    assert len(db.get_recent_downloads(limit=2)) == 2


def test_by_platform(db):
    db.add_download(_record(platform="youtube"))
    db.add_download(_record(platform="youtube"))
    db.add_download(_record(platform="tiktok"))
    assert db.get_downloads_by_platform() == {"youtube": 2, "tiktok": 1}


def test_delete(db):
    rid = db.add_download(_record())
    assert db.delete_download(rid) is True
    assert db.get_total_downloads() == 0


def test_failed_downloads_lifecycle(db):
    db.add_download(_record(status=DownloadStatus.FAILED.value, error_message="boom"))
    db.add_download(_record())
    assert len(db.get_failed_downloads()) == 1
    assert db.delete_failed_downloads() == 1
    assert db.get_failed_downloads() == []
    assert db.get_total_downloads() == 1


def test_settings_roundtrip(db):
    assert db.get_setting("k") is None
    assert db.set_setting("k", "v") is True
    assert db.set_setting("k", "v2") is True
    assert db.get_setting("k") == "v2"
    assert db.get_all_settings() == {"k": "v2"}
    assert db.delete_setting("k") is True
    assert db.get_setting("k") is None


def test_sql_injection_is_inert(db):
    db.add_download(_record(title="x'); DROP TABLE downloads;--"))
    assert db.get_total_downloads() == 1
