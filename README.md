# Universal Media Downloader (UMD)

CLI multiplataforma para descargar contenido multimedia desde múltiples plataformas.

## Estado Actual

✅ **Fase 5 Completada** - Soporte para contenido privado con cookies

## Plataformas soportadas

- YouTube ✅
- Facebook ✅
- Instagram ✅
- TikTok ✅

## Características

### Implementadas (Fases 1, 2, 3, 4 y 5)
- ✅ Descarga de video en máxima calidad disponible
- ✅ Descarga en calidad recomendada (720p)
- ✅ Detección automática de plataforma desde URL
- ✅ Verificación de dependencias (FFmpeg, yt-dlp)
- ✅ Conversión de audio a múltiples formatos (MP3, M4A, FLAC, OGG, WAV)
- ✅ Incrustación de carátulas desde miniaturas
- ✅ Metadatos ID3 (título, artista, álbum, fecha)
- ✅ Historial de descargas con SQLite
- ✅ Búsqueda por plataforma, fecha y nombre
- ✅ Exportación de historial (TXT, Markdown, JSON)
- ✅ Resumen estadístico de descargas
- ✅ **Detección automática de entorno (Termux/Windows/Linux/macOS)**
- ✅ **Organización de archivos en Android (Descargas/Música/Videos)**
- ✅ **Verificación de permisos de almacenamiento en Termux**
- ✅ **Cookies para contenido privado (archivo cookies.txt o navegador local)**
- ✅ **Detección automática de navegadores instalados**
- ✅ **Validación y prueba de cookies**
- ✅ Interfaz CLI profesional con Rich
- ✅ Soporte multiplataforma completo

## Requisitos

- Python 3.12+
- FFmpeg (instalado en el sistema)
- Conexión a internet

## Instalación

### Windows / Linux / macOS

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

- Windows: ```winget install FFmpeg```
- Linux: ```sudo apt install ffmpeg```
- macOS: ```brew install ffmpeg```

### Android (Termux)

1. Instalar Termux desde F-Droid (recomendado):

    - https://f-droid.org/packages/com.termux/

2. Actualizar paquetes:

```bash
    pkg update && pkg upgrade
```

3. Instalar dependencias

```bash
    pkg install python ffmpeg git
```

4. Configurar almacenamiento:

```bash
    termux-setup-storage
```
(Acepta los permisos cuando se soliciten)

5. Clonar repositorio:

```bash
    cd ~
    git clone https://github.com/pepe1603/universal-media-downloader.git
    cd universal-media-downloader
```

6. Crear entorno virtual e Instalar dependencias: 

```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
```

7. Mantener Termux despierto (opcional pero recomendado):

```bash
    termux-wake-lock
```

## Uso

```bash
python src/main.py 
```

La aplicación detecta automáticamente si estás en Termux o computadora y ajusta las rutas y opciones disponibles.


# Menú principal (Computadora)
    1. Descargar contenido - Descarga videos o audio desde URLs
    2. Consultar descargas - Busca en el historial de descargas
    3. Exportar historial - Exporta a TXT, Markdown o JSON
    4. Resumen reciente - Estadísticas y últimas descargas
    5. Limpiar errores - Elimina descargas fallidas del historial
    6. Cambiar usuario - Cambia el nombre de usuario
    7. Configuración - Verifica dependencias y base de datos

# Menu principal (Movil/Termux)
    1. Descargar contenido - Descarga videos o audio desde URLs
    2. Consultar descargas - Busca en el historial de descargas
    3. Exportar historial - Exporta a TXT, Markdown o JSON
    4. Resumen reciente - Estadísticas y últimas descargas
    5. Limpiar errores - Elimina descargas fallidas del historial
    6. 📁 Organizar archivos - Mueve archivos a Descargas/Música/Videos
    7. Cambiar usuario - Cambia el nombre de usuario
    8. Configuración - Verifica dependencias y entorno

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
- Registra la descarga en el historial SQLite
- Elimina archivos temporales

# Ejemplo de consulta de historial

1. Selecciona opción 2: "Consultar descargas"
2. Elige el tipo de búsqueda:
    - Ver últimas 20 descargas
    - Buscar por plataforma (YouTube, Facebook, Instagram, TikTok)
    - Buscar por rango de fechas
    - Buscar por texto en el título

# Ejemplo de exportación

1. Selecciona opción 3: "Exportar historial"
2. Elige el formato:
    - TXT: Texto plano legible
    - Markdown: Formato con encabezados y listas
    - JSON: Datos estructurados para procesamiento


## Cookies para contenido privado

Para descargar videos privados, restringidos por edad o que requieren inicio de sesión, necesitas configurar cookies de tu navegador.

Las cookies se organizan por plataforma en la carpeta `cookies/`:
```
UniversalDownloader/
└── cookies/
    ├── youtube.txt
    ├── instagram.txt
    ├── facebook.txt
    └── tiktok.txt
```

### Desde computadora (Windows/Linux/macOS)

**Opción A: Archivo cookies.txt por plataforma**

1. Instala la extensión "Get cookies.txt LOCALLY" en tu navegador
2. Inicia sesión en la plataforma (YouTube, Instagram, etc.)
3. Exporta las cookies con la extensión
4. En UMD: Configuración > Gestionar cookies > Cargar cookies para una plataforma
5. Selecciona la plataforma (YouTube, Instagram, etc.)
6. Ingresa la ruta al archivo exportado
7. El archivo se copiará automáticamente a `cookies/[plataforma].txt`

**Opción B: Extraer del navegador (automático)**

1. Ve a Configuración > Gestionar cookies > Extraer cookies del navegador
2. Selecciona la plataforma
3. Elige el navegador detectado (Chrome, Firefox, Edge, etc.)
4. El sistema extraerá las cookies automáticamente

### Desde Android (Termux)

1. Exporta cookies desde tu navegador móvil con "Get cookies.txt LOCALLY"
2. Copia el archivo a tu dispositivo:
    ```bash
    cp /sdcard/Download/instagram_cookies.txt ~/instagram_cookies.txt
    ```
3. En UMD: Configuración > Gestionar cookies > Cargar cookies para una plataforma
4. Selecciona la plataforma e ingresa la ruta al archivo

### Verificar cookies

Puedes probar si tus cookies siguen vigentes desde:
- Configuración > Gestionar cookies > Probar cookies de una plataforma

> **Nota:** Las cookies expiran periódicamente. Si una descarga falla con error de autenticación, re-exporta tus cookies.

## Rutas de almacenamiento

Los archivos se guardan en:

#### Computadora
    - Windows: C:\Users\TU_USUARIO\UniversalDownloader\
    - Linux/macOS: ~/UniversalDownloader/

#### Android (Termux)
    - Descargas: /storage/emulated/0/Download/UniversalDownloader/
    - Música: /storage/emulated/0/Music/UniversalDownloader/
    - Videos: /storage/emulated/0/Movies/UniversalDownloader/

#### En General

- Windows: C:\Users\TU_USUARIO\UniversalDownloader\exports\[plataforma]\
- Linux/macOS: ~/UniversalDownloader/exports/[plataforma]\
- Termux: /storage/emulated/0/UniversalDownloader/exports/[plataforma]\

## Tecnologías

- Python 3.12+
- yt-dlp (descarga de videos)
- FFmpeg (procesamiento de audio/video)
- mutagen (metadatos ID3)
- SQLite (base de datos de historial)
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

### Fase 3 ✅ (Completada)

- Historial de descargas con SQLite
- Exportación de resúmenes (TXT, MD, JSON)
- Búsqueda en historial (TXT, MD, JSON)
- Resumen estadístico

### Fase 4 ✅ (Completada)
- Detección automática de entorno (Termux/Windows/Linux/macOS)
- Rutas optimizadas para Android
- Verificación de permisos de almacenamiento
- Organización de archivos en móvil
- Instrucciones específicas para Termux

### Fase 5 ✅ (Completada)
- Soporte de cookies para contenido privado/restringido
- Carga de cookies desde archivo cookies.txt
- Extracción de cookies desde navegadores locales (Chrome, Firefox, Edge, etc.)
- Detección automática de navegadores instalados
- Validación y prueba de cookies
- Persistencia de configuración en SQLite
- Sugerencia automática al detectar errores de autenticación

### Fase 6 (Próxima)

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
│   │   ├── exporter.py      # Exportación de historial
│   │   ├── dependencies.py  # Verificación de dependencias
│   │   ├── environment.py   # Detección de entorno
│   │   ├── file_organizer.py # Organización de archivos
│   │   └── cookies.py       # Gestión de cookies para contenido privado
│   ├── platforms/
│   │   └── detector.py      # Detección de plataformas
│   ├── storage/
│   │   └── database.py      # Base de datos SQLite
│   ├── ui/                  # Componentes de UI (próximamente)
├── tests/
├── docs/
├── requirements.txt
├── requirements.lock
└── README.md
```

## Licencia
MIT

## Autor
pepe1603

Desarrollado como proyecto personal de automatización multimedia.











