"""
Detector de plataformas multimedia.
Analiza URLs para identificar la plataforma de origen.
"""

from typing import Optional
from dataclasses import dataclass
from enum import Enum


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
        
        url_clean = url.strip().lower()
        
        # Buscar coincidencias
        for platform, config in cls.PATTERNS.items():
            for domain in config["domains"]:
                if domain in url_clean:
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
    
    @classmethod
    def get_supported_platforms(cls) -> list[str]:
        """Obtener lista de plataformas soportadas."""
        return [config["name"] for config in cls.PATTERNS.values()]

