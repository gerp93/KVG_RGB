"""
Database module for persistent color storage.
"""
import sqlite3
import os
import json
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
                    friendly_name TEXT,
                    PRIMARY KEY (device_index, zone_index)
                )
            ''')
            
            # Create effects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS effects (
                    device_index INTEGER NOT NULL,
                    zone_index INTEGER NOT NULL,
                    effect_type TEXT NOT NULL,
                    effect_params TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (device_index, zone_index)
                )
            ''')
            conn.commit()
            
            # Add friendly_name column if it doesn't exist (for existing databases)
            try:
                cursor.execute('ALTER TABLE colors ADD COLUMN friendly_name TEXT')
                conn.commit()
            except sqlite3.OperationalError:
                # Column already exists
                pass
            
            # Add brightness column if it doesn't exist (default 100%)
            try:
                cursor.execute('ALTER TABLE colors ADD COLUMN brightness INTEGER DEFAULT 100')
                conn.commit()
            except sqlite3.OperationalError:
                pass
            
            # Add saturation column if it doesn't exist (default 100%)
            try:
                cursor.execute('ALTER TABLE colors ADD COLUMN saturation INTEGER DEFAULT 100')
                conn.commit()
            except sqlite3.OperationalError:
                pass
    
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
            
            # Check if row exists to preserve brightness/saturation
            cursor.execute('''
                SELECT brightness, saturation FROM colors
                WHERE device_index = ? AND zone_index = ?
            ''', (device_index, zone_index))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing row, preserving brightness/saturation
                brightness, saturation = existing
                cursor.execute('''
                    UPDATE colors SET r = ?, g = ?, b = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE device_index = ? AND zone_index = ?
                ''', (r, g, b, device_index, zone_index))
            else:
                # Insert new row with default brightness/saturation
                cursor.execute('''
                    INSERT INTO colors (device_index, zone_index, r, g, b, brightness, saturation, updated_at)
                    VALUES (?, ?, ?, ?, ?, 100, 100, CURRENT_TIMESTAMP)
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
    
    def set_friendly_name(self, device_index: int, zone_index: int, friendly_name: str):
        """
        Set a friendly name for a zone.
        
        Args:
            device_index: Index of the device
            zone_index: Index of the zone
            friendly_name: User-friendly name for the zone
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if row exists
            cursor.execute('''
                SELECT r, g, b FROM colors
                WHERE device_index = ? AND zone_index = ?
            ''', (device_index, zone_index))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing row
                cursor.execute('''
                    UPDATE colors SET friendly_name = ?
                    WHERE device_index = ? AND zone_index = ?
                ''', (friendly_name, device_index, zone_index))
            else:
                # Insert new row with default black color
                cursor.execute('''
                    INSERT INTO colors (device_index, zone_index, r, g, b, friendly_name)
                    VALUES (?, ?, 0, 0, 0, ?)
                ''', (device_index, zone_index, friendly_name))
            
            conn.commit()
    
    def get_friendly_name(self, device_index: int, zone_index: int) -> Optional[str]:
        """
        Get the friendly name for a zone.
        
        Args:
            device_index: Index of the device
            zone_index: Index of the zone
            
        Returns:
            Friendly name if set, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT friendly_name FROM colors
                WHERE device_index = ? AND zone_index = ?
            ''', (device_index, zone_index))
            result = cursor.fetchone()
            return result[0] if result and result[0] else None
    
    def get_all_friendly_names(self) -> List[Tuple[int, int, str]]:
        """
        Get all friendly names.
        
        Returns:
            List of tuples (device_index, zone_index, friendly_name)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT device_index, zone_index, friendly_name FROM colors
                WHERE friendly_name IS NOT NULL AND friendly_name != ''
            ''')
            return cursor.fetchall()
    
    def set_brightness_saturation(self, device_index: int, zone_index: int, brightness: int, saturation: int):
        """
        Set brightness and saturation for a zone.
        
        Args:
            device_index: Index of the device
            zone_index: Index of the zone
            brightness: Brightness percentage (0-100)
            saturation: Saturation percentage (0-100)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if row exists
            cursor.execute('''
                SELECT r, g, b FROM colors
                WHERE device_index = ? AND zone_index = ?
            ''', (device_index, zone_index))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing row
                cursor.execute('''
                    UPDATE colors SET brightness = ?, saturation = ?
                    WHERE device_index = ? AND zone_index = ?
                ''', (brightness, saturation, device_index, zone_index))
            else:
                # Insert new row with default black color
                cursor.execute('''
                    INSERT INTO colors (device_index, zone_index, r, g, b, brightness, saturation)
                    VALUES (?, ?, 0, 0, 0, ?, ?)
                ''', (device_index, zone_index, brightness, saturation))
            
            conn.commit()
    
    def get_brightness_saturation(self, device_index: int, zone_index: int) -> Tuple[int, int]:
        """
        Get brightness and saturation for a zone.
        
        Args:
            device_index: Index of the device
            zone_index: Index of the zone
            
        Returns:
            Tuple of (brightness, saturation) percentages, defaults to (100, 100)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT brightness, saturation FROM colors
                WHERE device_index = ? AND zone_index = ?
            ''', (device_index, zone_index))
            result = cursor.fetchone()
            
            if result and result[0] is not None and result[1] is not None:
                return (result[0], result[1])
            else:
                return (100, 100)  # Default to 100% brightness and saturation

    def set_effect(self, device_index: int, zone_index: int, effect_type: str, effect_params: Optional[str] = None):
        """
        Set an effect for a zone.
        
        Args:
            device_index: Index of the device
            zone_index: Index of the zone
            effect_type: Type of effect ('static', 'rainbow', 'breathing', 'wave', 'cycle', etc.)
            effect_params: JSON string with effect parameters (speed, color, etc.)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO effects (device_index, zone_index, effect_type, effect_params, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (device_index, zone_index, effect_type, effect_params))
            conn.commit()
    
    def get_effect(self, device_index: int, zone_index: int) -> Optional[Tuple[str, Optional[str]]]:
        """
        Get the active effect for a zone.
        
        Args:
            device_index: Index of the device
            zone_index: Index of the zone
            
        Returns:
            Tuple of (effect_type, effect_params) if found, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT effect_type, effect_params FROM effects
                WHERE device_index = ? AND zone_index = ?
            ''', (device_index, zone_index))
            result = cursor.fetchone()
            return tuple(result) if result else None
    
    def clear_effect(self, device_index: int, zone_index: int):
        """
        Clear the effect for a zone (sets to static).
        
        Args:
            device_index: Index of the device
            zone_index: Index of the zone
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM effects
                WHERE device_index = ? AND zone_index = ?
            ''', (device_index, zone_index))
            conn.commit()
    
    def get_all_effects(self) -> List[Tuple[int, int, str, Optional[str]]]:
        """
        Get all active effects.
        
        Returns:
            List of tuples (device_index, zone_index, effect_type, effect_params)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT device_index, zone_index, effect_type, effect_params FROM effects
                ORDER BY device_index, zone_index
            ''')
            return cursor.fetchall()
