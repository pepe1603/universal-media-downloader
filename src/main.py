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

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich import box
import typer

from src.platforms.detector import PlatformDetector, Platform
from src.core.downloader import MediaDownloader, Quality
from src.core.dependencies import DependencyChecker

# Crear aplicación Typer
app = typer.Typer(help="Universal Media Downloader - Descarga contenido multimedia de múltiples plataformas")
console = Console()

# Constantes
APP_NAME = "Universal Media Downloader"
VERSION = "0.1.0"


class DeviceConfig:
    """Configuración según el dispositivo."""
    
    def __init__(self, device_type: str):
        self.device_type = device_type
        self.base_path = self._get_base_path()
    
    def _get_base_path(self) -> Path:
        """Obtener ruta base según el dispositivo."""
        if self.device_type == "movil":
            # Termux/Android
            return Path("/storage/emulated/0/UniversalDownloader")
        else:
            # Windows/Linux/macOS
            return Path.home() / "UniversalDownloader"
    
    def get_platform_path(self, platform: str) -> Path:
        """Obtener ruta para una plataforma específica."""
        return self.base_path / platform


class UniversalDownloader:
    """Clase principal del Universal Media Downloader."""
    
    def __init__(self):
        self.console = Console()
        self.device_config: Optional[DeviceConfig] = None
        self.downloader = MediaDownloader(self.console)
        self.username = "Usuario"
        self.running = True
    
    def show_banner(self):
        """Mostrar banner de la aplicación."""
        banner = f"""
[bold cyan]{APP_NAME}[/bold cyan]
[green]Versión {VERSION}[/green]
[dim]Usuario: {self.username} | Dispositivo: {self.device_config.device_type if self.device_config else 'No configurado'}[/dim]
        """
        self.console.print(Panel(banner, box=box.DOUBLE_EDGE, expand=False))
    
    def select_device(self):
        """Seleccionar tipo de dispositivo."""
        self.console.print("\n[bold]Seleccione tipo de dispositivo:[/bold]")
        
        table = Table(box=box.SIMPLE)
        table.add_column("Opción", style="cyan", justify="center")
        table.add_column("Dispositivo", style="green")
        
        table.add_row("1", "Móvil (Termux/Android)")
        table.add_row("2", "Computadora (Windows/Linux/macOS)")
        
        self.console.print(table)
        
        choice = IntPrompt.ask(
            "\nSeleccione una opción",
            choices=["1", "2"],
            default="2"
        )
        
        device_type = "movil" if choice == 1 else "desktop"
        self.device_config = DeviceConfig(device_type)
        
        # Crear directorio base si no existe
        self.device_config.base_path.mkdir(parents=True, exist_ok=True)
        
        self.console.print(f"\n[green]✓[/green] Dispositivo configurado: [bold]{device_type}[/bold]")
        self.console.print(f"[dim]Ruta base: {self.device_config.base_path}[/dim]")
    
    def show_main_menu(self):
        """Mostrar menú principal."""
        self.console.print("\n[bold]═══ MENÚ PRINCIPAL ═══[/bold]\n")
        
        table = Table(box=box.ROUNDED, show_header=False)
        table.add_column("Opción", style="cyan", justify="center", width=8)
        table.add_column("Acción", style="white")
        
        table.add_row("1", "📥 Descargar contenido")
        table.add_row("2", "📋 Consultar descargas")
        table.add_row("3", "📤 Exportar/Mover archivos")
        table.add_row("4", "📊 Resumen reciente")
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
        
        # Detectar plataforma usando el módulo
        platform_info = PlatformDetector.detect(url)
        
        if platform_info.valid:
            self.console.print(f"[green]✓[/green] {platform_info.message}")
            
            # Seleccionar calidad
            self.console.print("\n[bold]Seleccione calidad:[/bold]")
            table = Table(box=box.SIMPLE)
            table.add_column("Opción", style="cyan", justify="center")
            table.add_column("Calidad", style="white")
            
            table.add_row("1", "Máxima disponible")
            table.add_row("2", "Recomendada (720p)")
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
            
            # Realizar descarga
            self.console.print(f"\n[cyan]Iniciando descarga...[/cyan]")
            result = self.downloader.download(
                url=url,
                quality=quality,
                output_path=self.device_config.base_path,
                platform=platform_info.name
            )
            
            if result.success:
                self.console.print(f"\n[green]✓ Descarga completada exitosamente[/green]")
                self.console.print(f"[dim]Título: {result.title}[/dim]")
                self.console.print(f"[dim]Ubicación: {result.file_path}[/dim]")
                if result.duration:
                    minutes = result.duration // 60
                    seconds = result.duration % 60
                    self.console.print(f"[dim]Duración: {minutes}:{seconds:02d}[/dim]")
            else:
                self.console.print(f"\n[red]✗ Error en la descarga[/red]")
                self.console.print(f"[red]{result.error_message}[/red]")
        
        else:
            self.console.print(f"[red]✗[/red] {platform_info.message}")
    
    def view_downloads(self):
        """Ver historial de descargas."""
        self.console.print("\n[bold cyan]═══ CONSULTAR DESCARGAS ═══[/bold cyan]\n")
        self.console.print("[yellow]⚠ Funcionalidad en desarrollo (Fase 3)[/yellow]")
    
    def export_files(self):
        """Exportar o mover archivos."""
        self.console.print("\n[bold cyan]═══ EXPORTAR/MOVER ARCHIVOS ═══[/bold cyan]\n")
        self.console.print("[yellow]⚠ Funcionalidad en desarrollo[/yellow]")
    
    def recent_summary(self):
        """Mostrar resumen reciente."""
        self.console.print("\n[bold cyan]═══ RESUMEN RECIENTE ═══[/bold cyan]\n")
        self.console.print("[yellow]⚠ Funcionalidad en desarrollo (Fase 3)[/yellow]")
    
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
        
        # Mostrar estado de dependencias
        DependencyChecker.show_status(self.console)
        
        self.console.print("[yellow]⚠ Más opciones en desarrollo[/yellow]")
    
    def run(self):
        """Ejecutar aplicación principal."""
        # Seleccionar dispositivo al inicio
        self.select_device()
        
        # Bucle principal
        while self.running:
            self.show_banner()
            self.show_main_menu()
            
            choice = Prompt.ask(
                "\nSeleccione una opción",
                choices=["0", "1", "2", "3", "4", "5", "6"],
                default="0"
            )
            
            if choice == "1":
                self.download_menu()
            elif choice == "2":
                self.view_downloads()
            elif choice == "3":
                self.export_files()
            elif choice == "4":
                self.recent_summary()
            elif choice == "5":
                self.change_user()
            elif choice == "6":
                self.settings()
            elif choice == "0":
                self.console.print("\n[green]¡Hasta luego![/green]\n")
                self.running = False
            
            # Pausa antes de volver al menú
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
        sys.exit(1)


if __name__ == "__main__":
    main()

