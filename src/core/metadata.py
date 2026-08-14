"""
Módulo de metadatos de audio.
Incrusta carátulas e información ID3 en archivos de audio.
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from rich.console import Console


@dataclass
class AudioMetadata:
    """Metadatos de un archivo de audio."""
    title: str
    artist: str = "Desconocido"
    album: str = "Single"
    date: Optional[str] = None
    genre: Optional[str] = None
    cover_path: Optional[Path] = None


class MetadataHandler:
    """Manejador de metadatos de audio."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    def embed_metadata(
        self,
        audio_path: Path,
        metadata: AudioMetadata
    ) -> bool:
        """
        Incrustar metadatos en un archivo de audio.
        
        Args:
            audio_path: Ruta del archivo de audio
            metadata: Metadatos a incrustar
            
        Returns:
            True si fue exitoso
        """
        try:
            # Verificar que el archivo existe
            if not audio_path.exists():
                self.console.print(f"[red]✗ Archivo no encontrado: {audio_path}[/red]")
                return False
            
            ext = audio_path.suffix.lower()
            
            if ext == ".mp3":
                return self._embed_mp3(audio_path, metadata)
            elif ext == ".m4a":
                return self._embed_m4a(audio_path, metadata)
            elif ext == ".flac":
                return self._embed_flac(audio_path, metadata)
            elif ext == ".ogg":
                return self._embed_ogg(audio_path, metadata)
            elif ext == ".wav":
                return self._embed_wav(audio_path, metadata)
            else:
                self.console.print(f"[yellow]⚠ Metadatos no soportados para {ext}[/yellow]")
                return False
        
        except Exception as e:
            self.console.print(f"[red]Error al incrustar metadatos: {e}[/red]")
            import traceback
            traceback.print_exc()
            return False
    
    def _embed_mp3(self, audio_path: Path, metadata: AudioMetadata) -> bool:
        """Incrustar metadatos en archivo MP3 usando mutagen."""
        try:
            from mutagen.mp3 import MP3
            from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, APIC
            
            self.console.print(f"[dim]  Procesando MP3: {audio_path.name}[/dim]")
            
            # Cargar archivo MP3
            audio = MP3(audio_path, ID3=ID3)
            
            # Si no tiene tags, crearlos
            if audio.tags is None:
                self.console.print(f"[dim]  Creando tags ID3 nuevos[/dim]")
                audio.add_tags()
            
            tags = audio.tags
            
            # Agregar metadatos de texto (encoding=3 para UTF-8)
            self.console.print(f"[dim]  Agregando título: {metadata.title}[/dim]")
            tags.add(TIT2(encoding=3, text=metadata.title))
            
            self.console.print(f"[dim]  Agregando artista: {metadata.artist}[/dim]")
            tags.add(TPE1(encoding=3, text=metadata.artist))
            
            self.console.print(f"[dim]  Agregando álbum: {metadata.album}[/dim]")
            tags.add(TALB(encoding=3, text=metadata.album))
            
            if metadata.date:
                self.console.print(f"[dim]  Agregando fecha: {metadata.date}[/dim]")
                tags.add(TDRC(encoding=3, text=metadata.date))
            
            if metadata.genre:
                tags.add(TCON(encoding=3, text=metadata.genre))
            
            # Agregar carátula si existe
            if metadata.cover_path:
                self.console.print(f"[dim]  Buscando carátula: {metadata.cover_path}[/dim]")
                
                if metadata.cover_path.exists():
                    self.console.print(f"[dim]  ✓ Carátula encontrada, tamaño: {metadata.cover_path.stat().st_size} bytes[/dim]")
                    
                    with open(metadata.cover_path, "rb") as img:
                        img_data = img.read()
                        self.console.print(f"[dim]  Leyendo {len(img_data)} bytes de la imagen[/dim]")
                        
                        # Determinar MIME type
                        mime = "image/jpeg"
                        if metadata.cover_path.suffix.lower() in ['.png']:
                            mime = "image/png"
                        elif metadata.cover_path.suffix.lower() in ['.webp']:
                            mime = "image/webp"
                        
                        # IMPORTANTE: Usar encoding=0 (Latin-1) para APIC para máxima compatibilidad
                        # El campo desc debe ser Latin-1, no UTF-8
                        tags.add(APIC(
                            encoding=0,  # Latin-1 para máxima compatibilidad
                            mime=mime,
                            type=3,  # Cover (front)
                            desc="Cover",  # Descripción simple en Latin-1
                            data=img_data
                        ))
                        self.console.print(f"[dim]  ✓ Carátula agregada al tag[/dim]")
                else:
                    self.console.print(f"[yellow]  ⚠ Carátula no encontrada en: {metadata.cover_path}[/yellow]")
            else:
                self.console.print(f"[yellow]  ⚠ No se proporcionó ruta de carátula[/yellow]")
            
            # Guardar cambios
            self.console.print(f"[dim]  Guardando cambios...[/dim]")
            audio.save()
            
            # Verificar que se guardó correctamente
            audio_check = MP3(audio_path)
            if audio_check.tags:
                apic_tags = [tag for tag in audio_check.tags.values() if hasattr(tag, 'FrameID') and tag.FrameID == 'APIC']
                if apic_tags:
                    self.console.print(f"[green]  ✓ Verificación: Carátula confirmada en el archivo[/green]")
                    return True
            
            self.console.print(f"[yellow]  ⚠ Advertencia: La carátula podría no haberse guardado[/yellow]")
            return True  # Aún así retornamos True porque los otros metadatos sí se guardaron
        
        except ImportError as e:
            self.console.print(f"[red]Error de importación: {e}[/red]")
            self.console.print("[yellow]⚠ Ejecuta: pip install mutagen[/yellow]")
            return False
        except Exception as e:
            self.console.print(f"[red]Error en MP3: {e}[/red]")
            import traceback
            traceback.print_exc()
            return False
    
    def _embed_m4a(self, audio_path: Path, metadata: AudioMetadata) -> bool:
        """Incrustar metadatos en archivo M4A usando mutagen."""
        try:
            from mutagen.mp4 import MP4, MP4Cover
            
            audio = MP4(audio_path)
            
            # Metadatos básicos
            audio["\xa9nam"] = metadata.title
            audio["\xa9ART"] = metadata.artist
            audio["\xa9alb"] = metadata.album
            
            if metadata.date:
                audio["\xa9day"] = metadata.date
            
            if metadata.genre:
                audio["\xa9gen"] = metadata.genre
            
            # Agregar carátula
            if metadata.cover_path and metadata.cover_path.exists():
                cover_data, cover_format = self._prepare_cover_for_m4a(metadata.cover_path)
                if cover_data and cover_format is not None:
                    audio["covr"] = [
                        MP4Cover(cover_data, imageformat=cover_format)
                    ]
            
            audio.save()
            return True
        
        except ImportError as e:
            self.console.print(f"[red]Error de importación: {e}[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]Error en M4A: {e}[/red]")
            return False

    def _prepare_cover_for_m4a(self, cover_path: Path):
        """
        Preparar carátula para incrustar en M4A.

        Devuelve (datos, imageformat) usando el formato correcto según el tipo
        de imagen. Las imágenes WEBP no son soportadas por MP4Cover, por lo que
        se convierten a JPEG con FFmpeg. Devuelve (None, None) si falla.
        """
        import subprocess
        from mutagen.mp4 import MP4Cover

        suffix = cover_path.suffix.lower()

        try:
            if suffix == ".png":
                with open(cover_path, "rb") as img:
                    return img.read(), MP4Cover.FORMAT_PNG

            if suffix in (".jpg", ".jpeg"):
                with open(cover_path, "rb") as img:
                    return img.read(), MP4Cover.FORMAT_JPEG

            # WEBP u otro formato: convertir a JPEG con FFmpeg
            self.console.print(f"[dim]  Convirtiendo carátula {suffix} a JPEG para M4A...[/dim]")
            temp_jpeg = cover_path.with_name(f"{cover_path.stem}_umd_cover.jpg")
            try:
                result = subprocess.run(
                    ["ffmpeg", "-y", "-i", str(cover_path), "-q:v", "2", str(temp_jpeg)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0 and temp_jpeg.exists():
                    with open(temp_jpeg, "rb") as img:
                        data = img.read()
                    return data, MP4Cover.FORMAT_JPEG
            finally:
                if temp_jpeg.exists():
                    try:
                        temp_jpeg.unlink()
                    except Exception:
                        pass
        except Exception as e:
            self.console.print(f"[yellow]  ⚠ No se pudo preparar la carátula para M4A: {e}[/yellow]")

        return None, None
    
    def _embed_flac(self, audio_path: Path, metadata: AudioMetadata) -> bool:
        """Incrustar metadatos en archivo FLAC usando mutagen."""
        try:
            from mutagen.flac import FLAC, Picture
            
            audio = FLAC(audio_path)
            
            # Metadatos básicos (Vorbis comments)
            audio["title"] = metadata.title
            audio["artist"] = metadata.artist
            audio["album"] = metadata.album
            
            if metadata.date:
                audio["date"] = metadata.date
            
            if metadata.genre:
                audio["genre"] = metadata.genre
            
            # Agregar carátula
            if metadata.cover_path and metadata.cover_path.exists():
                picture = Picture()
                picture.type = 3  # Cover (front)
                picture.mime = "image/jpeg"
                picture.desc = "Cover"
                
                with open(metadata.cover_path, "rb") as img:
                    picture.data = img.read()
                
                audio.add_picture(picture)
            
            audio.save()
            return True
        
        except ImportError as e:
            self.console.print(f"[red]Error de importación: {e}[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]Error en FLAC: {e}[/red]")
            return False

    def _embed_ogg(self, audio_path: Path, metadata: AudioMetadata) -> bool:
        """Incrustar metadatos en archivo OGG (Vorbis comments) usando mutagen."""
        try:
            import base64
            from mutagen.oggvorbis import OggVorbis
            from mutagen.flac import Picture

            audio = OggVorbis(audio_path)

            audio["title"] = metadata.title
            audio["artist"] = metadata.artist
            audio["album"] = metadata.album

            if metadata.date:
                audio["date"] = metadata.date

            if metadata.genre:
                audio["genre"] = metadata.genre

            # Carátula: METADATA_BLOCK_PICTURE (Picture de FLAC en base64)
            if metadata.cover_path and metadata.cover_path.exists():
                picture = Picture()
                picture.type = 3  # Cover (front)
                picture.desc = "Cover"
                picture.mime = "image/jpeg"
                suffix = metadata.cover_path.suffix.lower()
                if suffix == ".png":
                    picture.mime = "image/png"
                elif suffix == ".webp":
                    picture.mime = "image/webp"

                with open(metadata.cover_path, "rb") as img:
                    picture.data = img.read()

                audio["metadata_block_picture"] = [
                    base64.b64encode(picture.write()).decode("ascii")
                ]

            audio.save()
            return True

        except ImportError as e:
            self.console.print(f"[red]Error de importación: {e}[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]Error en OGG: {e}[/red]")
            return False

    def _embed_wav(self, audio_path: Path, metadata: AudioMetadata) -> bool:
        """Incrustar metadatos en archivo WAV (tags ID3) usando mutagen."""
        try:
            from mutagen.wave import WAVE
            from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, APIC

            audio = WAVE(audio_path)

            if audio.tags is None:
                audio.add_tags()

            tags = audio.tags
            tags.add(TIT2(encoding=3, text=metadata.title))
            tags.add(TPE1(encoding=3, text=metadata.artist))
            tags.add(TALB(encoding=3, text=metadata.album))

            if metadata.date:
                tags.add(TDRC(encoding=3, text=metadata.date))

            if metadata.genre:
                tags.add(TCON(encoding=3, text=metadata.genre))

            # Carátula
            if metadata.cover_path and metadata.cover_path.exists():
                with open(metadata.cover_path, "rb") as img:
                    img_data = img.read()

                mime = "image/jpeg"
                suffix = metadata.cover_path.suffix.lower()
                if suffix == ".png":
                    mime = "image/png"
                elif suffix == ".webp":
                    mime = "image/webp"

                tags.add(APIC(
                    encoding=0,  # Latin-1 para máxima compatibilidad
                    mime=mime,
                    type=3,  # Cover (front)
                    desc="Cover",
                    data=img_data
                ))

            audio.save()
            return True

        except ImportError as e:
            self.console.print(f"[red]Error de importación: {e}[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]Error en WAV: {e}[/red]")
            return False
