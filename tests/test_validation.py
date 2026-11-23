from pathlib import Path

import pytest
from src.ui.validation import normalize_url, normalize_user_path, normalize_username


@pytest.mark.parametrize("raw,expected", [
    ("https://youtu.be/x", "https://youtu.be/x"),
    ("  youtube.com/watch?v=1  ", "https://youtube.com/watch?v=1"),
    ("'https://tiktok.com/x'", "https://tiktok.com/x"),
])
def test_url_ok(raw, expected):
    assert normalize_url(raw) == expected


@pytest.mark.parametrize("raw", ["", "  ", "ftp://x.com/a", "javascript:alert(1)", "a b.com", "localhost", "file:///etc/passwd"])
def test_url_invalid(raw):
    assert normalize_url(raw) is None


@pytest.mark.parametrize("raw", ["Ana", " José Luis ", "user_1", "a.b-c"])
def test_username_ok(raw):
    assert normalize_username(raw) == raw.strip()


@pytest.mark.parametrize("raw", ["", "  ", "../x", "a/b", "a\\b", "x" * 33, "a\nb"])
def test_username_invalid(raw):
    assert normalize_username(raw) is None


def test_user_path(tmp_path):
    assert normalize_user_path("") is None
    assert normalize_user_path(f'"{tmp_path}"') == tmp_path.resolve()
    assert normalize_user_path("~") == Path.home().resolve()
