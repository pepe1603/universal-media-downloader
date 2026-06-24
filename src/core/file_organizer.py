"""
Módulo de organización de archivos.
Gestiona el movimiento de archivos a carpetas específicas en Android.
"""

import shutil
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum

from rich.console import Console


class DestinationFolder(Enum):
    """Carpetas de destino para organización."""
    DOWNLOADS = "downloads"
    MUSIC = "music"
    VIDEOS = "videos"
    
    @property
    def description(self) -> str:
        descriptions = {
            DestinationFolder.DOWNLOADS: "Descargas (Archivos generales)",
            DestinationFolder.MUSIC: "Música (Reproductores de música)",
            DestinationFolder.VIDEOS: "Videos (Galería de videos)"
        }
        return descriptions[self]
    
    @property
    def extensions(self) -> List[str]:
        """Extensiones de archivo que van a esta carpeta."""
        ext_map = {
            DestinationFolder.DOWNLOADS: ['.mp4', '.mkv', '.webm', '.mp3', '.m4a', '.flac', '.ogg', '.wav'],
            DestinationFolder.MUSIC: ['.mp3', '.m4a', '.flac', '.ogg', '.wav', '.aac'],
            DestinationFolder.VIDEOS: ['.mp4', '.mkv', '.webm', '.avi', '.mov']
        }
        return ext_map[self]


@dataclass
class MoveResult:
    """Resultado de mover un archivo."""
    success: bool
    source: Path
    destination: Optional[Path] = None
    error_message: Optional[str] = None


class FileOrganizer:
    """Organizador de archivos para dispositivos móviles."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    def move_to_folder(
        self,
        file_path: Path,
        destination: DestinationFolder,
        base_path: Path
    ) -> MoveResult:
        """
        Mover archivo a carpeta específica.
        
        Args:
            file_path: Ruta del archivo a mover
            destination: Carpeta de destino
            base_path: Ruta base del dispositivo
            
        Returns:
            MoveResult con el resultado
        """
        try:
            if not file_path.exists():
                return MoveResult(
                    success=False,
                    source=file_path,
                    error_message=f"Archivo no encontrado: {file_path}"
                )
            
            # Determinar ruta de destino
            if destination == DestinationFolder.DOWNLOADS:
                dest_dir = base_path / "Download" / "UniversalDownloader"
            elif destination == DestinationFolder.MUSIC:
                dest_dir = base_path / "Music" / "UniversalDownloader"
            elif destination == DestinationFolder.VIDEOS:
                dest_dir = base_path / "Movies" / "UniversalDownloader"
            else:
                dest_dir = base_path / "UniversalDownloader"
            
            # Crear directorio si no existe
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Mover archivo
            dest_path = dest_dir / file_path.name
            
            # Si ya existe, agregar sufijo
            if dest_path.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                counter = 1
                while dest_path.exists():
                    dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
            
            shutil.move(str(file_path), str(dest_path))
            
            return MoveResult(
                success=True,
                source=file_path,
                destination=dest_path
            )
        
        except Exception as e:
            return MoveResult(
                success=False,
                source=file_path,
                error_message=str(e)
            )
    
    def list_downloaded_files(self, base_path: Path) -> List[Path]:
        """Listar archivos descargados en el directorio base."""
        if not base_path.exists():
            return []
        
        files = []
        for ext in ['.mp4', '.mp3', '.m4a', '.flac', '.ogg', '.wav', '.mkv', '.webm']:
            files.extend(base_path.rglob(f"*{ext}"))
        
        return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)
    
    def auto_organize(self, base_path: Path) -> List[MoveResult]:
        """
        Organizar automáticamente archivos por tipo.
        
        Args:
            base_path: Ruta base del dispositivo
            
        Returns:
            Lista de resultados de movimiento
        """
        results = []
        files = self.list_downloaded_files(base_path)
        
        for file_path in files:
            ext = file_path.suffix.lower()
            
            # Determinar destino según extensión
            if ext in DestinationFolder.MUSIC.extensions:
                destination = DestinationFolder.MUSIC
            elif ext in DestinationFolder.VIDEOS.extensions:
                destination = DestinationFolder.VIDEOS
            else:
                destination = DestinationFolder.DOWNLOADS
            
            result = self.move_to_folder(file_path, destination, base_path.parent)
            results.append(result)
        
        return results
