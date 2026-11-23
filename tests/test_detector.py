import pytest

from src.platforms.detector import Platform, PlatformDetector


@pytest.mark.parametrize(
    "url,platform",
    [
        ("https://www.youtube.com/watch?v=abc", Platform.YOUTUBE),
        ("https://youtu.be/abc", Platform.YOUTUBE),
        ("youtube.com/watch?v=abc", Platform.YOUTUBE),
        ("https://music.youtube.com/watch?v=abc", Platform.YOUTUBE),
        ("https://fb.watch/xyz", Platform.FACEBOOK),
        ("https://www.instagram.com/reel/abc", Platform.INSTAGRAM),
        ("https://vm.tiktok.com/abc", Platform.TIKTOK),
        ("  HTTPS://WWW.TIKTOK.COM/@u/video/1  ", Platform.TIKTOK),
    ],
)
def test_detect_supported(url, platform):
    info = PlatformDetector.detect(url)
    assert info.valid is True
    assert info.platform is platform


@pytest.mark.parametrize(
    "url",
    [
        "",
        "   ",
        "https://example.com/video",
        "https://evil.com/?u=youtube.com",
        "https://youtube.com.evil.com/watch",
        "https://notyoutube.com/watch",
    ],
)
def test_detect_rejects_unsupported_or_spoofed(url):
    info = PlatformDetector.detect(url)
    assert info.valid is False
    assert info.platform is Platform.UNKNOWN


def test_supported_platforms_list():
    assert PlatformDetector.get_supported_platforms() == [
        "YouTube", "Facebook", "Instagram", "TikTok",
    ]
