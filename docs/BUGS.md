# Bugs y errores detectados — Universal Media Downloader

Lista de problemas detectados en la CLI, separados por entorno (Termux / Terminal de escritorio). Cada bug incluye su severidad, ubicación y una propuesta de solución para trackear el arreglo en las ramas `termux` y `terminal`.

## Prioridades

- 🔴 **Crítico**: rompe la funcionalidad principal o provoca crash.
- 🟡 **Alto**: funciona parcialmente pero con errores visibles.
- 🟢 **Menor**: fallos parciales, UX o inconsistencias.

---

## Entorno Termux (rama `termux`)

### BUG-01 🔴 Crash si no hay permisos de almacenamiento
- **Archivo:** `src/main.py:97-105` y `src/core/environment.py:96`
- **Descripción:** Si el usuario acepta "continuar sin permisos" (default `True` en `main.py:93`), `downloads_path` es `None` y `self.base_path.mkdir()` lanza `AttributeError: 'NoneType' object has no attribute 'mkdir'`. La app se cae con traceback en lugar de continuar en modo local (sin almacenamiento compartido).
- **Solución propuesta:** Si no hay permisos, usar `home_path/UniversalDownloader` como `base_path` y avisar que solo se almacenará en memoria interna. No permitir continuar hacia un crash.

### BUG-02 🔴 Auto-organizar archivos usa ruta anidada incorrecta
- **Archivo:** `src/main.py:615-616` y `src/core/file_organizer.py:156`
- **Descripción:** `base_path` en Termux = `/storage/emulated/0/Download/UniversalDownloader`. `auto_organize()` pasa `.parent` (`.../Download`) como base, y `move_to_folder()` construye `.../Download/Download/UniversalDownloader` → mueve archivos a una carpeta doble errónea.
- **Solución propuesta:** Centralizar el cálculo de rutas: `move_to_folder` debe recibir `/storage/emulated/0` como base, o `auto_organize` debe pasar la raíz correcta. Eliminar `storage_base` muerto en `main.py:615`.

### BUG-03 🟡 M4A con carátula `.webp`/`.png` genera archivo corrupto
- **Archivo:** `src/core/metadata.py:182-187`
- **Descripción:** `MP4Cover` siempre se crea con `imageformat=FORMAT_JPEG`; yt-dlp suele guardar miniaturas como `.webp`, produciendo carátula/metadatos inválidos en M4A.
- **Solución propuesta:** Detectar el MIME por extensión y usar `MP4Cover.FORMAT_PNG` (o convertir a JPEG) cuando corresponda.

### BUG-04 🟢 Metadatos no soportados para OGG/WAV
- **Archivo:** `src/core/metadata.py:60-62`
- **Descripción:** `embed_metadata()` retorna `False` para `.ogg`/`.wav`; el usuario ve "No se pudieron incrustar metadatos" aunque la descarga fue exitosa.
- **Solución propuesta:** Implementar tags Vorbis para OGG/WAV con mutagen, o informar de forma clara que ese formato no lleva metadatos.

### BUG-05 🟢 Detección de Termux depende de rutas/entorno
- **Archivo:** `src/core/environment.py:66-80`
- **Descripción:** Si se ejecuta en otra app de terminal Android sin `/data/data/com.termux` y sin `TERMUX_VERSION`, se detecta como "Sistema desconocido" (sin soporte móvil).
- **Solución propuesta:** Detectar también `$ANDROID_ROOT`/`$PREFIX` y la presencia de `pkg` para identificar entornos Android alternativos.

---

## Entorno Terminal de escritorio (rama `terminal`)

### BUG-06 🟡 Detección de navegadores en Windows poco fiable
- **Archivo:** `src/core/environment.py:235`
- **Descripción:** `shutil.which("chrome")` falla en Windows porque Chrome/Edge/Opera normalmente no están en `PATH`. La opción "Extraer cookies del navegador" puede no aparecer aunque el navegador esté instalado.
- **Solución propuesta:** Verificar rutas estándar de instalación en Windows (`%LOCALAPPDATA%`, `%PROGRAMFILES%`, `%PROGRAMFILES(X86)%`).

### BUG-07 🟡 `configure_from_browser` falla si el navegador está abierto
- **Archivo:** `src/core/cookies.py:218`
- **Descripción:** Chrome/Firefox bloquean la base de datos de cookies en uso (Windows/Linux); la extracción falla sin mensaje claro.
- **Solución propuesta:** Detectar el fallo y avisar "Cierra el navegador e inténtalo de nuevo"; documentar el requisito.

### BUG-08 🟡 `test_cookies` da falsos positivos
- **Archivo:** `src/core/cookies.py:338-344`
- **Descripción:** Instagram/Facebook/TikTok se prueban contra la portada (no requiere login), por lo que cookies expiradas pueden reportarse como "válidas".
- **Solución propuesta:** Probar contra una URL autenticada o pedir al usuario una URL privada de prueba.

### BUG-09 🟡 Búsqueda por fecha sin validación
- **Archivo:** `src/main.py:428-429`
- **Descripción:** Acepta cualquier texto como fecha; una fecha inválida se compara como string en SQLite y puede devolver resultados incorrectos.
- **Solución propuesta:** Validar formato `YYYY-MM-DD` con `datetime.strptime` antes de consultar.

### BUG-10 🟢 Ruta de exportación inconsistente con README
- **Archivo:** `src/main.py:525`
- **Descripción:** El código usa `base_path.parent / "exports"` (`~/exports`) mientras el README documenta `~/UniversalDownloader/exports/[plataforma]`.
- **Solución propuesta:** Unificar a `~/UniversalDownloader/exports/` (o actualizar README).

### BUG-11 🟢 `get_failed_downloads` marca duración=0 como fallida
- **Archivo:** `src/storage/database.py:356-363`
- **Descripción:** Videos en vivo o de duración 0 que descargaron correctamente aparecen como errores y pueden borrarse del historial.
- **Solución propuesta:** Considerar solo `status = 'failed'` (y `file_path` inexistente/0 KB).

### BUG-12 🟢 Avisos de instalación de FFmpeg hardcodeados a Windows
- **Archivo:** `src/core/downloader.py:62-65`
- **Descripción:** Siempre muestra `winget install FFmpeg` y la URL de builds de Windows, incluso en Linux/macOS.
- **Solución propuesta:** Mostrar instrucciones según el SO detectado.

### BUG-13 🟢 Typer importado pero no utilizado
- **Archivo:** `src/main.py:23,37`
- **Descripción:** `typer` se importa y se crea `app` pero el flujo real es manual; si no está instalado la app no arranca innecesariamente.
- **Solución propuesta:** Eliminar la dependencia e import, o migrar el CLI a Typer de verdad.

### BUG-14 🟢 Posible `UnicodeDecodeError` en conversión FFmpeg
- **Archivo:** `src/core/converter.py:164`
- **Descripción:** `subprocess.run(..., text=True)` usa la codificación del sistema; en Windows (cp1252) puede fallar si FFmpeg emite no-UTF-8.
- **Solución propuesta:** Usar `encoding="utf-8", errors="replace"` en `subprocess.run`.

### BUG-15 🟢 Emoji/acentos distorsionados en consolas legacy
- **Archivo:** `src/main.py` (general)
- **Descripción:** En consolas Windows legacy (cmd, cp437) los emoji y caracteres especiales del menú se ven como símbolos extraños.
- **Solución propuesta:** Usar `Console(legacy_windows=True)` y/o sustituir emoji por texto en Windows.

---

## Estado de resolución

| Bug | Entorno | Rama | Estado |
|-----|---------|------|--------|
| BUG-01 | Termux | `termux` | Resuelto |
| BUG-02 | Termux | `termux` | Resuelto |
| BUG-03 | Termux | `termux` | Resuelto |
| BUG-04 | Termux | `termux` | Pendiente |
| BUG-05 | Termux | `termux` | Pendiente |
| BUG-06 | Terminal | `terminal` | Pendiente |
| BUG-07 | Terminal | `terminal` | Pendiente |
| BUG-08 | Terminal | `terminal` | Pendiente |
| BUG-09 | Terminal | `terminal` | Pendiente |
| BUG-10 | Terminal | `terminal` | Pendiente |
| BUG-11 | Terminal | `terminal` | Pendiente |
| BUG-12 | Terminal | `terminal` | Pendiente |
| BUG-13 | Terminal | `terminal` | Pendiente |
| BUG-14 | Terminal | `terminal` | Pendiente |
| BUG-15 | Terminal | `terminal` | Pendiente |
