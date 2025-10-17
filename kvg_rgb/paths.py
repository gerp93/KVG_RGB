"""
Centralized path management for KVG RGB Controller.
Defines all file and directory paths used by the application.
"""
from pathlib import Path

# Application data directory in user's home folder
DATA_DIR = Path.home() / '.kvg_rgb'

# Database file path
DATABASE_FILE = DATA_DIR / 'rgb_controller.db'

# Configuration file path (for future use)
CONFIG_FILE = DATA_DIR / 'config.json'

# Log file path (for future use)
LOG_FILE = DATA_DIR / 'kvg_rgb.log'

def ensure_data_dir():
    """Ensure the data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

__all__ = ['DATA_DIR', 'DATABASE_FILE', 'CONFIG_FILE', 'LOG_FILE', 'ensure_data_dir']
