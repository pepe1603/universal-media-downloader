# Platform rules
- Detect environment via src/core/environment.py.
- Support Termux, Windows, Linux, macOS.
- Don't assume UTF-8 console (handle legacy Windows).
- Use OS-specific install hints (FFmpeg etc.).
- Termux paths: /storage/emulated/0/Download/UniversalDownloader.