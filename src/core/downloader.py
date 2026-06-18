"""
Módulo de descarga de contenido multimedia.
Utiliza yt-dlp para descargar videos y audio de múltiples plataformas.
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum

import yt_dlp
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from src.core.dependencies import DependencyChecker


class Quality(Enum):
    """Calidades de descarga disponibles."""
    MAXIMUM = "maximum"
    RECOMMENDED = "recommended"
    AUDIO = "audio"


@dataclass
class DownloadResult:
    """Resultado de una descarga."""
    success: bool
    file_path: Optional[Path] = None
    title: Optional[str] = None
    duration: Optional[int] = None
    error_message: Optional[str] = None


class MediaDownloader:
    """Descargador de contenido multimedia usando yt-dlp."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    def _check_dependencies(self) -> bool:
        """
        Verificar que las dependencias necesarias estén instaladas.
        
        Returns:
            True si todas las dependencias están disponibles
        """
        ffmpeg_status = DependencyChecker.check_ffmpeg()
        
        if not ffmpeg_status.installed:
            self.console.print(f"\n[red]✗ {ffmpeg_status.message}[/red]")
            self.console.print("\n[yellow]Para instalar FFmpeg en Windows:[/yellow]")
            self.console.print("[dim]  winget install FFmpeg[/dim]")
            self.console.print("\n[yellow]O descarga manualmente desde:[/yellow]")
            self.console.print("[dim]  https://www.gyan.dev/ffmpeg/builds/[/dim]")
            return False
        
        return True
    
    def _get_ydl_opts(self, quality: Quality, output_path: Path) -> dict:
        """
        Obtener opciones de yt-dlp según la calidad.
        
        Args:
            quality: Calidad de descarga
            output_path: Ruta de salida
            
        Returns:
            Diccionario con opciones de yt-dlp
        """
        output_template = str(output_path / "%(title)s.%(ext)s")
        
        if quality == Quality.MAXIMUM:
            # Máxima calidad disponible
            return {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': output_template,
                'merge_output_format': 'mp4',
                'quiet': True,
                'no_warnings': True,
            }
        
        elif quality == Quality.RECOMMENDED:
            # Calidad recomendada (720p)
            return {
                'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
                'outtmpl': output_template,
                'merge_output_format': 'mp4',
                'quiet': True,
                'no_warnings': True,
            }
        
        elif quality == Quality.AUDIO:
            # Solo audio (MP3)
            return {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
        
        return {}
    
    def download(
        self,
        url: str,
        quality: Quality,
        output_path: Path,
        platform: str
    ) -> DownloadResult:
        """
        Descargar contenido desde una URL.
        
        Args:
            url: URL del contenido
            quality: Calidad de descarga
            output_path: Ruta base de salida
            platform: Nombre de la plataforma
            
        Returns:
            DownloadResult con el resultado de la descarga
        """
        # Verificar dependencias antes de descargar
        if not self._check_dependencies():
            return DownloadResult(
                success=False,
                error_message="FFmpeg no está instalado"
            )
        
        try:
            # Crear directorio de la plataforma
            platform_path = output_path / platform.lower()
            platform_path.mkdir(parents=True, exist_ok=True)
            
            # Obtener opciones de yt-dlp
            ydl_opts = self._get_ydl_opts(quality, platform_path)
            
            # Descargar con barra de progreso
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console,
            ) as progress:
                task = progress.add_task("[cyan]Descargando...", total=None)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Obtener información del video
                    info = ydl.extract_info(url, download=True)
                    
                    if info:
                        title = info.get('title', 'Sin título')
                        duration = info.get('duration', 0)
                        
                        # Construir ruta del archivo descargado
                        ext = 'mp3' if quality == Quality.AUDIO else 'mp4'
                        filename = f"{title}.{ext}"
                        # Limpiar nombre de archivo
                        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
                        file_path = platform_path / filename
                        
                        progress.update(task, completed=100, description="[green]✓ Descarga completada")
                        
                        return DownloadResult(
                            success=True,
                            file_path=file_path,
                            title=title,
                            duration=duration
                        )
            
            return DownloadResult(
                success=False,
                error_message="No se pudo obtener información del video"
            )
        
        except yt_dlp.utils.DownloadError as e:
            return DownloadResult(
                success=False,
                error_message=f"Error de descarga: {str(e)}"
            )
        except Exception as e:
            return DownloadResult(
                success=False,
                error_message=f"Error inesperado: {str(e)}"
            )
    
    def get_video_info(self, url: str) -> Optional[dict]:
        """
        Obtener información de un video sin descargarlo.
        
        Args:
            url: URL del video
            
        Returns:
            Diccionario con información del video o None
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        
        except Exception as e:
            self.console.print(f"[red]Error al obtener información: {e}[/red]")
            return None
