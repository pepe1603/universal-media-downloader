"""
Módulo de base de datos SQLite.
Gestiona el historial de descargas y configuración.
"""

import sqlite3
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from rich.console import Console


class DownloadStatus(Enum):
    """Estado de una descarga."""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class DownloadRecord:
    """Registro de una descarga."""
    id: Optional[int]
    date: str
    platform: str
    title: str
    url: str
    format: str
    file_path: str
    duration: Optional[int]
    status: str
    artist: Optional[str] = None
    quality: Optional[str] = None


class Database:
    """Gestor de base de datos SQLite."""
    
    def __init__(self, db_path: Optional[Path] = None, console: Optional[Console] = None):
        self.console = console or Console()
        
        if db_path is None:
            # Ruta por defecto en el directorio del usuario
            db_path = Path.home() / "UniversalDownloader" / "umd.db"
        
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """Asegurar que el directorio de la base de datos existe."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """Inicializar la base de datos con las tablas necesarias."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de descargas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                platform TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                format TEXT NOT NULL,
                file_path TEXT NOT NULL,
                duration INTEGER,
                status TEXT NOT NULL,
                artist TEXT,
                quality TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de configuración
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                device_type TEXT NOT NULL,
                base_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_download(self, record: DownloadRecord) -> int:
        """
        Agregar un registro de descarga.
        
        Args:
            record: Registro de descarga
            
        Returns:
            ID del registro insertado
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO downloads (
                date, platform, title, url, format, file_path,
                duration, status, artist, quality
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.date,
            record.platform,
            record.title,
            record.url,
            record.format,
            record.file_path,
            record.duration,
            record.status,
            record.artist,
            record.quality
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def get_recent_downloads(self, limit: int = 20) -> List[DownloadRecord]:
        """
        Obtener descargas recientes.
        
        Args:
            limit: Número máximo de registros
            
        Returns:
            Lista de registros de descarga
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, date, platform, title, url, format, file_path,
                   duration, status, artist, quality
            FROM downloads
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        records = []
        for row in cursor.fetchall():
            records.append(DownloadRecord(
                id=row[0],
                date=row[1],
                platform=row[2],
                title=row[3],
                url=row[4],
                format=row[5],
                file_path=row[6],
                duration=row[7],
                status=row[8],
                artist=row[9],
                quality=row[10]
            ))
        
        conn.close()
        return records
    
    def search_downloads(
        self,
        platform: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        title_contains: Optional[str] = None
    ) -> List[DownloadRecord]:
        """
        Buscar descargas con filtros.
        
        Args:
            platform: Filtrar por plataforma
            date_from: Fecha desde (YYYY-MM-DD)
            date_to: Fecha hasta (YYYY-MM-DD)
            title_contains: Texto en el título
            
        Returns:
            Lista de registros de descarga
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT id, date, platform, title, url, format, file_path,
                   duration, status, artist, quality
            FROM downloads
            WHERE 1=1
        """
        params = []
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        if date_from:
            query += " AND date >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND date <= ?"
            params.append(date_to)
        
        if title_contains:
            query += " AND title LIKE ?"
            params.append(f"%{title_contains}%")
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        
        records = []
        for row in cursor.fetchall():
            records.append(DownloadRecord(
                id=row[0],
                date=row[1],
                platform=row[2],
                title=row[3],
                url=row[4],
                format=row[5],
                file_path=row[6],
                duration=row[7],
                status=row[8],
                artist=row[9],
                quality=row[10]
            ))
        
        conn.close()
        return records
    
    def get_download_by_id(self, download_id: int) -> Optional[DownloadRecord]:
        """
        Obtener una descarga por ID.
        
        Args:
            download_id: ID de la descarga
            
        Returns:
            Registro de descarga o None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, date, platform, title, url, format, file_path,
                   duration, status, artist, quality
            FROM downloads
            WHERE id = ?
        """, (download_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return DownloadRecord(
                id=row[0],
                date=row[1],
                platform=row[2],
                title=row[3],
                url=row[4],
                format=row[5],
                file_path=row[6],
                duration=row[7],
                status=row[8],
                artist=row[9],
                quality=row[10]
            )
        
        return None
    
    def get_total_downloads(self) -> int:
        """Obtener el total de descargas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM downloads")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_downloads_by_platform(self) -> dict:
        """Obtener conteo de descargas por plataforma."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT platform, COUNT(*) as count
            FROM downloads
            GROUP BY platform
            ORDER BY count DESC
        """)
        
        result = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        
        return result
    
    def delete_download(self, download_id: int) -> bool:
        """
        Eliminar un registro de descarga.
        
        Args:
            download_id: ID de la descarga
            
        Returns:
            True si se eliminó correctamente
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM downloads WHERE id = ?", (download_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
