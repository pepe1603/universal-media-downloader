# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [0.2.0] - 2026-11-22

### Added
- Descarga de playlists de YouTube (`src/core/playlist.py`): fallos aislados por video, omisión de privados/eliminados/ya descargados, reintento de fallidos, corte tras 5 fallos seguidos e interrupción con Ctrl+C.

### Fixed
- Un enlace `watch?v=...&list=...` ya no expande toda la lista en una descarga individual (`noplaylist`) (BUG-20).

## [0.1.0] - 2026-11-22

### Added
- Suite de tests (pytest) para detector, environment, file_organizer, database, cookies, converter, metadata, exporter, dependencies, downloader y validación (cobertura `src/core` ≈ 73%).
- `src/ui/validation.py`: validación de URL, nombre de usuario y rutas.
- Comando `umd` (entry point) e instalación con `pip install -e .`.
- CI en GitHub Actions (ruff, py_compile, pytest) en Linux, Windows y macOS.
- Logging por módulo en `core/`; `UMD_DEBUG=1` habilita logs y traceback.
- Confirmación antes de eliminar cookies de una plataforma.

### Changed
- Excepciones específicas en lugar de `except Exception` en `core/` (salvo fronteras de yt-dlp).
- Saltos de línea normalizados a LF (`.gitattributes`).

### Security
- Validación del nombre de plataforma de cookies (path traversal) y permisos `0600` en cookies copiadas (BUG-16).
- Detección de plataforma por hostname y no por subcadena (BUG-17).
- `subprocess` con `encoding="utf-8", errors="replace"` y rutas absolutas a FFmpeg (BUG-18).
