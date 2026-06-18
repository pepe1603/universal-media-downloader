
# Universal Media Downloader (UMD)

CLI multiplataforma para descargar contenido multimedia desde múltiples plataformas.

## Plataformas soportadas

- YouTube
- Facebook
- Instagram
- TikTok

## Características

- Descarga de video en máxima calidad disponible
- Descarga en calidad recomendada
- Conversión a audio (MP3, M4A, FLAC, OGG, WAV)
- Inserción de carátulas y metadatos
- Historial de descargas con SQLite
- Exportación de resúmenes (TXT, MD, JSON)
- Compatibilidad con Windows, Linux, macOS y Termux

## Tecnologías

- Python 3.12+
- yt-dlp
- FFmpeg
- Rich (UI terminal)
- Typer (CLI profesional)
- Pydantic (configuración)
- SQLite (historial)
- mutagen (metadatos)

## Instalación

1. Clonar repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno virtual
4. Instalar dependencias: `pip install -r requirements.txt`

## Uso

```bash
python src/main.py

Estado
🚧 En desarrollo - Fase 1
Roadmap
Fase 1 (Actual)
Estructura del proyecto
CLI básica con menú principal
Detección de plataforma
Descarga de video (calidad máxima y recomendada)
Fase 2
Conversión de audio
Carátulas y metadatos
Fase 3
Historial SQLite
Exportación TXT y Markdown
Fase 4
Soporte avanzado para Termux
Fase 5
API REST con FastAPI
Licencia
MIT
EOF