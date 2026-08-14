"""
Módulo de detección de entorno.
Detecta automáticamente si se ejecuta en Termux, Windows, Linux o macOS.
"""

import os
import platform
import shutil
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum


class EnvironmentType(Enum):
    """Tipos de entorno detectados."""
    TERMUX = "termux"
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNKNOWN = "unknown"


@dataclass
class EnvironmentInfo:
    """Información del entorno detectado."""
    env_type: EnvironmentType
    is_mobile: bool
    home_path: Path
    downloads_path: Optional[Path]
    music_path: Optional[Path]
    videos_path: Optional[Path]
    has_storage_permission: bool
    display_name: str
    available_browsers: List[str] = field(default_factory=list)


class EnvironmentDetector:
    """Detector automático de entorno de ejecución."""
    
    @classmethod
    def detect(cls) -> EnvironmentInfo:
        """
        Detectar automáticamente el entorno de ejecución.
        
        Returns:
            EnvironmentInfo con información del entorno
        """
        # Detectar Termux primero (más específico)
        if cls._is_termux():
            return cls._get_termux_info()
        
        # Detectar sistema operativo
        system = platform.system().lower()
        
        if system == "windows":
            return cls._get_windows_info()
        elif system == "darwin":
            return cls._get_macos_info()
        elif system == "linux":
            return cls._get_linux_info()
        
        return cls._get_unknown_info()
    
    @classmethod
    def _is_termux(cls) -> bool:
        """Detectar si estamos en Termux o un terminal Android (UserLAnd, proot, etc.)."""
        # Verificar variable de entorno específica de Termux
        if "TERMUX_VERSION" in os.environ:
            return True
        
        # Verificar ruta específica de Termux
        if Path("/data/data/com.termux").exists():
            return True
        
        # Verificar comando termux-info
        if shutil.which("termux-info"):
            return True
        
        # Entornos Android alternativos (UserLAnd, proot, Android nativo, etc.)
        # Toda Android expone ANDROID_ROOT/ANDROID_DATA; PREFIX identifica Termux.
        if "ANDROID_ROOT" in os.environ or "ANDROID_DATA" in os.environ:
            return True
        
        return False
    
    @classmethod
    def _get_termux_info(cls) -> EnvironmentInfo:
        """Obtener información del entorno Termux."""
        home = Path.home()
        
        # Verificar permiso de almacenamiento
        storage_path = Path("/storage/emulated/0")
        has_permission = storage_path.exists() and os.access(storage_path, os.W_OK)
        
        if has_permission:
            downloads = storage_path / "Download" / "UniversalDownloader"
            music = storage_path / "Music" / "UniversalDownloader"
            videos = storage_path / "Movies" / "UniversalDownloader"
        else:
            downloads = None
            music = None
            videos = None
        
        return EnvironmentInfo(
            env_type=EnvironmentType.TERMUX,
            is_mobile=True,
            home_path=home,
            downloads_path=downloads,
            music_path=music,
            videos_path=videos,
            has_storage_permission=has_permission,
            display_name="Móvil (Termux/Android)"
        )
    
    @classmethod
    def _get_windows_info(cls) -> EnvironmentInfo:
        """Obtener información del entorno Windows."""
        home = Path.home()
        downloads = home / "UniversalDownloader"
        
        return EnvironmentInfo(
            env_type=EnvironmentType.WINDOWS,
            is_mobile=False,
            home_path=home,
            downloads_path=downloads,
            music_path=downloads,
            videos_path=downloads,
            has_storage_permission=True,
            display_name="Computadora (Windows)",
            available_browsers=cls._detect_browsers()
        )
    
    @classmethod
    def _get_linux_info(cls) -> EnvironmentInfo:
        """Obtener información del entorno Linux."""
        home = Path.home()
        downloads = home / "UniversalDownloader"
        
        return EnvironmentInfo(
            env_type=EnvironmentType.LINUX,
            is_mobile=False,
            home_path=home,
            downloads_path=downloads,
            music_path=downloads,
            videos_path=downloads,
            has_storage_permission=True,
            display_name="Computadora (Linux)",
            available_browsers=cls._detect_browsers()
        )
    
    @classmethod
    def _get_macos_info(cls) -> EnvironmentInfo:
        """Obtener información del entorno macOS."""
        home = Path.home()
        downloads = home / "UniversalDownloader"
        
        return EnvironmentInfo(
            env_type=EnvironmentType.MACOS,
            is_mobile=False,
            home_path=home,
            downloads_path=downloads,
            music_path=downloads,
            videos_path=downloads,
            has_storage_permission=True,
            display_name="Computadora (macOS)",
            available_browsers=cls._detect_browsers()
        )
    
    @classmethod
    def _get_unknown_info(cls) -> EnvironmentInfo:
        """Obtener información de entorno desconocido."""
        home = Path.home()
        downloads = home / "UniversalDownloader"
        
        return EnvironmentInfo(
            env_type=EnvironmentType.UNKNOWN,
            is_mobile=False,
            home_path=home,
            downloads_path=downloads,
            music_path=downloads,
            videos_path=downloads,
            has_storage_permission=True,
            display_name="Sistema desconocido",
            available_browsers=cls._detect_browsers()
        )
    
    # Rutas de instalación estándar de navegadores en Windows (no suelen estar en PATH)
    _WINDOWS_BROWSER_PATHS = {
        "chrome": [
            r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe",
            r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe",
            r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe",
        ],
        "firefox": [
            r"%PROGRAMFILES%\Mozilla Firefox\firefox.exe",
            r"%PROGRAMFILES(X86)%\Mozilla Firefox\firefox.exe",
            r"%LOCALAPPDATA%\Mozilla Firefox\firefox.exe",
        ],
        "edge": [
            r"%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe",
            r"%PROGRAMFILES%\Microsoft\Edge\Application\msedge.exe",
            r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe",
        ],
        "opera": [
            r"%LOCALAPPDATA%\Programs\Opera\opera.exe",
            r"%PROGRAMFILES%\Opera\opera.exe",
            r"%PROGRAMFILES(X86)%\Opera\opera.exe",
        ],
        "brave": [
            r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"%PROGRAMFILES%\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"%PROGRAMFILES(X86)%\BraveSoftware\Brave-Browser\Application\brave.exe",
        ],
        "chromium": [
            r"%LOCALAPPDATA%\Chromium\Application\chromium.exe",
            r"%PROGRAMFILES%\Chromium\Application\chromium.exe",
            r"%PROGRAMFILES(X86)%\Chromium\Application\chromium.exe",
        ],
    }

    @classmethod
    def _detect_browsers(cls) -> List[str]:
        """
        Detectar navegadores instalados en el sistema.
        
        En Windows se verifican además las rutas estándar de instalación, ya
        que Chrome/Edge/Opera normalmente no están en el PATH.
        
        Returns:
            Lista de nombres de navegadores detectados
        """
        system = platform.system().lower()
        browsers_found = []

        browser_checks = {
            "chrome": {
                "windows": ["chrome"],
                "linux": ["google-chrome", "google-chrome-stable"],
                "darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
            },
            "firefox": {
                "windows": ["firefox"],
                "linux": ["firefox"],
                "darwin": ["/Applications/Firefox.app/Contents/MacOS/firefox"],
            },
            "edge": {
                "windows": ["msedge"],
                "linux": ["microsoft-edge", "microsoft-edge-stable"],
                "darwin": ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"],
            },
            "opera": {
                "windows": ["opera"],
                "linux": ["opera"],
                "darwin": ["/Applications/Opera.app/Contents/MacOS/Opera"],
            },
            "brave": {
                "windows": ["brave"],
                "linux": ["brave-browser", "brave"],
                "darwin": ["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"],
            },
            "chromium": {
                "windows": ["chromium"],
                "linux": ["chromium", "chromium-browser"],
                "darwin": ["/Applications/Chromium.app/Contents/MacOS/Chromium"],
            },
        }

        for browser_name, executables in browser_checks.items():
            exe_list = executables.get(system, [])
            found = False
            for exe in exe_list:
                if system == "darwin":
                    if Path(exe).exists():
                        found = True
                        break
                else:
                    if shutil.which(exe):
                        found = True
                        break
            if not found and system == "windows":
                known_paths = cls._WINDOWS_BROWSER_PATHS.get(browser_name, [])
                for path in known_paths:
                    expanded = os.path.expandvars(path)
                    if expanded and Path(expanded).exists():
                        found = True
                        break
            if found:
                browsers_found.append(browser_name)

        return browsers_found
    
    @classmethod
    def show_info(cls, info: EnvironmentInfo, console) -> None:
        """Mostrar información del entorno detectado."""
        console.print(f"\n[bold cyan]Entorno detectado:[/bold cyan]")
        console.print(f"  Tipo: [green]{info.display_name}[/green]")
        console.print(f"  Home: [dim]{info.home_path}[/dim]")
        
        if info.is_mobile:
            if info.has_storage_permission:
                console.print(f"  [green]✓ Permiso de almacenamiento: Concedido[/green]")
                console.print(f"  Descargas: [dim]{info.downloads_path}[/dim]")
                console.print(f"  Música: [dim]{info.music_path}[/dim]")
                console.print(f"  Videos: [dim]{info.videos_path}[/dim]")
            else:
                console.print(f"  [red]✗ Permiso de almacenamiento: No concedido[/red]")
                console.print(f"  [yellow]Ejecuta: termux-setup-storage[/yellow]")
        
        if info.available_browsers:
            console.print(f"  Navegadores detectados: [dim]{', '.join(info.available_browsers)}[/dim]")
