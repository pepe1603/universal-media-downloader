"""
Módulo de descarga de playlists de YouTube.

Solo soporta listas de YouTube. Cada video se descarga de forma independiente
mediante ``MediaDownloader``, de modo que el fallo de uno no detiene la lista.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional
from urllib.parse import parse_qs, urlparse

import yt_dlp
from rich.console import Console
from yt_dlp.utils import sanitize_filename

from src.core.downloader import DownloadResult, MediaDownloader, Quality

logger = logging.getLogger(__name__)

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}
MAX_PLAYLIST_ITEMS = 200
MAX_CONSECUTIVE_FAILURES = 5  # corta la lista ante bloqueos (403/429) para no empeorarlos
MAX_FOLDER_NAME_LENGTH = 80
PLATFORM_NAME = "YouTube"

_PLAYLIST_ID_RE = re.compile(r"[A-Za-z0-9_-]{2,64}")
_VIDEO_ID_RE = re.compile(r"[A-Za-z0-9_-]{11}")
# Mixes/radios automáticos (RD...) son personalizados e infinitos: no son una playlist descargable.
_UNSUPPORTED_LIST_PREFIXES = ("RD",)
_UNAVAILABLE_TITLES = {"[private video]", "[deleted video]"}

STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"
STATUS_ABORTED = "aborted"


def extract_playlist_id(url: str) -> Optional[str]:
    """Extrae el ID de playlist de una URL de YouTube.

    Args:
        url: URL ingresada por el usuario.

    Returns:
        El ID de la lista, o None si no es una URL de YouTube con lista soportada
        (otras plataformas, sin ``list=`` o mixes automáticos ``RD...``).
    """
    try:
        parsed = urlparse(url.strip())
    except ValueError:
        return None
    if (parsed.hostname or "").lower() not in YOUTUBE_HOSTS:
        return None
    values = parse_qs(parsed.query).get("list")
    if not values:
        return None
    playlist_id = values[0]
    if not _PLAYLIST_ID_RE.fullmatch(playlist_id) or playlist_id.startswith(_UNSUPPORTED_LIST_PREFIXES):
        return None
    return playlist_id


def has_video_reference(url: str) -> bool:
    """Indica si la URL, además de la lista, apunta a un video concreto (``watch?v=`` / youtu.be)."""
    parsed = urlparse(url.strip())
    if (parsed.hostname or "").lower() == "youtu.be":
        return bool(parsed.path.strip("/"))
    return "v" in parse_qs(parsed.query)


def build_playlist_url(playlist_id: str) -> str:
    """URL canónica de una playlist (descarta cualquier otro parámetro de la URL original)."""
    return f"https://www.youtube.com/playlist?list={playlist_id}"


def build_video_url(video_id: str) -> str:
    """URL canónica de un video.

    Raises:
        ValueError: Si el ID no tiene el formato de 11 caracteres de YouTube.
    """
    if not _VIDEO_ID_RE.fullmatch(video_id):
        raise ValueError(f"ID de video inválido: {video_id!r}")
    return f"https://www.youtube.com/watch?v={video_id}"


def safe_folder_name(title: str, fallback: str) -> str:
    """Nombre de carpeta seguro (sin separadores ni puntos iniciales) a partir de un título."""
    name = sanitize_filename(title, restricted=True).strip(" ._")[:MAX_FOLDER_NAME_LENGTH]
    return name or fallback


@dataclass
class PlaylistEntry:
    """Un elemento de la playlist."""
    index: int
    video_id: Optional[str]
    title: str
    skip_reason: Optional[str] = None


@dataclass
class PlaylistInfo:
    """Información de una playlist."""
    playlist_id: str
    title: str
    entries: List[PlaylistEntry]
    truncated: bool = False

    @property
    def downloadable(self) -> List[PlaylistEntry]:
        """Entradas sin motivo de omisión previo."""
        return [e for e in self.entries if e.skip_reason is None]


@dataclass
class EntryOutcome:
    """Resultado del procesamiento de un elemento."""
    entry: PlaylistEntry
    status: str
    message: str = ""
    result: Optional[DownloadResult] = None


@dataclass
class PlaylistSummary:
    """Resumen de una ejecución de descarga de playlist."""
    outcomes: List[EntryOutcome] = field(default_factory=list)
    interrupted: bool = False
    stopped_by_failures: bool = False

    def _with_status(self, status: str) -> List[EntryOutcome]:
        return [o for o in self.outcomes if o.status == status]

    @property
    def succeeded(self) -> List[EntryOutcome]:
        """Descargas completadas."""
        return self._with_status(STATUS_SUCCESS)

    @property
    def failed(self) -> List[EntryOutcome]:
        """Descargas que fallaron."""
        return self._with_status(STATUS_FAILED)

    @property
    def skipped(self) -> List[EntryOutcome]:
        """Elementos omitidos (privados, eliminados, ya descargados)."""
        return self._with_status(STATUS_SKIPPED)

    @property
    def aborted(self) -> List[EntryOutcome]:
        """Elementos no procesados por interrupción o exceso de fallos."""
        return self._with_status(STATUS_ABORTED)


class PlaylistDownloader:
    """Descarga playlists de YouTube video por video."""

    def __init__(self, downloader: MediaDownloader, console: Optional[Console] = None) -> None:
        self.downloader = downloader
        self.console = console or Console()

    def fetch_info(self, url: str) -> Optional[PlaylistInfo]:
        """Obtiene título y elementos de la playlist sin descargar nada.

        Args:
            url: URL con parámetro ``list=`` de YouTube.

        Returns:
            PlaylistInfo, o None si la URL no es válida o la lista no se pudo leer.
        """
        playlist_id = extract_playlist_id(url)
        if playlist_id is None:
            return None

        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": "in_playlist",
            "skip_download": True,
            "playlistend": MAX_PLAYLIST_ITEMS + 1,
            "socket_timeout": 30,
        }
        opts.update(self.downloader.cookie_manager.get_ydl_opts("youtube"))

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                data = ydl.extract_info(build_playlist_url(playlist_id), download=False)
        except yt_dlp.utils.YoutubeDLError as e:
            logger.warning("No se pudo leer la playlist %s: %s", playlist_id, e)
            self.console.print(f"[red]✗ No se pudo leer la playlist: {e}[/red]")
            return None

        if not data:
            return None

        raw_entries = list(data.get("entries") or [])
        truncated = len(raw_entries) > MAX_PLAYLIST_ITEMS
        entries = [
            self._parse_entry(i, raw)
            for i, raw in enumerate(raw_entries[:MAX_PLAYLIST_ITEMS], start=1)
        ]
        title = data.get("title") or playlist_id
        return PlaylistInfo(playlist_id=playlist_id, title=title, entries=entries, truncated=truncated)

    @staticmethod
    def _parse_entry(index: int, raw: Optional[dict]) -> PlaylistEntry:
        """Convierte una entrada plana de yt-dlp en PlaylistEntry, marcando las no disponibles."""
        if not raw:
            return PlaylistEntry(index, None, "(no disponible)", "video no disponible")
        title = raw.get("title") or "(sin título)"
        video_id = raw.get("id")
        if title.lower() in _UNAVAILABLE_TITLES:
            return PlaylistEntry(index, video_id, title, "video privado o eliminado")
        if not video_id or not _VIDEO_ID_RE.fullmatch(video_id):
            return PlaylistEntry(index, None, title, "ID de video inválido")
        return PlaylistEntry(index, video_id, title)

    def output_dir_for(self, info: PlaylistInfo, base: Path) -> Path:
        """Carpeta de salida de la playlist, garantizada dentro de ``base``."""
        folder = base / "playlists" / safe_folder_name(info.title, info.playlist_id)
        if not folder.resolve().is_relative_to(base.resolve()):
            raise ValueError("Carpeta de playlist fuera de la ruta base")
        return folder

    def download_entries(
        self,
        entries: List[PlaylistEntry],
        quality: Quality,
        output_dir: Path,
        download_thumbnail: bool = False,
        on_success: Optional[Callable[[DownloadResult], None]] = None,
        total: Optional[int] = None,
    ) -> PlaylistSummary:
        """Descarga los elementos uno a uno, aislando los fallos de cada video.

        Args:
            entries: Elementos a procesar.
            quality: Calidad de descarga.
            output_dir: Carpeta base de salida (yt-dlp añade la subcarpeta de plataforma).
            download_thumbnail: Si debe descargar la miniatura.
            on_success: Callback tras cada descarga correcta (p. ej. conversión de audio).
            total: Total mostrado en el contador ``[i/total]`` (por defecto, len(entries)).

        Returns:
            PlaylistSummary con el resultado de cada elemento.
        """
        summary = PlaylistSummary()
        total = total or len(entries)
        consecutive_failures = 0

        for position, entry in enumerate(entries):
            label = f"[{entry.index}/{total}] {entry.title}"

            if entry.skip_reason:
                summary.outcomes.append(EntryOutcome(entry, STATUS_SKIPPED, entry.skip_reason))
                self.console.print(f"[yellow]⏭ {label} — omitido: {entry.skip_reason}[/yellow]")
                continue

            url = build_video_url(entry.video_id)
            existing = self.downloader.database.find_successful_download(url)
            if existing and Path(existing.file_path).exists():
                summary.outcomes.append(EntryOutcome(entry, STATUS_SKIPPED, "ya descargado"))
                self.console.print(f"[dim]⏭ {label} — ya descargado[/dim]")
                continue

            self.console.print(f"\n[bold cyan]⬇ {label}[/bold cyan]")
            try:
                result = self.downloader.download(
                    url=url,
                    quality=quality,
                    output_path=output_dir,
                    platform=PLATFORM_NAME,
                    download_thumbnail=download_thumbnail,
                )
            except KeyboardInterrupt:
                summary.interrupted = True
                self._mark_remaining(summary, entries[position:], "interrumpido por el usuario")
                self.console.print("\n[yellow]⚠ Descarga de la lista interrumpida[/yellow]")
                break

            if result.success:
                consecutive_failures = 0
                summary.outcomes.append(EntryOutcome(entry, STATUS_SUCCESS, result=result))
                if on_success is not None:
                    self._run_callback(on_success, result)
                continue

            consecutive_failures += 1
            reason = (result.error_message or "error desconocido").splitlines()[0]
            summary.outcomes.append(EntryOutcome(entry, STATUS_FAILED, reason, result))
            self.console.print(f"[red]✗ Falló: {reason}[/red]")

            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                summary.stopped_by_failures = True
                self._mark_remaining(
                    summary, entries[position + 1:],
                    f"detenido tras {MAX_CONSECUTIVE_FAILURES} fallos seguidos",
                )
                self.console.print(
                    f"\n[red]✗ {MAX_CONSECUTIVE_FAILURES} fallos seguidos: se detiene la lista "
                    "(posible bloqueo, límite de peticiones o falta de cookies).[/red]"
                )
                break

        return summary

    def _run_callback(self, callback: Callable[[DownloadResult], None], result: DownloadResult) -> None:
        """Ejecuta el post-proceso de un video sin que sus errores detengan la lista."""
        try:
            callback(result)
        except (OSError, ValueError) as e:
            logger.exception("Falló el post-proceso de %s", result.file_path)
            self.console.print(f"[yellow]⚠ Post-proceso fallido: {e}[/yellow]")

    @staticmethod
    def _mark_remaining(summary: PlaylistSummary, remaining: List[PlaylistEntry], reason: str) -> None:
        """Registra como no procesados los elementos restantes."""
        for entry in remaining:
            summary.outcomes.append(EntryOutcome(entry, STATUS_ABORTED, reason))
