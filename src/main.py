#!/usr/bin/env python3
"""
Universal Media Downloader (UMD)
CLI multiplataforma para descargar contenido multimedia.
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path para permitir imports absolutos
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from typing import Optional
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich import box
import typer

from src.platforms.detector import PlatformDetector, Platform
from src.core.downloader import MediaDownloader, Quality
from src.core.dependencies import DependencyChecker
from src.core.converter import AudioConverter, AudioFormat
from src.core.metadata import MetadataHandler, AudioMetadata
from src.core.exporter import HistoryExporter
from src.core.environment import EnvironmentDetector, EnvironmentInfo, EnvironmentType
from src.core.file_organizer import FileOrganizer, DestinationFolder
from src.storage.database import Database, DownloadRecord

# Crear aplicación Typer
app = typer.Typer(help="Universal Media Downloader - Descarga contenido multimedia de múltiples plataformas")
console = Console()

# Constantes
APP_NAME = "Universal Media Downloader"
VERSION = "0.4.0"


class UniversalDownloader:
    """Clase principal del Universal Media Downloader."""
    
    def __init__(self):
        self.console = Console()
        self.env_info: Optional[EnvironmentInfo] = None
        self.base_path: Optional[Path] = None
        self.database = Database()
        self.downloader = MediaDownloader(self.console, self.database)
        self.converter = AudioConverter(self.console)
        self.metadata_handler = MetadataHandler(self.console)
        self.exporter = HistoryExporter(self.console)
        self.file_organizer = FileOrganizer(self.console)
        self.username = "Usuario"
        self.running = True
    
    def show_banner(self):
        """Mostrar banner de la aplicación."""
        total_downloads = self.database.get_total_downloads()
        device_name = self.env_info.display_name if self.env_info else "No detectado"
        
        banner = f"""
[bold cyan]{APP_NAME}[/bold cyan]
[green]Versión {VERSION}[/green]
[dim]Usuario: {self.username} | Dispositivo: {device_name}[/dim]
[dim]Total de descargas: {total_downloads}[/dim]
        """
        self.console.print(Panel(banner, box=box.DOUBLE_EDGE, expand=False))
    
    def detect_environment(self):
        """Detectar automáticamente el entorno de ejecución."""
        self.console.print("\n[cyan]Detectando entorno...[/cyan]")
        
        self.env_info = EnvironmentDetector.detect()
        
        # Mostrar información del entorno
        EnvironmentDetector.show_info(self.env_info, self.console)
        
        # Si es Termux y no tiene permisos, advertir
        if self.env_info.env_type == EnvironmentType.TERMUX:
            if not self.env_info.has_storage_permission:
                self.console.print("\n[bold yellow]⚠ IMPORTANTE:[/bold yellow]")
                self.console.print("[yellow]Para usar el almacenamiento compartido en Termux:[/yellow]")
                self.console.print("[dim]1. Ejecuta: termux-setup-storage[/dim]")
                self.console.print("[dim]2. Acepta los permisos cuando se soliciten[/dim]")
                self.console.print("[dim]3. Reinicia la aplicación[/dim]")
                
                if not Confirm.ask("\n¿Deseas continuar sin permisos de almacenamiento?", default=True):
                    sys.exit(0)
        
        # Configurar ruta base
        if self.env_info.is_mobile and self.env_info.has_storage_permission:
            # En móvil, usar carpeta Download como base
            self.base_path = self.env_info.downloads_path
        else:
            # En desktop, usar UniversalDownloader en home
            self.base_path = self.env_info.downloads_path
        
        # Crear directorio base
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.console.print(f"\n[green]✓[/green] Entorno configurado: [bold]{self.env_info.display_name}[/bold]")
        self.console.print(f"[dim]Ruta base: {self.base_path}[/dim]")
    
    def show_main_menu(self):
        """Mostrar menú principal."""
        self.console.print("\n[bold]═══ MENÚ PRINCIPAL ═══[/bold]\n")
        
        table = Table(box=box.ROUNDED, show_header=False)
        table.add_column("Opción", style="cyan", justify="center", width=8)
        table.add_column("Acción", style="white")
        
        table.add_row("1", "📥 Descargar contenido")
        table.add_row("2", "📋 Consultar descargas")
        table.add_row("3", "📤 Exportar historial")
        table.add_row("4", "📊 Resumen reciente")
        
        # Solo mostrar opción de organizar si es móvil
        if self.env_info and self.env_info.is_mobile:
            table.add_row("5", "📁 Organizar archivos")
            table.add_row("6", "👤 Cambiar usuario")
            table.add_row("7", "⚙️  Configuración")
            table.add_row("0", "🚪 Salir")
        else:
            table.add_row("5", "👤 Cambiar usuario")
            table.add_row("6", "⚙️  Configuración")
            table.add_row("0", "🚪 Salir")
        
        self.console.print(table)
    
    def download_menu(self):
        """Menú de descarga."""
        self.console.print("\n[bold cyan]═══ DESCARGAR CONTENIDO ═══[/bold cyan]\n")
        
        url = Prompt.ask("Ingrese la URL del contenido")
        
        if not url:
            self.console.print("[yellow]⚠ URL no válida[/yellow]")
            return
        
        # Detectar plataforma
        platform_info = PlatformDetector.detect(url)
        
        if platform_info.valid:
            self.console.print(f"[green]✓[/green] {platform_info.message}")
            
            # Seleccionar calidad
            self.console.print("\n[bold]Seleccione calidad:[/bold]")
            table = Table(box=box.SIMPLE)
            table.add_column("Opción", style="cyan", justify="center")
            table.add_column("Calidad", style="white")
            
            table.add_row("1", "Máxima disponible (Video)")
            table.add_row("2", "Recomendada 720p (Video)")
            table.add_row("3", "Convertir a audio")
            table.add_row("4", "Regresar")
            
            self.console.print(table)
            
            choice = IntPrompt.ask(
                "\nSeleccione una opción",
                choices=["1", "2", "3", "4"],
                default="2"
            )
            
            if choice == 4:
                return
            
            # Mapear elección a calidad
            quality_map = {
                1: Quality.MAXIMUM,
                2: Quality.RECOMMENDED,
                3: Quality.AUDIO
            }
            
            quality = quality_map.get(choice, Quality.RECOMMENDED)
            
            # Si es audio, preguntar formato
            audio_format = None
            if choice == 3:
                audio_format = self._select_audio_format()
                if audio_format is None:
                    return
            
            # Realizar descarga
            self.console.print(f"\n[cyan]Iniciando descarga...[/cyan]")
            
            download_thumbnail = (choice == 3)
            
            result = self.downloader.download(
                url=url,
                quality=quality,
                output_path=self.base_path,
                platform=platform_info.name,
                download_thumbnail=download_thumbnail
            )
            
            if result.success:
                self.console.print(f"\n[green]✓ Descarga completada exitosamente[/green]")
                self.console.print(f"[dim]Título: {result.title}[/dim]")
                self.console.print(f"[dim]Artista: {result.artist}[/dim]")
                self.console.print(f"[dim]Ubicación: {result.file_path}[/dim]")
                if result.duration:
                    minutes = result.duration // 60
                    seconds = result.duration % 60
                    self.console.print(f"[dim]Duración: {minutes}:{seconds:02d}[/dim]")
                if result.record_id:
                    self.console.print(f"[dim]ID de registro: {result.record_id}[/dim]")
                
                # Si es audio, procesar metadatos
                if choice == 3 and audio_format and result.file_path:
                    self._process_audio_with_metadata(result, audio_format)
                
                # Preguntar si desea organizar el archivo (solo en móvil)
                if self.env_info and self.env_info.is_mobile:
                    self._ask_organize_file(result.file_path)
            else:
                self.console.print(f"\n[red]✗ Error en la descarga[/red]")
                self.console.print(f"[red]{result.error_message}[/red]")
        
        else:
            self.console.print(f"[red]✗[/red] {platform_info.message}")
    
    def _ask_organize_file(self, file_path: Path):
        """Preguntar si desea organizar el archivo descargado."""
        if not self.env_info or not self.env_info.is_mobile:
            return
        
        self.console.print(f"\n[cyan]¿Deseas mover el archivo a una carpeta específica?[/cyan]")
        
        table = Table(box=box.SIMPLE)
        table.add_column("Opción", style="cyan", justify="center")
        table.add_column("Carpeta", style="white")
        
        table.add_row("1", f"📁 Descargas ({self.env_info.downloads_path})")
        table.add_row("2", f"🎵 Música ({self.env_info.music_path})")
        table.add_row("3", f"🎬 Videos ({self.env_info.videos_path})")
        table.add_row("4", "❌ No mover")
        
        self.console.print(table)
        
        choice = IntPrompt.ask(
            "\nSeleccione una opción",
            choices=["1", "2", "3", "4"],
            default="4"
        )
        # Convertir a string para usar como clave del diccionario
        choice_str = str(choice)
        
        if choice_str == "4":
            return
        
        dest_map = {
            "1": DestinationFolder.DOWNLOADS,
            "2": DestinationFolder.MUSIC,
            "3": DestinationFolder.VIDEOS
        }
        
        destination = dest_map[choice_str]  # Usar choice_str en lugar de choice
        
        # La ruta base para organizer es /storage/emulated/0
        storage_base = Path("/storage/emulated/0")
        
        result = self.file_organizer.move_to_folder(file_path, destination, storage_base)
        
        if result.success:
            self.console.print(f"\n[green]✓ Archivo movido exitosamente[/green]")
            self.console.print(f"[dim]Nueva ubicación: {result.destination}[/dim]")
        else:
            self.console.print(f"\n[red]✗ Error al mover archivo: {result.error_message}[/red]")
    
    def _select_audio_format(self) -> Optional[AudioFormat]:
        """Seleccionar formato de audio."""
        self.console.print("\n[bold]Seleccione formato de audio:[/bold]")
        
        table = Table(box=box.SIMPLE)
        table.add_column("Opción", style="cyan", justify="center")
        table.add_column("Formato", style="white")
        
        formats = list(AudioFormat)
        for i, fmt in enumerate(formats, 1):
            table.add_row(str(i), fmt.description)
        
        table.add_row(str(len(formats) + 1), "Regresar")
        
        self.console.print(table)
        
        choice = IntPrompt.ask(
            "\nSeleccione una opción",
            choices=[str(i) for i in range(1, len(formats) + 2)],
            default="1"
        )
        
        if choice == len(formats) + 1:
            return None
        
        return formats[choice - 1]
    
    def _process_audio_with_metadata(self, result, target_format: AudioFormat):
        """Procesar audio: convertir formato e incrustar metadatos."""
        self.console.print(f"\n[cyan]Procesando audio...[/cyan]")
        
        current_path = result.file_path
        final_path = current_path
        
        if current_path.suffix.lower() != f".{target_format.value}":
            self.console.print(f"[dim]Convirtiendo a {target_format.description}...[/dim]")
            
            conversion_result = self.converter.convert(
                input_path=current_path,
                output_format=target_format
            )
            
            if conversion_result.success:
                final_path = conversion_result.output_path
                self.console.print(f"[green]✓[/green] Conversión completada")
                
                if current_path != final_path and current_path.exists():
                    current_path.unlink()
            else:
                self.console.print(f"[red]✗ Error en conversión: {conversion_result.error_message}[/red]")
                return
        
        # Incrustar metadatos
        self.console.print(f"[dim]Incrustando metadatos y carátula...[/dim]")
        
        metadata = AudioMetadata(
            title=result.title or "Sin título",
            artist=result.artist or "Desconocido",
            album="Single",
            date=result.upload_date,
            cover_path=result.thumbnail_path
        )
        
        if self.metadata_handler.embed_metadata(final_path, metadata):
            self.console.print(f"[green]✓[/green] Metadatos incrustados exitosamente")
            self.console.print(f"[dim]Formato final: {final_path.name}[/dim]")
            
            # Actualizar ruta en el resultado
            result.file_path = final_path
            
            if result.thumbnail_path and result.thumbnail_path.exists():
                try:
                    result.thumbnail_path.unlink()
                    self.console.print(f"[dim]✓ Miniatura temporal eliminada[/dim]")
                except Exception as e:
                    self.console.print(f"[yellow]⚠ No se pudo eliminar miniatura: {e}[/yellow]")
        else:
            self.console.print(f"[yellow]⚠ No se pudieron incrustar metadatos[/yellow]")
    
    def view_downloads(self):
        """Ver historial de descargas."""
        self.console.print("\n[bold cyan]═══ CONSULTAR DESCARGAS ═══[/bold cyan]\n")
        
        table = Table(box=box.SIMPLE)
        table.add_column("Opción", style="cyan", justify="center")
        table.add_column("Acción", style="white")
        
        table.add_row("1", "Ver últimas 20 descargas")
        table.add_row("2", "Buscar por plataforma")
        table.add_row("3", "Buscar por fecha")
        table.add_row("4", "Buscar por nombre")
        table.add_row("5", "Regresar")
        
        self.console.print(table)
        
        choice = IntPrompt.ask(
            "\nSeleccione una opción",
            choices=["1", "2", "3", "4", "5"],
            default="1"
        )
        
        if choice == 1:
            self._show_recent_downloads()
        elif choice == 2:
            self._search_by_platform()
        elif choice == 3:
            self._search_by_date()
        elif choice == 4:
            self._search_by_name()
    
    def _show_recent_downloads(self, limit: int = 20):
        """Mostrar descargas recientes."""
        records = self.database.get_recent_downloads(limit)
        
        if not records:
            self.console.print("[yellow]No hay descargas registradas[/yellow]")
            return
        
        self._display_downloads_table(records)
    
    def _search_by_platform(self):
        """Buscar descargas por plataforma."""
        self.console.print("\n[bold]Plataformas disponibles:[/bold]")
        platforms = ["YouTube", "Facebook", "Instagram", "TikTok"]
        
        for i, platform in enumerate(platforms, 1):
            self.console.print(f"  {i}. {platform}")
        
        choice = IntPrompt.ask(
            "\nSeleccione una plataforma",
            choices=[str(i) for i in range(1, len(platforms) + 1)],
            default="1"
        )
        
        platform = platforms[choice - 1]
        records = self.database.search_downloads(platform=platform)
        
        if not records:
            self.console.print(f"[yellow]No hay descargas de {platform}[/yellow]")
            return
        
        self._display_downloads_table(records)
    
    def _search_by_date(self):
        """Buscar descargas por fecha."""
        self.console.print("\n[bold]Búsqueda por fecha:[/bold]")
        date_from = Prompt.ask("Desde (YYYY-MM-DD)", default="")
        date_to = Prompt.ask("Hasta (YYYY-MM-DD)", default="")
        
        records = self.database.search_downloads(
            date_from=date_from if date_from else None,
            date_to=date_to if date_to else None
        )
        
        if not records:
            self.console.print("[yellow]No se encontraron descargas en ese rango de fechas[/yellow]")
            return
        
        self._display_downloads_table(records)
    
    def _search_by_name(self):
        """Buscar descargas por nombre."""
        title = Prompt.ask("\nIngrese texto a buscar en el título")
        
        if not title:
            return
        
        records = self.database.search_downloads(title_contains=title)
        
        if not records:
            self.console.print(f"[yellow]No se encontraron descargas con '{title}'[/yellow]")
            return
        
        self._display_downloads_table(records)
    
    def _display_downloads_table(self, records: list):
        """Mostrar tabla de descargas."""
        table = Table(box=box.ROUNDED)
        table.add_column("ID", style="cyan", justify="center")
        table.add_column("Fecha", style="green")
        table.add_column("Plataforma", style="magenta")
        table.add_column("Título", style="white", max_width=40)
        table.add_column("Formato", style="yellow")
        table.add_column("Duración", style="blue", justify="right")
        
        for record in records:
            duration_str = self._format_duration(record.duration)
            title_short = record.title[:40] + "..." if len(record.title) > 40 else record.title
            
            table.add_row(
                str(record.id),
                record.date,
                record.platform,
                title_short,
                record.format,
                duration_str
            )
        
        self.console.print(f"\n[bold]Resultados ({len(records)} descargas):[/bold]\n")
        self.console.print(table)
    
    def _format_duration(self, seconds: Optional[int]) -> str:
        """Formatear duración."""
        if seconds is None:
            return "N/A"
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    
    def export_history(self):
        """Exportar historial de descargas."""
        self.console.print("\n[bold cyan]═══ EXPORTAR HISTORIAL ═══[/bold cyan]\n")
        
        records = self.database.get_recent_downloads(1000)
        
        if not records:
            self.console.print("[yellow]No hay descargas para exportar[/yellow]")
            return
        
        self.console.print(f"[dim]Total de descargas: {len(records)}[/dim]\n")
        
        table = Table(box=box.SIMPLE)
        table.add_column("Opción", style="cyan", justify="center")
        table.add_column("Formato", style="white")
        
        table.add_row("1", "TXT (Texto plano)")
        table.add_row("2", "Markdown (MD)")
        table.add_row("3", "JSON (Datos estructurados)")
        table.add_row("4", "Regresar")
        
        self.console.print(table)
        
        choice = IntPrompt.ask(
            "\nSeleccione un formato",
            choices=["1", "2", "3", "4"],
            default="1"
        )
        
        if choice == 4:
            return
        
        # Crear directorio de exportación
        export_dir = self.base_path.parent / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if choice == 1:
            output_path = export_dir / f"historial_{timestamp}.txt"
            success = self.exporter.export_to_txt(records, output_path)
        elif choice == 2:
            output_path = export_dir / f"historial_{timestamp}.md"
            success = self.exporter.export_to_markdown(records, output_path)
        elif choice == 3:
            output_path = export_dir / f"historial_{timestamp}.json"
            success = self.exporter.export_to_json(records, output_path)
        
        if success:
            self.console.print(f"\n[green]✓ Historial exportado exitosamente[/green]")
            self.console.print(f"[dim]Ubicación: {output_path}[/dim]")
        else:
            self.console.print(f"\n[red]✗ Error al exportar el historial[/red]")
    
    def organize_files_menu(self):
        """Menú de organización de archivos (solo móvil)."""
        if not self.env_info or not self.env_info.is_mobile:
            self.console.print("[yellow]Esta opción solo está disponible en dispositivos móviles[/yellow]")
            return
        
        self.console.print("\n[bold cyan]═══ ORGANIZAR ARCHIVOS ═══[/bold cyan]\n")
        
        table = Table(box=box.SIMPLE)
        table.add_column("Opción", style="cyan", justify="center")
        table.add_column("Acción", style="white")
        
        table.add_row("1", "Listar archivos descargados")
        table.add_row("2", "Organizar automáticamente (por tipo)")
        table.add_row("3", "Mover archivo específico")
        table.add_row("4", "Regresar")
        
        self.console.print(table)
        
        choice = IntPrompt.ask(
            "\nSeleccione una opción",
            choices=["1", "2", "3", "4"],
            default="1"
        )
        
        if choice == 1:
            self._list_downloaded_files()
        elif choice == 2:
            self._auto_organize_files()
        elif choice == 3:
            self._move_specific_file()
    
    def _list_downloaded_files(self):
        """Listar archivos descargados."""
        files = self.file_organizer.list_downloaded_files(self.base_path)
        
        if not files:
            self.console.print("[yellow]No hay archivos descargados[/yellow]")
            return
        
        self.console.print(f"\n[bold]Archivos descargados ({len(files)}):[/bold]\n")
        
        table = Table(box=box.ROUNDED)
        table.add_column("#", style="cyan", justify="center")
        table.add_column("Nombre", style="white", max_width=50)
        table.add_column("Tamaño", style="green", justify="right")
        table.add_column("Fecha", style="yellow")
        
        for i, file_path in enumerate(files[:20], 1):
            size_mb = file_path.stat().st_size / (1024 * 1024)
            date = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d')
            name = file_path.name[:50] + "..." if len(file_path.name) > 50 else file_path.name
            
            table.add_row(
                str(i),
                name,
                f"{size_mb:.2f} MB",
                date
            )
        
        self.console.print(table)
    
    def _auto_organize_files(self):
        """Organizar archivos automáticamente."""
        if not Confirm.ask("\n¿Organizar todos los archivos automáticamente?", default=False):
            return
        
        self.console.print("\n[cyan]Organizando archivos...[/cyan]")
        
        storage_base = Path("/storage/emulated/0")
        results = self.file_organizer.auto_organize(self.base_path)
        
        success_count = sum(1 for r in results if r.success)
        error_count = len(results) - success_count
        
        self.console.print(f"\n[green]✓ {success_count} archivos organizados[/green]")
        if error_count > 0:
            self.console.print(f"[red]✗ {error_count} errores[/red]")
    
    def _move_specific_file(self):
        """Mover archivo específico."""
        files = self.file_organizer.list_downloaded_files(self.base_path)
        
        if not files:
            self.console.print("[yellow]No hay archivos para mover[/yellow]")
            return
        
        self.console.print("\n[bold]Archivos disponibles:[/bold]\n")
        
        for i, file_path in enumerate(files[:20], 1):
            self.console.print(f"  {i}. {file_path.name}")
        
        choice = IntPrompt.ask(
            "\nSeleccione un archivo",
            choices=[str(i) for i in range(1, min(len(files), 20) + 1)]
        )
        
        file_path = files[choice - 1]
        self._ask_organize_file(file_path)
    
    def recent_summary(self):
        """Mostrar resumen reciente."""
        self.console.print("\n[bold cyan]═══ RESUMEN RECIENTE ═══[/bold cyan]\n")
        
        total = self.database.get_total_downloads()
        by_platform = self.database.get_downloads_by_platform()
        recent = self.database.get_recent_downloads(5)
        
        self.console.print(f"[bold]Total de descargas:[/bold] {total}\n")
        
        if by_platform:
            self.console.print("[bold]Descargas por plataforma:[/bold]")
            table = Table(box=box.SIMPLE)
            table.add_column("Plataforma", style="cyan")
            table.add_column("Cantidad", style="green", justify="right")
            
            for platform, count in by_platform.items():
                table.add_row(platform, str(count))
            
            self.console.print(table)
            self.console.print()
        
        if recent:
            self.console.print("[bold]Últimas 5 descargas:[/bold]")
            self._display_downloads_table(recent)
        else:
            self.console.print("[yellow]No hay descargas recientes[/yellow]")
    
    def change_user(self):
        """Cambiar usuario."""
        self.console.print("\n[bold cyan]═══ CAMBIAR USUARIO ═══[/bold cyan]\n")
        new_username = Prompt.ask("Ingrese el nuevo nombre de usuario")
        if new_username:
            self.username = new_username
            self.console.print(f"[green]✓[/green] Usuario cambiado a: [bold]{self.username}[/bold]")
    
    def settings(self):
        """Configuración."""
        self.console.print("\n[bold cyan]═══ CONFIGURACIÓN ═══[/bold cyan]\n")
        
        # Información del entorno
        self.console.print("[bold]Entorno:[/bold]")
        EnvironmentDetector.show_info(self.env_info, self.console)
        self.console.print()
        
        # Dependencias
        self.console.print("[bold]Dependencias:[/bold]")
        DependencyChecker.show_status(self.console)
        
        try:
            import mutagen
            self.console.print(f"[green]✓[/green] [bold]mutagen[/bold]")
            self.console.print(f"  [dim]Versión: {mutagen.version_tuple[0]}.{mutagen.version_tuple[1]}.{mutagen.version_tuple[2]}[/dim]")
        except ImportError:
            self.console.print(f"[red]✗[/red] [bold]mutagen[/bold]")
            self.console.print(f"  [red]No está instalado[/red]")
        
        # Base de datos
        self.console.print(f"\n[bold]Base de datos:[/bold]")
        self.console.print(f"  [dim]Ubicación: {self.database.db_path}[/dim]")
        self.console.print(f"  [dim]Total de registros: {self.database.get_total_downloads()}[/dim]")
        
        # Instrucciones específicas para Termux
        if self.env_info and self.env_info.env_type == EnvironmentType.TERMUX:
            self.console.print(f"\n[bold cyan]Termux - Comandos útiles:[/bold cyan]")
            self.console.print(f"  [dim]• Mantener despierto: termux-wake-lock[/dim]")
            self.console.print(f"  [dim]• Configurar almacenamiento: termux-setup-storage[/dim]")
            self.console.print(f"  [dim]• Instalar FFmpeg: pkg install ffmpeg[/dim]")
            self.console.print(f"  [dim]• Instalar Python: pkg install python[/dim]")
        
        self.console.print("\n[yellow]⚠ Más opciones en desarrollo[/yellow]")
    
    def run(self):
        """Ejecutar aplicación principal."""
        # Detectar entorno automáticamente
        self.detect_environment()
        
        # Bucle principal
        while self.running:
            self.show_banner()
            self.show_main_menu()
            
            # Determinar opciones válidas según el entorno
            if self.env_info and self.env_info.is_mobile:
                valid_choices = ["0", "1", "2", "3", "4", "5", "6", "7"]
            else:
                valid_choices = ["0", "1", "2", "3", "4", "5", "6"]
            
            choice = Prompt.ask(
                "\nSeleccione una opción",
                choices=valid_choices,
                default="0"
            )
            
            if choice == "1":
                self.download_menu()
            elif choice == "2":
                self.view_downloads()
            elif choice == "3":
                self.export_history()
            elif choice == "4":
                self.recent_summary()
            elif choice == "5":
                if self.env_info and self.env_info.is_mobile:
                    self.organize_files_menu()
                else:
                    self.change_user()
            elif choice == "6":
                if self.env_info and self.env_info.is_mobile:
                    self.change_user()
                else:
                    self.settings()
            elif choice == "7":
                if self.env_info and self.env_info.is_mobile:
                    self.settings()
            elif choice == "0":
                self.console.print("\n[green]¡Hasta luego![/green]\n")
                self.running = False
            
            if self.running:
                Prompt.ask("\nPresione [bold]Enter[/bold] para continuar")


def main():
    """Punto de entrada principal."""
    try:
        downloader = UniversalDownloader()
        downloader.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Aplicación interrumpida por el usuario[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
