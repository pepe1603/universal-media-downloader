# Universal Media Downloader (UMD)

CLI multiplataforma para descargar contenido multimedia desde múltiples plataformas.

## Estado Actual

✅ **Fase 1 Completada** - Descarga de videos funcional

## Plataformas soportadas

- YouTube ✅
- Facebook ✅
- Instagram ✅
- TikTok ✅

## Características

### Implementadas (Fase 1)
- ✅ Descarga de video en máxima calidad disponible
- ✅ Descarga en calidad recomendada (720p)
- ✅ Detección automática de plataforma desde URL
- ✅ Verificación de dependencias (FFmpeg, yt-dlp)
- ✅ Interfaz CLI profesional con Rich
- ✅ Soporte multiplataforma (Windows, Linux, macOS)

### En desarrollo
- 🔄 Conversión a audio (MP3, M4A, FLAC, OGG, WAV)
- 🔄 Inserción de carátulas y metadatos
- 🔄 Historial de descargas con SQLite
- 🔄 Exportación de resúmenes (TXT, MD, JSON)
- 🔄 Compatibilidad con Termux (Android)

## Requisitos

- Python 3.12+
- FFmpeg (instalado en el sistema)
- Conexión a internet

## Instalación

1. Clonar repositorio:
```bash
git clone https://github.com/pepe1603/universal-media-downloader.git
cd universal-media-downloader ```

2. Crear entorno virtual:

- Activar entorno virtual:
- Windows (Git Bash): source venv/Scripts/activate
- Linux/macOS: source venv/bin/activate

4. Instalar dependencias:

```bash
pip install -r requirements.txt ```

5. Importante: Asegúrate de tener FFmpeg instalado:

- Windows: winget install FFmpeg 
- Linux: sudo apt install ffmpeg
- macOS: brew install ffmpeg

## Uso

```bash
python src/main.py ```

Ejemplo de descarga
Selecciona tipo de dispositivo (Móvil/Computadora)
Selecciona opción 1: "Descargar contenido"
Ingresa la URL (ejemplo: https://www.youtube.com/watch?v=dQw4w9WgXcQ)
Selecciona calidad:
1: Máxima disponible
2: Recomendada (720p)
3: Convertir a audio (próximamente)
Los archivos se guardan en:
Windows: C:\Users\TU_USUARIO\UniversalDownloader\[plataforma]\
Linux/macOS: ~/UniversalDownloader/[plataforma]\
Termux: /storage/emulated/0/UniversalDownloader/[plataforma]\
Tecnologías
Python 3.12+
yt-dlp (descarga de videos)
FFmpeg (procesamiento de audio/video)
Rich (UI terminal profesional)
Typer (CLI framework)
Pydantic (validación de datos)

Roadmap
Fase 1 ✅ (Completada)
CLI básica con menú principal
Detección de plataforma
Descarga de video (calidad máxima y recomendada)
Verificación de dependencias
Fase 2 (Próxima)
Conversión de audio (MP3, M4A, FLAC, OGG, WAV)
Inserción de carátulas desde miniaturas
Metadatos ID3 (artista, título, álbum)
Fase 3
Historial de descargas con SQLite
Exportación de resúmenes (TXT, MD, JSON)
Búsqueda en historial
Fase 4
Soporte completo para Termux (Android)
Optimización de rutas para móvil
Fase 5
API REST con FastAPI
Cliente Web o Android
Estructura del proyecto

# Estructura del proyecto
universal-media-downloader/
├── src/
│   ├── main.py              # Punto de entrada y menú principal
│   ├── core/
│   │   ├── downloader.py    # Lógica de descarga con yt-dlp
│   │   └── dependencies.py  # Verificación de dependencias
│   ├── platforms/
│   │   └── detector.py      # Detección de plataformas
│   ├── ui/                  # Componentes de UI (próximamente)
│   └── storage/             # Base de datos y configuración (próximamente)
├── tests/
├── docs/
├── requirements.txt
├── requirements.lock
└── README.md

Licencia
MIT
Autor
Desarrollado como proyecto personal de automatización multimedia.
