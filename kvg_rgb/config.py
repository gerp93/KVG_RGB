"""
Configuration management for KVG RGB Controller
Stores user preferences like excluded devices
"""
import json
import os
from pathlib import Path


class Config:
    """Manage configuration settings"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.kvg_rgb'
        self.config_file = self.config_dir / 'config.json'
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            'excluded_devices': []
        }
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def get_excluded_devices(self):
        """Get list of excluded device names"""
        return self.config.get('excluded_devices', [])
    
    def is_device_excluded(self, device_name):
        """Check if a device is excluded"""
        return device_name in self.get_excluded_devices()
    
    def exclude_device(self, device_name):
        """Add a device to the exclusion list"""
        excluded = self.get_excluded_devices()
        if device_name not in excluded:
            excluded.append(device_name)
            self.config['excluded_devices'] = excluded
            self._save_config()
            return True
        return False
    
    def include_device(self, device_name):
        """Remove a device from the exclusion list"""
        excluded = self.get_excluded_devices()
        if device_name in excluded:
            excluded.remove(device_name)
            self.config['excluded_devices'] = excluded
            self._save_config()
            return True
        return False
    
    def toggle_device(self, device_name):
        """Toggle device exclusion status"""
        if self.is_device_excluded(device_name):
            self.include_device(device_name)
            return False  # Now included
        else:
            self.exclude_device(device_name)
            return True  # Now excluded


# Global config instance
_config = None

def get_config():
    """Get the global config instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config
