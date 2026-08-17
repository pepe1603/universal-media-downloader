# Guía Android - Universal Media Downloader

Guía completa para instalar, configurar y usar UMD en Android (Termux).

## Índice

1. [Requisitos](#1-requisitos)
2. [Instalación](#2-instalación)
3. [Permisos de almacenamiento](#3-permisos-de-almacenamiento)
4. [Configuración de cookies](#4-configuración-de-cookies)
5. [Uso](#5-uso)
6. [Estructura de archivos](#6-estructura-de-archivos)
7. [Solución de problemas](#7-solución-de-problemas)
8. [Actualización](#8-actualización)

---

## 1. Requisitos

- Android 7.0+
- **Termux** desde F-Droid (⚠️ NO usar la versión de Play Store, está desactualizada)
- ~200 MB de espacio libre
- Conexión a internet

### Paquetes necesarios

| Paquete  | Propósito                          |
|----------|------------------------------------|
| python   | Intérprete de UMD                  |
| ffmpeg   | Conversión y procesamiento de audio/video |
| git      | Clonar el repositorio              |

---

## 2. Instalación

### 2.1 Instalar Termux

Descargar desde **F-Droid** (recomendado):
- https://f-droid.org/packages/com.termux/

> **⚠️ NO usar Google Play Store**: la versión de Play Store está desactualizada y puede causar errores.

### 2.2 Preparar el entorno

```bash
pkg update && pkg upgrade
pkg install python ffmpeg git
```

### 2.3 Dar permisos de almacenamiento

```bash
termux-setup-storage
```

Cuando aparezca el diálogo de permisos, toca **"Allow"**. Esto crea la carpeta `~/storage/` con enlaces al almacenamiento del dispositivo.

### 2.4 Clonar e instalar UMD

```bash
cd ~
git clone https://github.com/pepe1603/universal-media-downloader.git
cd universal-media-downloader
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2.5 Verificar instalación

```bash
python src/main.py
```

Si todo está bien, verás el menú principal con la opción de **Termux**.

### 2.6 Mantener Termux despierto (recomendado)

```bash
termux-wake-lock
```

Evita que Android pause la descarga cuando la pantalla se apaga.

---

## 3. Permisos de almacenamiento

### ¿Por qué son necesarios?

UMD guarda los archivos descargados en:
- `/storage/emulated/0/Download/UniversalDownloader/` (archivos generales)
- `/storage/emulated/0/Music/UniversalDownloader/` (audio)
- `/storage/emulated/0/Movies/UniversalDownloader/` (video)

Sin permisos, los archivos se guardan en el almacenamiento interno de Termux (`~/.local/share/...`) que es inaccesible desde el gestor de archivos.

### Si no se concedieron los permisos

Ejecuta de nuevo:
```bash
termux-setup-storage
```

Si el diálogo no aparece, verifica la configuración:
- **Android > Apps > Termux > Permisos > Archivos** → Permitir

### Verificar que los permisos funcionan

```bash
ls -la /storage/emulated/0/Download/
```

Si ves el contenido de tu carpeta de Descargas, los permisos están correctos.

---

## 4. Configuración de cookies

### ¿Qué son las cookies?

Las cookies permiten descargar contenido **privado** o **restringido** (videos privados, historiales de reproducción, etc.) usando tu sesión de navegador.

### Opción A: Exportar cookies desde el navegador del celular

1. Abre Chrome/Firefox en tu celular
2. Busca la extensión **"Get cookies.txt LOCALLY"** (Chrome) o **"cookies.txt"** (Firefox)
3. Inicia sesión en la plataforma (YouTube, Instagram, etc.)
4. Exporta las cookies como archivo `cookies.txt`
5. Copia el archivo a `/storage/emulated/0/Download/` o envíalo a Termux por Bluetooth/USB

### Opción B: Copiar cookies desde la computadora

1. Exporta cookies desde tu navegador de escritorio
2. Transfiere el archivo `cookies.txt` al celular (USB, Bluetooth, etc.)
3. Colócalo en `/storage/emulated/0/Download/`

### Importar cookies en UMD

Dentro de UMD, selecciona la opción de configurar cookies y apunta al archivo:
```
/storage/emulated/0/Download/cookies.txt
```

### Validar cookies

UMD puede probar si las cookies son válidas. Si ves el mensaje:
- ✅ "Cookies de youtube válidas" → todo funciona
- ❌ "Cookies inválidas o expiradas" → vuelve a exportarlas

---

## 5. Uso

### Iniciar UMD

```bash
cd ~/universal-media-downloader
source venv/bin/activate
python src/main.py
```

### Menú Termux

| Opción | Descripción |
|--------|-------------|
| 1. Descargar contenido | Videos o audio desde URLs |
| 2. Consultar descargas | Buscar en el historial |
| 3. Exportar historial | TXT, Markdown o JSON |
| 4. Resumen reciente | Estadísticas |
| 5. Organizar archivos | Mover archivos entre carpetas |
| 6. Limpiar errores | Eliminar descargas fallidas |
| 7. Configuración | Verificar dependencias |

### Descargar un video

1. Selecciona opción **1**
2. Pega la URL (YouTube, TikTok, Instagram, Facebook)
3. Elige calidad:
   - **Máxima** → mejor calidad disponible
   - **Recomendada** → 720p (balance calidad/tamaño)
   - **Solo audio** → descarga como MP3
4. Espera a que termine

### Organizar archivos

La opción **5** mueve los archivos descargados automáticamente:
- `.mp3`, `.m4a`, `.flac` → `/Music/UniversalDownloader/`
- `.mp4`, `.mkv`, `.webm` → `/Movies/UniversalDownloader/`
- Otros → `/Download/UniversalDownloader/`

---

## 6. Estructura de archivos

```
/storage/emulated/0/
├── Download/
│   └── UniversalDownloader/
│       ├── *.mp4, *.mp3, *.m4a
│       └── cookies.txt (si configuraste cookies)
├── Music/
│   └── UniversalDownloader/
│       └── (audio organizado)
└── Movies/
    └── UniversalDownloader/
        └── (video organizado)

~/universal-media-downloader/
├── src/
│   └── main.py
├── venv/
└── umd.db (base de datos de historial)
```

---

## 7. Solución de problemas

### Error: "No hay cookies configuradas"

**Causa**: No exportaste cookies o el archivo no se encontró.

**Solución**:
1. Exporta cookies desde tu navegador (ver sección 4)
2. Coloca el archivo en `/storage/emulated/0/Download/cookies.txt`
3. Configura las cookies en UMD con la ruta completa

### Error: "Permiso de almacenamiento no concedido"

**Solución**:
```bash
termux-setup-storage
```
Si no funciona:
- Android > Apps > Termux > Permisos > Archivos → Permitir
- Reinicia Termux

### Error: "FFmpeg no encontrado"

**Solución**:
```bash
pkg install ffmpeg
```

### Error: "yt-dlp no encontrado"

**Solución**:
```bash
source venv/bin/activate
pip install --upgrade yt-dlp
```

### Error: Nombre de archivo muy largo

**Causa**: YouTube permite títulos de 100+ caracteres.

**Solución automática**: UMD ahora trunca los nombres a 200 caracteres automáticamente. Si ves un error de "filename too long", actualiza UMD.

### Error: "Could not find ffmpeg" al convertir audio

**Solución**:
```bash
pkg install ffmpeg
ffmpeg -version  # verificar que funciona
```

### La descarga se pausa al apagar la pantalla

**Solución**:
```bash
termux-wake-lock
```
También puedes desactivar la optimización de batería para Termux en:
- **Android > Apps > Batería > Sin restricciones**

### Error de conexión / timeout

**Posibles causas**:
- Conexión lenta o inestable
- Límite de velocidad del proveedor
- Contenido geo-restringido

**Solución**: Intenta con otra URL o usa una VPN si es contenido geo-restringido.

### Los archivos no aparecen en el gestor de archivos

**Verifica la ubicación**:
```bash
ls /storage/emulated/0/Download/UniversalDownloader/
```

Si la carpeta no existe, verifica los permisos (sección 3).

---

## 8. Actualización

### Actualizar UMD

```bash
cd ~/universal-media-downloader
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
```

### Actualizar solo yt-dlp (para mantener compatibilidad con plataformas)

```bash
pip install --upgrade yt-dlp
```

> YouTube cambia frecuentemente su API; mantener yt-dlp actualizado es importante.

### Actualizar FFmpeg

```bash
pkg upgrade ffmpeg
```

---

## Notas importantes

- **No cierres Termux** mientras descarga
- **Mantén la pantalla encendida** o usa `termux-wake-lock`
- **Cookies expiradas**: exporta nuevas cada ~30 días
- **Almacenamiento**: un video de 10 min en 1080p ocupa ~200 MB; en 720p ~100 MB
- **Batería**: descargas largas consumen batería; mantén el celular cargando
