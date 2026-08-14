"""
Módulo de gestión de cookies para contenido privado.
Soporta cookies desde archivo (cookies.txt) organizadas por plataforma.
"""

import shutil
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum

from rich.console import Console

from src.storage.database import Database


class Browser(Enum):
    """Navegadores soportados para extracción de cookies."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    OPERA = "opera"
    BRAVE = "brave"
    CHROMIUM = "chromium"


@dataclass
class CookieValidation:
    """Resultado de validación de cookies."""
    valid: bool
    message: str


class BrowserDetector:
    """Detecta navegadores instalados en el sistema."""

    _BROWSER_EXECUTABLES = {
        Browser.CHROME: {
            "windows": ["chrome"],
            "linux": ["google-chrome", "google-chrome-stable", "chrome"],
            "macos": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
        },
        Browser.FIREFOX: {
            "windows": ["firefox"],
            "linux": ["firefox"],
            "macos": ["/Applications/Firefox.app/Contents/MacOS/firefox"],
        },
        Browser.EDGE: {
            "windows": ["msedge"],
            "linux": ["microsoft-edge", "microsoft-edge-stable"],
            "macos": ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"],
        },
        Browser.OPERA: {
            "windows": ["opera"],
            "linux": ["opera"],
            "macos": ["/Applications/Opera.app/Contents/MacOS/Opera"],
        },
        Browser.BRAVE: {
            "windows": ["brave"],
            "linux": ["brave-browser", "brave"],
            "macos": ["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"],
        },
        Browser.CHROMIUM: {
            "windows": ["chromium"],
            "linux": ["chromium", "chromium-browser"],
            "macos": ["/Applications/Chromium.app/Contents/MacOS/Chromium"],
        },
    }

    @classmethod
    def detect_installed_browsers(cls, platform_system: str) -> List[Browser]:
        """
        Detectar navegadores instalados en el sistema.

        Args:
            platform_system: Sistema operativo (windows, linux, darwin)

        Returns:
            Lista de navegadores detectados
        """
        system_key = "windows" if platform_system == "Windows" else (
            "macos" if platform_system == "Darwin" else "linux"
        )

        installed = []

        for browser, executables in cls._BROWSER_EXECUTABLES.items():
            for exe in executables.get(system_key, []):
                if system_key == "macos":
                    if Path(exe).exists():
                        installed.append(browser)
                        break
                else:
                    if shutil.which(exe):
                        installed.append(browser)
                        break

        return installed


class CookieManager:
    """Gestor de cookies para autenticación con plataformas, organizadas por plataforma."""

    PLATFORMS = ["youtube", "instagram", "facebook", "tiktok"]

    def __init__(self, base_path: Path, console: Optional[Console] = None, database: Optional[Database] = None):
        self.console = console or Console()
        self.database = database or Database()
        self.cookies_dir = base_path / "cookies"
        self.cookies_dir.mkdir(parents=True, exist_ok=True)

    def get_cookie_path(self, platform: str) -> Path:
        """
        Obtener la ruta del archivo de cookies para una plataforma.

        Args:
            platform: Nombre de la plataforma (youtube, instagram, facebook, tiktok)

        Returns:
            Path al archivo de cookies
        """
        platform_lower = platform.lower()
        return self.cookies_dir / f"{platform_lower}.txt"

    def has_cookies(self, platform: str) -> bool:
        """
        Verificar si existen cookies para una plataforma.

        Args:
            platform: Nombre de la plataforma

        Returns:
            True si el archivo existe y no está vacío
        """
        cookie_path = self.get_cookie_path(platform)
        return cookie_path.exists() and cookie_path.stat().st_size > 0

    def get_ydl_opts(self, platform: str) -> dict:
        """
        Obtener las opciones de yt-dlp para cookies según la plataforma.

        Args:
            platform: Nombre de la plataforma

        Returns:
            Diccionario con opciones de cookies para yt-dlp (vacío si no hay cookies)
        """
        cookie_path = self.get_cookie_path(platform)

        if cookie_path.exists() and cookie_path.stat().st_size > 0:
            return {"cookiefile": str(cookie_path)}

        return {}

    def is_active(self, platform: str = None) -> bool:
        """
        Verificar si hay cookies configuradas.

        Args:
            platform: Si se especifica, verifica solo esa plataforma.
                     Si no, verifica si hay al menos una plataforma con cookies.

        Returns:
            True si hay cookies configuradas
        """
        if platform:
            return self.has_cookies(platform)

        return any(self.has_cookies(p) for p in self.PLATFORMS)

    def configure_file(self, platform: str, cookie_file_path: Path) -> bool:
        """
        Configurar cookies para una plataforma copiando el archivo a la carpeta cookies/.

        Args:
            platform: Nombre de la plataforma
            cookie_file_path: Ruta al archivo cookies.txt origen

        Returns:
            True si se configuró correctamente
        """
        validation = self.validate_cookie_file(cookie_file_path)

        if not validation.valid:
            self.console.print(f"[red]{validation.message}[/red]")
            return False

        dest_path = self.get_cookie_path(platform)

        try:
            shutil.copy2(cookie_file_path, dest_path)
            self.console.print(f"[green]✓[/green] Cookies para [bold]{platform}[/bold] configuradas: [dim]{dest_path}[/dim]")
            return True
        except Exception as e:
            self.console.print(f"[red]Error al copiar archivo: {e}[/red]")
            return False

    def configure_from_browser(self, platform: str, browser: Browser) -> bool:
        """
        Configurar cookies extrayéndolas del navegador.

        Args:
            platform: Nombre de la plataforma
            browser: Navegador del cual extraer cookies

        Returns:
            True si se configuró correctamente
        """
        import yt_dlp

        dest_path = self.get_cookie_path(platform)

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "cookiefile": str(dest_path),
            "cookiesfrombrowser": (browser.value,),
        }

        try:
            url_map = {
                "youtube": "https://www.youtube.com",
                "instagram": "https://www.instagram.com",
                "facebook": "https://www.facebook.com",
                "tiktok": "https://www.tiktok.com",
            }
            test_url = url_map.get(platform.lower(), "https://www.youtube.com")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(test_url, download=False)

            if dest_path.exists() and dest_path.stat().st_size > 0:
                self.console.print(f"[green]✓[/green] Cookies para [bold]{platform}[/bold] extraídas de {browser.value}")
                return True
            else:
                self.console.print(f"[yellow]⚠ No se pudieron extraer cookies de {browser.value}[/yellow]")
                return False

        except yt_dlp.utils.DownloadError as e:
            self._print_browser_cookie_error(e, browser)
            return False
        except Exception as e:
            self._print_browser_cookie_error(e, browser)
            return False

    def _print_browser_cookie_error(self, error: Exception, browser: Browser) -> None:
        """Mostrar un mensaje claro y accionable cuando falla la extracción de cookies."""
        error_lower = str(error).lower()

        if any(kw in error_lower for kw in ["locked", "in use", "database is locked", "busy"]):
            self.console.print(f"[yellow]⚠ El navegador {browser.value} está en uso.[/yellow]")
            self.console.print("[yellow]Cierra el navegador por completo e inténtalo de nuevo.[/yellow]")
        elif any(kw in error_lower for kw in ["keyring", "crypto", "encryption", "master key", "decrypt", "safely stored"]):
            self.console.print(f"[yellow]⚠ No se pudieron descifrar las cookies de {browser.value}.[/yellow]")
            self.console.print("[yellow]Usa la opción 'Cargar cookies desde archivo' con un cookies.txt exportado.[/yellow]")
        elif any(kw in error_lower for kw in ["profile", "not found", "unable to find", "permission", "access denied"]):
            self.console.print(f"[yellow]⚠ No se encontró un perfil accesible de {browser.value}.[/yellow]")
            self.console.print("[yellow]Inicia sesión en el navegador o usa la opción 'Cargar cookies desde archivo'.[/yellow]")
        else:
            self.console.print(f"[red]Error al extraer cookies: {error}[/red]")

    def clear(self, platform: str = None) -> bool:
        """
        Desactivar cookies.

        Args:
            platform: Si se especifica, elimina solo esa plataforma.
                     Si no, elimina todas las cookies.

        Returns:
            True si se limpió correctamente
        """
        if platform:
            cookie_path = self.get_cookie_path(platform)
            if cookie_path.exists():
                cookie_path.unlink()
                self.console.print(f"[green]✓[/green] Cookies de [bold]{platform}[/bold] eliminadas")
            return True

        for p in self.PLATFORMS:
            cookie_path = self.get_cookie_path(p)
            if cookie_path.exists():
                cookie_path.unlink()

        self.console.print("[green]✓[/green] Todas las cookies eliminadas")
        return True

    def validate_cookie_file(self, cookie_file_path: Path) -> CookieValidation:
        """
        Validar que un archivo cookies.txt tenga formato correcto.

        Args:
            cookie_file_path: Ruta al archivo cookies.txt

        Returns:
            CookieValidation con el resultado
        """
        if not cookie_file_path.exists():
            return CookieValidation(valid=False, message=f"El archivo no existe: {cookie_file_path}")

        if not cookie_file_path.is_file():
            return CookieValidation(valid=False, message="La ruta no es un archivo")

        if cookie_file_path.stat().st_size == 0:
            return CookieValidation(valid=False, message="El archivo está vacío")

        try:
            content = cookie_file_path.read_text(encoding="utf-8", errors="ignore")
            lines = [
                line.strip()
                for line in content.splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]

            if not lines:
                return CookieValidation(
                    valid=False,
                    message="El archivo no contiene cookies válidas (solo comentarios o líneas vacías)"
                )

            valid_lines = 0
            for line in lines:
                fields = line.split("\t")
                if len(fields) >= 7:
                    valid_lines += 1

            if valid_lines == 0:
                return CookieValidation(
                    valid=False,
                    message="El archivo no tiene formato Netscape válido. Usa una extensión como 'Get cookies.txt LOCALLY'"
                )

            return CookieValidation(
                valid=True,
                message=f"Archivo válido con {valid_lines} cookies"
            )

        except Exception as e:
            return CookieValidation(valid=False, message=f"Error al leer el archivo: {e}")

    def test_cookies(self, platform: str) -> CookieValidation:
        """
        Verificar si las cookies de una plataforma permiten acceder.

        Realiza una petición HTTP autenticada a una página de cuenta y detecta
        si el servidor redirige al login o devuelve una página de inicio de
        sesión, lo que indica cookies inválidas o expiradas.
        """
        from http.cookiejar import MozillaCookieJar

        import urllib.request

        if not self.has_cookies(platform):
            return CookieValidation(valid=False, message=f"No hay cookies configuradas para {platform}")

        # Páginas que requieren iniciar sesión para acceder
        url_map = {
            "youtube": "https://www.youtube.com/account",
            "instagram": "https://www.instagram.com/accounts/edit/",
            "facebook": "https://www.facebook.com/settings",
            "tiktok": "https://www.tiktok.com/upload",
        }
        test_url = url_map.get(platform.lower())

        if not test_url:
            return CookieValidation(valid=False, message=f"Plataforma no soportada: {platform}")

        cookie_path = self.get_cookie_path(platform)
        jar = MozillaCookieJar(str(cookie_path))
        try:
            jar.load(ignore_discard=True, ignore_expires=True)
        except Exception as e:
            return CookieValidation(valid=False, message=f"No se pudo leer el archivo de cookies ({e}). Re-exporta tus cookies.")

        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
        opener.addheaders = [
            ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
            ("Accept-Language", "en-US,en;q=0.9"),
        ]

        try:
            with opener.open(test_url, timeout=30) as resp:
                final_url = resp.geturl().lower()
                body = resp.read(200000).decode("utf-8", errors="ignore").lower()
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                return CookieValidation(valid=False, message=f"Cookies de {platform} inválidas o expiradas (HTTP {e.code}). Re-exporta tus cookies.")
            return CookieValidation(valid=False, message=f"Error de acceso: HTTP {e.code}")
        except Exception as e:
            return CookieValidation(valid=False, message=f"Error de acceso: {e}")

        # Detectar redirección a una URL de inicio de sesión
        redirected_to_login = any(m in final_url for m in ["signin", "servicelogin", "/login", "accounts/login"])

        # Detectar marcadores de inicio de sesión en el cuerpo (páginas que responden 200 con el login)
        body_has_login = any(m in body for m in [
            "sign in to continue", "log in to continue",
            "sign in", "log in", "iniciar sesión", "iniciar sesion",
            "enter your password", "log in with",
        ])

        if redirected_to_login or body_has_login:
            return CookieValidation(valid=False, message=f"Cookies de {platform} inválidas o expiradas. Re-exporta tus cookies.")

        return CookieValidation(valid=True, message=f"Cookies de {platform} válidas")

    def show_status(self) -> None:
        """Mostrar el estado actual de las cookies por plataforma."""
        self.console.print("\n[bold cyan]Estado de cookies:[/bold cyan]")
        self.console.print(f"  [dim]Carpeta: {self.cookies_dir}[/dim]\n")

        any_configured = False

        for platform in self.PLATFORMS:
            cookie_path = self.get_cookie_path(platform)
            if cookie_path.exists() and cookie_path.stat().st_size > 0:
                any_configured = True
                size_kb = cookie_path.stat().st_size / 1024
                self.console.print(f"  [green]✓[/green] [bold]{platform.capitalize()}[/bold]: [dim]{size_kb:.1f} KB[/dim]")
            else:
                self.console.print(f"  [dim]○ {platform.capitalize()}: Sin cookies[/dim]")

        if not any_configured:
            self.console.print("\n  [yellow]⚠ No hay cookies configuradas[/yellow]")
            self.console.print("  [dim]Los videos privados/restringidos no podrán descargarse[/dim]")
