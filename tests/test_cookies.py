import os
import stat

import pytest

from src.core.cookies import CookieManager


@pytest.fixture
def manager(tmp_path, console, db):
    return CookieManager(tmp_path / "base", console=console, database=db)


def test_cookie_path_is_inside_cookies_dir(manager):
    path = manager.get_cookie_path("YouTube")
    assert path.name == "youtube.txt"
    assert path.parent == manager.cookies_dir


@pytest.mark.parametrize("bad", ["../evil", "a/b", "..", "", "x" * 64, "a b", "a\\b"])
def test_cookie_path_rejects_traversal(manager, bad):
    with pytest.raises(ValueError):
        manager.get_cookie_path(bad)


def test_validate_missing_empty_and_invalid(manager, tmp_path):
    assert not manager.validate_cookie_file(tmp_path / "nope.txt").valid
    empty = tmp_path / "empty.txt"
    empty.write_text("")
    assert not manager.validate_cookie_file(empty).valid
    comments = tmp_path / "c.txt"
    comments.write_text("# only comment\n")
    assert not manager.validate_cookie_file(comments).valid
    bad = tmp_path / "bad.txt"
    bad.write_text("not\tnetscape\n")
    assert not manager.validate_cookie_file(bad).valid
    assert not manager.validate_cookie_file(tmp_path).valid


def test_validate_ok(manager, netscape_cookies):
    res = manager.validate_cookie_file(netscape_cookies)
    assert res.valid and "1 cookies" in res.message


def test_configure_file_and_clear(manager, netscape_cookies):
    assert manager.has_cookies("youtube") is False
    assert manager.configure_file("youtube", netscape_cookies) is True
    assert manager.has_cookies("youtube") is True
    assert manager.is_active() is True
    assert "cookiefile" in manager.get_ydl_opts("youtube")
    manager.clear("youtube")
    assert manager.has_cookies("youtube") is False
    assert manager.get_ydl_opts("youtube") == {}


@pytest.mark.skipif(os.name == "nt", reason="permisos POSIX")
def test_configured_cookie_file_is_private(manager, netscape_cookies):
    manager.configure_file("tiktok", netscape_cookies)
    mode = stat.S_IMODE(manager.get_cookie_path("tiktok").stat().st_mode)
    assert mode == 0o600


def test_configure_invalid_file_rejected(manager, tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_text("garbage")
    assert manager.configure_file("youtube", bad) is False


def test_clear_all(manager, netscape_cookies):
    manager.configure_file("youtube", netscape_cookies)
    manager.configure_file("tiktok", netscape_cookies)
    assert manager.clear() is True
    assert manager.is_active() is False
