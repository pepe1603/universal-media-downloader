"""
Verificación de dependencias del sistema.
Comprueba que las herramientas necesarias estén instaladas.
"""

import shutil
import subprocess
from typing import Optional
from dataclasses import dataclass

from rich.console import Console


@dataclass
class DependencyStatus:
    """Estado de una dependencia."""
    name: str
    installed: bool
    version: Optional[str] = None
    path: Optional[str] = None
    message: str = ""


class DependencyChecker:
    """Verificador de dependencias del sistema."""
    
    @staticmethod
    def check_ffmpeg() -> DependencyStatus:
        """
        Verificar si FFmpeg está instalado.
        
        Returns:
            DependencyStatus con el estado de FFmpeg
        """
        ffmpeg_path = shutil.which("ffmpeg")
        
        if not ffmpeg_path:
            return DependencyStatus(
                name="FFmpeg",
                installed=False,
                message="FFmpeg no está instalado. Es necesario para combinar video/audio y convertir formatos."
            )
        
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Extraer versión de la primera línea
                first_line = result.stdout.split('\n')[0]
                version = first_line.split('version')[1].split()[0] if 'version' in first_line else "desconocida"
                
                return DependencyStatus(
                    name="FFmpeg",
                    installed=True,
                    version=version,
                    path=ffmpeg_path,
                    message="FFmpeg está instalado correctamente"
                )
        
        except Exception as e:
            return DependencyStatus(
                name="FFmpeg",
                installed=False,
                message=f"Error al verificar FFmpeg: {str(e)}"
            )
        
        return DependencyStatus(
            name="FFmpeg",
            installed=False,
            message="FFmpeg no está disponible"
        )
    
    @staticmethod
    def check_ytdlp() -> DependencyStatus:
        """
        Verificar si yt-dlp está instalado.
        
        Returns:
            DependencyStatus con el estado de yt-dlp
        """
        try:
            import yt_dlp
            version = yt_dlp.version.__version__
            
            return DependencyStatus(
                name="yt-dlp",
                installed=True,
                version=version,
                message="yt-dlp está instalado correctamente"
            )
        
        except ImportError:
            return DependencyStatus(
                name="yt-dlp",
                installed=False,
                message="yt-dlp no está instalado. Ejecuta: pip install yt-dlp"
            )
    
    @classmethod
    def check_all(cls, console: Optional[Console] = None) -> dict[str, DependencyStatus]:
        """
        Verificar todas las dependencias.
        
        Returns:
            Diccionario con el estado de cada dependencia
        """
        return {
            "ffmpeg": cls.check_ffmpeg(),
            "ytdlp": cls.check_ytdlp()
        }
    
    @classmethod
    def show_status(cls, console: Optional[Console] = None):
        """Mostrar estado de todas las dependencias."""
        if console is None:
            console = Console()
        
        console.print("\n[bold]Estado de dependencias:[/bold]\n")
        
        statuses = cls.check_all(console)
        
        for key, status in statuses.items():
            icon = "[green]✓[/green]" if status.installed else "[red]✗[/red]"
            console.print(f"{icon} [bold]{status.name}[/bold]")
            
            if status.installed:
                console.print(f"  [dim]Versión: {status.version}[/dim]")
                console.print(f"  [dim]Ruta: {status.path}[/dim]")
            else:
                console.print(f"  [red]{status.message}[/red]")
        
        console.print()

