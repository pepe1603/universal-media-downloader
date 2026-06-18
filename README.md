# Universal Media Downloader (UMD)

CLI multiplataforma para descargar contenido multimedia desde múltiples plataformas.

## Estado Actual

✅ **Fase 2 Completada** - Conversión de audio con carátulas y metadatos

## Plataformas soportadas

- YouTube ✅
- Facebook ✅
- Instagram ✅
- TikTok ✅

## Características

### Implementadas (Fase 1 y 2)
- ✅ Descarga de video en máxima calidad disponible
- ✅ Descarga en calidad recomendada (720p)
- ✅ Detección automática de plataforma desde URL
- ✅ Verificación de dependencias (FFmpeg, yt-dlp)
- ✅ Conversión de audio a múltiples formatos (MP3, M4A, FLAC, OGG, WAV)
- ✅ Incrustación de carátulas desde miniaturas
- ✅ Metadatos ID3 (título, artista, álbum, fecha)
- ✅ Interfaz CLI profesional con Rich
- ✅ Soporte multiplataforma (Windows, Linux, macOS)

### En desarrollo
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
cd universal-media-downloader

```


2. Crear entorno virtual:

```bash
python -m venv venv 
```

3. Activar entorno virtual:
- Windows (Git Bash): source venv/Scripts/activate
- Linux/macOS: source venv/bin/activate

4. Instalar dependencias:

```bash
pip install -r requirements.txt 
```

5. Importante: Asegúrate de tener FFmpeg instalado:

- Windows: winget install FFmpeg
- Linux: sudo apt install ffmpeg
- macOS: brew install ffmpeg

## Uso

```bash
python src/main.py 
```

# Ejemplo de descarga de video

1. Selecciona tipo de dispositivo (Móvil/Computadora)
2. Selecciona opción 1: "Descargar contenido"
3. Ingresa la URL (ejemplo: https://www.youtube.com/watch?v=dQw4w9WgXcQ)
4. Selecciona calidad:
    - 1: Máxima disponible
    - 2: Recomendada (720p)

## Ejemplo de descarga de audio

1. Selecciona opción 1: "Descargar contenido"
2. Ingresa la URL de YouTube
3. Selecciona opción 3: "Convertir a audio"
4. Selecciona formato de audio:
    - 1: MP3 (Recomendado)
    - 2: M4A (Apple/iOS)
    - 3: FLAC (Sin pérdida)
    - 4: OGG (Código abierto)
    - 5: WAV (Sin comprimir)

El sistema automáticamente:

- Descarga el audio en la mejor calidad
- Descarga la miniatura del video
- Convierte al formato seleccionado
- Incrusta la carátula y metadatos (título, artista, álbum, fecha)
- Elimina archivos temporales

Los archivos se guardan en:

- Windows: C:\Users\TU_USUARIO\UniversalDownloader\[plataforma]\
- Linux/macOS: ~/UniversalDownloader/[plataforma]\
- Termux: /storage/emulated/0/UniversalDownloader/[plataforma]\

## Tecnologías

- Python 3.12+
- yt-dlp (descarga de videos)
- FFmpeg (procesamiento de audio/video)
- mutagen (metadatos ID3)
- Rich (UI terminal profesional)
- Typer (CLI framework)
- Pydantic (validación de datos)

## Roadmap

### Fase 1 ✅ (Completada)

- CLI básica con menú principal
- Detección de plataforma
- Descarga de video (calidad máxima y recomendada)
- Verificación de dependencias

### Fase 2 ✅ (Completada)

- onversión de audio (MP3, M4A, FLAC, OGG, WAV)
- Descarga de miniaturas
- Inserción de carátulas
- Metadatos ID3 (artista, título, álbum, fecha)

### Fase 3 (Próxima)

- Historial de descargas con SQLite
- Exportación de resúmenes (TXT, MD, JSON)
- Búsqueda en historial

### Fase 4

- Soporte completo para Termux (Android)
- Optimización de rutas para móvil

### Fase 5

- API REST con FastAPI
- Cliente Web o Android

### Estructura del proyecto

```markdown
universal-media-downloader/
├── src/
│   ├── main.py              # Punto de entrada y menú principal
│   ├── core/
│   │   ├── downloader.py    # Lógica de descarga con yt-dlp
│   │   ├── converter.py     # Conversión de audio con FFmpeg
│   │   ├── metadata.py      # Incrustación de metadatos y carátulas
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
```

## Licencia
- MIT

## Autor
Desarrollado como proyecto personal de automatización multimedia.











