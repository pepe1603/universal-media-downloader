"""
Detector de plataformas multimedia.
Analiza URLs para identificar la plataforma de origen.
"""

from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse


class Platform(Enum):
    """Plataformas soportadas."""
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    UNKNOWN = "unknown"


@dataclass
class PlatformInfo:
    """Información de una plataforma detectada."""
    platform: Platform
    name: str
    url: str
    valid: bool
    message: str = ""


class PlatformDetector:
    """Detector de plataformas multimedia."""

    # Patrones de URLs soportadas
    PATTERNS = {
        Platform.YOUTUBE: {
            "domains": ["youtube.com", "youtu.be", "m.youtube.com", "www.youtube.com"],
            "name": "YouTube"
        },
        Platform.FACEBOOK: {
            "domains": ["facebook.com", "fb.watch", "m.facebook.com", "www.facebook.com", "fb.com"],
            "name": "Facebook"
        },
        Platform.INSTAGRAM: {
            "domains": ["instagram.com", "www.instagram.com", "instagr.am"],
            "name": "Instagram"
        },
        Platform.TIKTOK: {
            "domains": ["tiktok.com", "www.tiktok.com", "vm.tiktok.com", "vt.tiktok.com"],
            "name": "TikTok"
        }
    }

    @classmethod
    def detect(cls, url: str) -> PlatformInfo:
        """
        Detectar plataforma desde una URL.

        Args:
            url: URL a analizar

        Returns:
            PlatformInfo con información de la plataforma detectada
        """
        if not url or not url.strip():
            return PlatformInfo(
                platform=Platform.UNKNOWN,
                name="Desconocido",
                url=url,
                valid=False,
                message="URL vacía"
            )

        hostname = cls._extract_hostname(url)

        # Buscar coincidencias exactas de dominio o subdominio
        for platform, config in cls.PATTERNS.items():
            for domain in config["domains"]:
                if hostname == domain or hostname.endswith(f".{domain}"):
                    return PlatformInfo(
                        platform=platform,
                        name=config["name"],
                        url=url,
                        valid=True,
                        message=f"Plataforma detectada: {config['name']}"
                    )

        return PlatformInfo(
            platform=Platform.UNKNOWN,
            name="Desconocido",
            url=url,
            valid=False,
            message="Plataforma no soportada"
        )

    @staticmethod
    def _extract_hostname(url: str) -> str:
        """Extraer el hostname en minúsculas de una URL (con o sin esquema)."""
        url_clean = url.strip().lower()
        if "://" not in url_clean:
            url_clean = f"//{url_clean}"
        try:
            return urlparse(url_clean).hostname or ""
        except ValueError:
            return ""

    @classmethod
    def get_supported_platforms(cls) -> list[str]:
        """Obtener lista de plataformas soportadas."""
        return [config["name"] for config in cls.PATTERNS.values()]

