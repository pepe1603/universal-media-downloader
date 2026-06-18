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
    artist: Optional[str] = None
    duration: Optional[int] = None
    upload_date: Optional[str] = None
    thumbnail_path: Optional[Path] = None
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
    
    def _get_ydl_opts(
        self,
        quality: Quality,
        output_path: Path,
        download_thumbnail: bool = False
    ) -> dict:
        """
        Obtener opciones de yt-dlp según la calidad.
        
        Args:
            quality: Calidad de descarga
            output_path: Ruta de salida
            download_thumbnail: Si debe descargar la miniatura
            
        Returns:
            Diccionario con opciones de yt-dlp
        """
        output_template = str(output_path / "%(title)s.%(ext)s")
        
        opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
        }
        
        # Descargar miniatura si se solicita
        if download_thumbnail:
            opts['writethumbnail'] = True
            # Convertir miniatura a JPG para compatibilidad con metadatos ID3
            opts['postprocessors'] = opts.get('postprocessors', [])
            opts['postprocessors'].append({
                'key': 'ModifyChapters',
                'remove_chapters_patterns': [],
            })
            # Agregar postprocessor para convertir thumbnails
            if 'postprocessors' not in opts:
                opts['postprocessors'] = []
            opts['postprocessors'].append({
                'key': 'FFmpegThumbnailsConvertor',
                'format': 'jpg',
                'when': 'before_dl',
            })
        
        if quality == Quality.MAXIMUM:
            opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            })
        
        elif quality == Quality.RECOMMENDED:
            opts.update({
                'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
                'merge_output_format': 'mp4',
            })
        
        elif quality == Quality.AUDIO:
            audio_pp = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            
            # Si también queremos miniatura, agregar conversión antes
            if download_thumbnail:
                opts['postprocessors'] = [{
                    'key': 'FFmpegThumbnailsConvertor',
                    'format': 'jpg',
                    'when': 'before_dl',
                }] + audio_pp
            else:
                opts['postprocessors'] = audio_pp
        
        return opts
    
    def download(
        self,
        url: str,
        quality: Quality,
        output_path: Path,
        platform: str,
        download_thumbnail: bool = False
    ) -> DownloadResult:
        """
        Descargar contenido desde una URL.
        
        Args:
            url: URL del contenido
            quality: Calidad de descarga
            output_path: Ruta base de salida
            platform: Nombre de la plataforma
            download_thumbnail: Si debe descargar la miniatura
            
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
            ydl_opts = self._get_ydl_opts(quality, platform_path, download_thumbnail)
            
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
                        artist = info.get('uploader', info.get('channel', 'Desconocido'))
                        upload_date = info.get('upload_date', '')
                        
                        # Formatear fecha
                        formatted_date = ""
                        if upload_date and len(upload_date) >= 8:
                            formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                        
                        # Obtener la ruta real del archivo descargado
                        ext = 'mp3' if quality == Quality.AUDIO else 'mp4'
                        filename = ydl.prepare_filename(info)
                        
                        # Si es audio, cambiar la extensión a mp3
                        if quality == Quality.AUDIO:
                            filename = Path(filename).with_suffix('.mp3')
                        else:
                            filename = Path(filename)
                        
                        file_path = filename
                        
                        # Buscar miniatura descargada (ahora en JPG)
                        thumbnail_path = None
                        if download_thumbnail:
                            stem = file_path.stem
                            # Buscar primero JPG (el que convertimos)
                            for thumb_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                                potential_thumb = platform_path / f"{stem}{thumb_ext}"
                                if potential_thumb.exists():
                                    thumbnail_path = potential_thumb
                                    break
                        
                        progress.update(task, completed=100, description="[green]✓ Descarga completada")
                        
                        return DownloadResult(
                            success=True,
                            file_path=file_path,
                            title=title,
                            artist=artist,
                            duration=duration,
                            upload_date=formatted_date,
                            thumbnail_path=thumbnail_path
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
