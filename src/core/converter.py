"""
Módulo de conversión de audio.
Convierte archivos de audio a diferentes formatos usando FFmpeg.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum

from rich.console import Console


class AudioFormat(Enum):
    """Formatos de audio soportados."""
    MP3 = "mp3"
    M4A = "m4a"
    FLAC = "flac"
    OGG = "ogg"
    WAV = "wav"
    
    @property
    def description(self) -> str:
        """Descripción del formato."""
        descriptions = {
            AudioFormat.MP3: "MP3 (Recomendado - Compatible)",
            AudioFormat.M4A: "M4A (Apple/iOS)",
            AudioFormat.FLAC: "FLAC (Sin pérdida)",
            AudioFormat.OGG: "OGG (Código abierto)",
            AudioFormat.WAV: "WAV (Sin comprimir)",
        }
        return descriptions[self]
    
    @property
    def bitrate(self) -> str:
        """Bitrate recomendado para el formato."""
        bitrates = {
            AudioFormat.MP3: "192k",
            AudioFormat.M4A: "256k",
            AudioFormat.FLAC: "0",  # Calidad máxima (0-10, menor = mejor)
            AudioFormat.OGG: "192k",
            AudioFormat.WAV: "1411k",  # CD quality
        }
        return bitrates[self]


@dataclass
class ConversionResult:
    """Resultado de una conversión."""
    success: bool
    output_path: Optional[Path] = None
    error_message: Optional[str] = None


class AudioConverter:
    """Conversor de audio usando FFmpeg."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    def _check_ffmpeg(self) -> bool:
        """Verificar que FFmpeg esté disponible."""
        return shutil.which("ffmpeg") is not None
    
    def _build_ffmpeg_command(
        self,
        input_path: Path,
        output_path: Path,
        audio_format: AudioFormat
    ) -> list[str]:
        """
        Construir comando de FFmpeg para conversión.
        
        Args:
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida
            audio_format: Formato de destino
            
        Returns:
            Lista con el comando y argumentos
        """
        cmd = ["ffmpeg", "-i", str(input_path), "-y"]  # -y = sobrescribir
        
        if audio_format == AudioFormat.MP3:
            cmd.extend([
                "-codec:a", "libmp3lame",
                "-b:a", audio_format.bitrate,
                "-map_metadata", "0",  # Preservar metadatos
            ])
        
        elif audio_format == AudioFormat.M4A:
            cmd.extend([
                "-codec:a", "aac",
                "-b:a", audio_format.bitrate,
                "-movflags", "+faststart",
            ])
        
        elif audio_format == AudioFormat.FLAC:
            cmd.extend([
                "-codec:a", "flac",
                "-compression_level", "8",  # Máxima compresión
            ])
        
        elif audio_format == AudioFormat.OGG:
            cmd.extend([
                "-codec:a", "libvorbis",
                "-b:a", audio_format.bitrate,
            ])
        
        elif audio_format == AudioFormat.WAV:
            cmd.extend([
                "-codec:a", "pcm_s16le",  # 16-bit PCM
                "-ar", "44100",  # 44.1 kHz
            ])
        
        cmd.append(str(output_path))
        return cmd
    
    def convert(
        self,
        input_path: Path,
        output_format: AudioFormat,
        output_dir: Optional[Path] = None
    ) -> ConversionResult:
        """
        Convertir archivo de audio a otro formato.
        
        Args:
            input_path: Ruta del archivo de entrada
            output_format: Formato de destino
            output_dir: Directorio de salida (opcional, usa el mismo que input)
            
        Returns:
            ConversionResult con el resultado
        """
        if not self._check_ffmpeg():
            return ConversionResult(
                success=False,
                error_message="FFmpeg no está instalado"
            )
        
        if not input_path.exists():
            return ConversionResult(
                success=False,
                error_message=f"Archivo no encontrado: {input_path}"
            )
        
        try:
            # Determinar directorio de salida
            if output_dir is None:
                output_dir = input_path.parent
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Construir ruta de salida
            output_path = output_dir / f"{input_path.stem}.{output_format.value}"
            
            # Construir comando
            cmd = self._build_ffmpeg_command(input_path, output_path, output_format)
            
            # Ejecutar conversión
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0 and output_path.exists():
                return ConversionResult(
                    success=True,
                    output_path=output_path
                )
            else:
                return ConversionResult(
                    success=False,
                    error_message=f"Error en conversión: {result.stderr[:200]}"
                )
        
        except subprocess.TimeoutExpired:
            return ConversionResult(
                success=False,
                error_message="Tiempo de conversión excedido"
            )
        except Exception as e:
            return ConversionResult(
                success=False,
                error_message=f"Error inesperado: {str(e)}"
            )
    
    def get_supported_formats(self) -> list[AudioFormat]:
        """Obtener lista de formatos soportados."""
        return list(AudioFormat)

