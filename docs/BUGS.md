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
- **Solución aplicada:** `_is_termux` ahora también devuelve `True` si existen `$ANDROID_ROOT`/`$ANDROID_DATA` (presentes en toda Android), cubriendo UserLAnd, proot y terminales Android alternativos. `_get_termux_info` usa `/storage/emulated/0`, estándar en todas ellas.

---

## Entorno Terminal de escritorio (rama `terminal`)

### BUG-06 🟡 Detección de navegadores en Windows poco fiable
- **Archivo:** `src/core/environment.py:235`
- **Descripción:** `shutil.which("chrome")` falla en Windows porque Chrome/Edge/Opera normalmente no están en `PATH`. La opción "Extraer cookies del navegador" puede no aparecer aunque el navegador esté instalado.
- **Solución aplicada:** Verificar también rutas estándar de instalación en Windows (`%LOCALAPPDATA%`, `%PROGRAMFILES%`, `%PROGRAMFILES(X86)%`). Verificado: detecta Chrome, Edge y Brave que antes no aparecían.

### BUG-07 🟡 `configure_from_browser` falla si el navegador está abierto
- **Archivo:** `src/core/cookies.py:218`
- **Descripción:** Chrome/Firefox bloquean la base de datos de cookies en uso (Windows/Linux); la extracción falla sin mensaje claro.
- **Solución aplicada:** Se clasifica el error y se muestra un mensaje accionable: navegador en uso → "cierra el navegador"; problemas de cifrado/llave → "usa cookies.txt"; perfil no accesible → "inicia sesión o usa cookies.txt".

### BUG-08 🟡 `test_cookies` da falsos positivos
- **Archivo:** `src/core/cookies.py:338-344`
- **Descripción:** Instagram/Facebook/TikTok se prueban contra la portada (no requiere login), por lo que cookies expiradas pueden reportarse como "válidas".
- **Solución aplicada:** La prueba ahora hace una petición HTTP autenticada a una página de cuenta (YouTube `/account`, Instagram `/accounts/edit/`, Facebook `/settings`, TikTok `/upload`) y detecta redirección a login o marcadores de sesión en la respuesta. Verificado: cookies falsas se detectan como inválidas en YouTube e Instagram.

### BUG-09 🟡 Búsqueda por fecha sin validación
- **Archivo:** `src/main.py:441-470`
- **Descripción:** Acepta cualquier texto como fecha; una fecha inválida se compara como string en SQLite y puede devolver resultados incorrectos.
- **Solución aplicada:** Nuevo helper `_ask_valid_date` que valida el formato `YYYY-MM-DD` con `datetime.strptime` antes de consultar; si es inválido pide la fecha de nuevo.

### BUG-10 🟢 Ruta de exportación inconsistente con README
- **Archivo:** `src/main.py:553`
- **Descripción:** El código usa `base_path.parent / "exports"` (`~/exports`) mientras el README documenta `~/UniversalDownloader/exports/[plataforma]`.
- **Solución aplicada:** Se unifica a `~/UniversalDownloader/exports/` y se actualiza el README (sin subcarpeta `[plataforma]`, que no existe en el código, y ruta móvil corregida a `/storage/emulated/0/Download/UniversalDownloader/exports/`).

### BUG-11 🟢 `get_failed_downloads` marca duración=0 como fallida
- **Archivo:** `src/storage/database.py:346-405`
- **Descripción:** Videos en vivo o de duración 0 que descargaron correctamente aparecen como errores y pueden borrarse del historial.
- **Solución aplicada:** Las consultas (`get_failed_downloads` y `delete_failed_downloads`) ya no consideran `duration = 0/IS NULL`; ahora usan `status = 'failed'` o `file_path = 'N/A'/''` (cómo se guardan realmente las fallidas). Verificado: un directo descargado con éxito (duración 0) ya no se marca fallido.

### BUG-12 🟢 Avisos de instalación de FFmpeg hardcodeados a Windows
- **Archivo:** `src/core/downloader.py:62-66`
- **Descripción:** Siempre muestra `winget install FFmpeg` y la URL de builds de Windows, incluso en Linux/macOS.
- **Solución aplicada:** Nuevo helper `_ffmpeg_install_hints()` que muestra instrucciones según el SO (Windows: winget/gyan.dev; macOS: brew; Linux: apt/dnf/pacman; Termux: pkg).

### BUG-13 🟢 Typer importado pero no utilizado
- **Archivo:** `src/main.py:23,37`
- **Descripción:** `typer` se importa y se crea `app` pero el flujo real es manual; si no está instalado la app no arranca innecesariamente.
- **Solución aplicada:** Se eliminaron el import de `typer`, la instancia `app` y la dependencia de `requirements.txt`, `requirements.lock` y README. La app arranca sin typer instalado.

### BUG-14 🟢 Posible `UnicodeDecodeError` en conversión FFmpeg
- **Archivo:** `src/core/converter.py:164`
- **Descripción:** `subprocess.run(..., text=True)` usa la codificación del sistema; en Windows (cp1252) puede fallar si FFmpeg emite no-UTF-8.
- **Solución aplicada:** `encoding="utf-8", errors="replace"` en `subprocess.run`.

### BUG-15 🔴 Crash en todas las descargas en consolas Windows legacy (cp1252)
- **Archivo:** `src/core/downloader.py:170` y `src/main.py` (creación de `Console()`)
- **Descripción:** El `SpinnerColumn()` de la barra de progreso renderiza caracteres braille (p. ej. `\u280b`). En consolas Windows sin VT/UTF-8 (cmd, cp437/cp1252), `Console().legacy_windows` es `True` y el renderer legacy escribe el carácter a `sys.stdout` (TextIOWrapper cp1252), que lanza `UnicodeEncodeError: 'charmap' codec can't encode character`. `downloader.py:297-301` lo captura como "Error inesperado" y marca la descarga como **fallida aunque el archivo se descargó correctamente** (falso negativo que afecta a todas las descargas).
- **Solución aplicada:** Reconfigurar `sys.stdout`/`sys.stderr` a UTF-8 al inicio de `src/main.py`, **antes** de crear `Console()` (Rich captura la codificación al construirse). Verificado: sin fix → `UnicodeEncodeError`; con fix → descarga reportada como éxito y spinner renderiza correctamente.

---

## Estado de resolución

| Bug | Entorno | Rama | Estado |
|-----|---------|------|--------|
| BUG-01 | Termux | `termux` | Resuelto |
| BUG-02 | Termux | `termux` | Resuelto |
| BUG-03 | Termux | `termux` | Resuelto |
| BUG-04 | Termux | `termux` | Resuelto |
| BUG-05 | Termux | `termux` | Resuelto |
| BUG-06 | Terminal | `terminal` | Resuelto |
| BUG-07 | Terminal | `terminal` | Resuelto |
| BUG-08 | Terminal | `terminal` | Resuelto |
| BUG-09 | Terminal | `terminal` | Resuelto |
| BUG-10 | Terminal | `terminal` | Resuelto |
| BUG-11 | Terminal | `terminal` | Resuelto |
| BUG-12 | Terminal | `terminal` | Resuelto |
| BUG-13 | Terminal | `terminal` | Resuelto |
| BUG-14 | Terminal | `terminal` | Resuelto |
| BUG-15 | Terminal | `terminal` | Resuelto |
