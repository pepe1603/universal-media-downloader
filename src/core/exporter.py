"""
Módulo de exportación de historial.
Exporta el historial de descargas a diferentes formatos.
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from rich.console import Console

from src.storage.database import DownloadRecord


class HistoryExporter:
    """Exportador de historial de descargas."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    def export_to_txt(
        self,
        records: List[DownloadRecord],
        output_path: Path
    ) -> bool:
        """
        Exportar historial a archivo TXT.
        
        Args:
            records: Lista de registros
            output_path: Ruta del archivo de salida
            
        Returns:
            True si fue exitoso
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("RESUMEN DE DESCARGAS - Universal Media Downloader\n")
                f.write("=" * 60 + "\n")
                f.write(f"Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total de descargas: {len(records)}\n")
                f.write("=" * 60 + "\n\n")
                
                for i, record in enumerate(records, 1):
                    f.write(f"[{i}] {record.title}\n")
                    f.write(f"    Plataforma: {record.platform}\n")
                    f.write(f"    Artista: {record.artist or 'Desconocido'}\n")
                    f.write(f"    Formato: {record.format}\n")
                    f.write(f"    Fecha: {record.date}\n")
                    f.write(f"    Duración: {self._format_duration(record.duration)}\n")
                    f.write(f"    URL: {record.url}\n")
                    f.write(f"    Archivo: {record.file_path}\n")
                    f.write("\n")
                
                f.write("=" * 60 + "\n")
                f.write("Fin del reporte\n")
            
            return True
        
        except Exception as e:
            self.console.print(f"[red]Error al exportar a TXT: {e}[/red]")
            return False
    
    def export_to_markdown(
        self,
        records: List[DownloadRecord],
        output_path: Path
    ) -> bool:
        """
        Exportar historial a archivo Markdown.
        
        Args:
            records: Lista de registros
            output_path: Ruta del archivo de salida
            
        Returns:
            True si fue exitoso
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# Resumen de Descargas\n\n")
                f.write(f"**Fecha de exportación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
                f.write(f"**Total de descargas:** {len(records)}\n\n")
                f.write("---\n\n")
                
                for i, record in enumerate(records, 1):
                    f.write(f"## {i}. {record.title}\n\n")
                    f.write(f"- **Plataforma:** {record.platform}\n")
                    f.write(f"- **Artista:** {record.artist or 'Desconocido'}\n")
                    f.write(f"- **Formato:** {record.format}\n")
                    f.write(f"- **Fecha:** {record.date}\n")
                    f.write(f"- **Duración:** {self._format_duration(record.duration)}\n")
                    f.write(f"- **URL:** [{record.url}]({record.url})\n")
                    f.write(f"- **Archivo:** `{record.file_path}`\n\n")
                
                f.write("---\n\n")
                f.write("*Generado por Universal Media Downloader*\n")
            
            return True
        
        except Exception as e:
            self.console.print(f"[red]Error al exportar a Markdown: {e}[/red]")
            return False
    
    def export_to_json(
        self,
        records: List[DownloadRecord],
        output_path: Path
    ) -> bool:
        """
        Exportar historial a archivo JSON.
        
        Args:
            records: Lista de registros
            output_path: Ruta del archivo de salida
            
        Returns:
            True si fue exitoso
        """
        try:
            data = {
                "export_date": datetime.now().isoformat(),
                "total_downloads": len(records),
                "downloads": []
            }
            
            for record in records:
                data["downloads"].append({
                    "id": record.id,
                    "date": record.date,
                    "platform": record.platform,
                    "title": record.title,
                    "url": record.url,
                    "format": record.format,
                    "file_path": record.file_path,
                    "duration": record.duration,
                    "status": record.status,
                    "artist": record.artist,
                    "quality": record.quality
                })
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            self.console.print(f"[red]Error al exportar a JSON: {e}[/red]")
            return False
    
    def _format_duration(self, seconds: Optional[int]) -> str:
        """Formatear duración en segundos a formato MM:SS."""
        if seconds is None:
            return "Desconocido"
        
        seconds = int(seconds)
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
