"""
Database module for persistent color storage.
"""
import sqlite3
import os
from pathlib import Path
from typing import Optional, Tuple, List


class ColorDatabase:
    """Manages persistent storage of device and zone colors."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the color database.
        
        Args:
            db_path: Path to the SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Use ~/.kvg_rgb/colors.db by default
            config_dir = Path.home() / '.kvg_rgb'
            config_dir.mkdir(exist_ok=True)
            db_path = str(config_dir / 'colors.db')
        
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Create the database schema if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS colors (
                    device_index INTEGER NOT NULL,
                    zone_index INTEGER NOT NULL,
                    r INTEGER NOT NULL,
                    g INTEGER NOT NULL,
                    b INTEGER NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (device_index, zone_index)
                )
            ''')
            conn.commit()
    
    def set_color(self, device_index: int, zone_index: int, r: int, g: int, b: int):
        """
        Store a color for a specific device zone.
        
        Args:
            device_index: Index of the device
            zone_index: Index of the zone (-1 for entire device)
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO colors (device_index, zone_index, r, g, b, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (device_index, zone_index, r, g, b))
            conn.commit()
    
    def get_color(self, device_index: int, zone_index: int) -> Optional[Tuple[int, int, int]]:
        """
        Retrieve the stored color for a specific device zone.
        
        Args:
            device_index: Index of the device
            zone_index: Index of the zone (-1 for entire device)
        
        Returns:
            Tuple of (r, g, b) if found, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r, g, b FROM colors
                WHERE device_index = ? AND zone_index = ?
            ''', (device_index, zone_index))
            result = cursor.fetchone()
            return tuple(result) if result else None
    
    def get_device_colors(self, device_index: int) -> List[Tuple[int, int, int, int]]:
        """
        Retrieve all stored colors for a device.
        
        Args:
            device_index: Index of the device
        
        Returns:
            List of tuples (zone_index, r, g, b) for actual zones only (excludes zone_index = -1)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT zone_index, r, g, b FROM colors
                WHERE device_index = ? AND zone_index >= 0
                ORDER BY zone_index
            ''', (device_index,))
            return cursor.fetchall()
    
    def clear_device_colors(self, device_index: int):
        """
        Remove all stored colors for a device.
        
        Args:
            device_index: Index of the device
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM colors WHERE device_index = ?
            ''', (device_index,))
            conn.commit()
    
    def clear_all_colors(self):
        """Remove all stored colors from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM colors')
            conn.commit()
