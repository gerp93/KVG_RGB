"""
Centralized path management for KVG RGB Controller.
Defines all file and directory paths used by the application.
"""
from pathlib import Path
from kvg_dblocation import DbLocation

# Application data directory in user's home folder
DATA_DIR = Path.home() / '.kvg_rgb'

# Relocatable database location (see KVG_Standards' db-location-versioning.md).
# Default path is DATA_DIR / 'rgb_controller.db'; the user can point it
# elsewhere via Settings, tracked in DATA_DIR / 'db_location.json'.
db_location = DbLocation(data_dir=DATA_DIR, default_filename='rgb_controller.db')

# Database file path — the *effective* path (default, or user-relocated)
DATABASE_FILE = db_location.get_effective_db_path()

# Configuration file path (for future use)
CONFIG_FILE = DATA_DIR / 'config.json'

# Log file path (for future use)
LOG_FILE = DATA_DIR / 'kvg_rgb.log'

def ensure_data_dir():
    """Ensure the data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

__all__ = ['DATA_DIR', 'DATABASE_FILE', 'CONFIG_FILE', 'LOG_FILE', 'db_location', 'ensure_data_dir']
