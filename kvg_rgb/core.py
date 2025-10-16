"""
Core RGB control functionality (can be used by CLI or GUI)
"""
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
from .config import get_config
from .database import ColorDatabase
import time
import math
import sys
import logging
import colorsys
import threading
import json

logger = logging.getLogger(__name__)


def apply_brightness_saturation(r, g, b, brightness=100, saturation=100):
    """
    Apply brightness and saturation adjustments to RGB color.
    
    Args:
        r, g, b: RGB values (0-255)
        brightness: Brightness percentage (0-100)
        saturation: Saturation percentage (0-100)
        
    Returns:
        Tuple of adjusted (r, g, b) values
    """
    # Convert RGB to HSV
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
    
    # Apply saturation (0-100% -> 0.0-1.0)
    s = s * (saturation / 100.0)
    
    # Apply brightness (0-100% -> 0.0-1.0)
    v = v * (brightness / 100.0)
    
    # Convert back to RGB
    r_adj, g_adj, b_adj = colorsys.hsv_to_rgb(h, s, v)
    
    return (
        int(r_adj * 255),
        int(g_adj * 255),
        int(b_adj * 255)
    )


class RGBController:
    """Core RGB controller class"""
    
    def __init__(self, host='localhost', port=6742):
        """Initialize connection to OpenRGB"""
        self.client = OpenRGBClient(name="KVG_RGB", address=host, port=port)
        self.config = get_config()
        # Use database for persistent color storage
        self.db = ColorDatabase()
        
    def disconnect(self):
        """Disconnect from OpenRGB"""
        self.client.disconnect()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    
    def get_devices(self, include_excluded=False):
        """
        Get list of RGB devices
        
        Args:
            include_excluded: If True, return all devices. If False, filter out excluded ones.
        """
        devices = self.client.devices
        if include_excluded:
            return devices
        return [d for d in devices if not self.config.is_device_excluded(d.name)]
    
    def get_all_devices(self):
        """Get all devices including excluded ones (for management UI)"""
        return self.client.devices
    
    def set_color(self, r, g, b, device_index=None):
        """
        Set device(s) to a specific color
        
        Args:
            r, g, b: RGB values (0-255)
            device_index: Specific device index, or None for all devices
        """
        if device_index is not None:
            device = self.client.devices[device_index]
            # Check if device is excluded
            if self.config.is_device_excluded(device.name):
                return  # Skip excluded device
            logger.warning(f"\n🎨 Setting device color for {device.name}")
            logger.warning(f"   Color: RGB({r}, {g}, {b})")
            # Save device color to database for EVERY zone
            logger.warning(f"   Saving to DB for {len(device.zones)} zones:")
            for zone_idx in range(len(device.zones)):
                self.db.set_color(device_index, zone_idx, r, g, b)
                logger.warning(f"   ✓ Zone {zone_idx} → RGB({r}, {g}, {b})")
            # Switch to Direct mode if available
            self._set_direct_mode(device)
            # Re-fetch device after mode change
            device = self.client.devices[device_index]
            
            # Apply brightness/saturation per zone
            logger.warning(f"   Applying brightness/saturation to zones:")
            for zone_idx in range(len(device.zones)):
                # Get brightness and saturation for this zone
                brightness, saturation = self.db.get_brightness_saturation(device_index, zone_idx)
                
                # Apply brightness and saturation adjustments
                adj_r, adj_g, adj_b = apply_brightness_saturation(r, g, b, brightness, saturation)
                
                logger.warning(f"   Zone {zone_idx}: RGB({r}, {g}, {b}) → RGB({adj_r}, {adj_g}, {adj_b}) [B:{brightness}% S:{saturation}%]")
                
                # Set the zone color with adjustments
                zone_color = RGBColor(adj_r, adj_g, adj_b)
                device.zones[zone_idx].set_color(zone_color)
            
            # Force update to hardware
            device.update()
            logger.warning(f"   ✅ Device updated\n")
        else:
            # Get only non-excluded devices
            devices = list(enumerate(self.get_devices(include_excluded=False)))
            for idx, device in devices:
                logger.warning(f"\n🎨 Setting device color for {device.name}")
                logger.warning(f"   Color: RGB({r}, {g}, {b})")
                # Save device color to database for EVERY zone
                logger.warning(f"   Saving to DB for {len(device.zones)} zones:")
                for zone_idx in range(len(device.zones)):
                    self.db.set_color(idx, zone_idx, r, g, b)
                    logger.warning(f"   ✓ Zone {zone_idx} → RGB({r}, {g}, {b})")
                # Switch to Direct mode if available
                self._set_direct_mode(device)
                # Re-fetch device after mode change
                device = self.client.devices[idx]
                
                # Apply brightness/saturation per zone
                logger.warning(f"   Applying brightness/saturation to zones:")
                for zone_idx in range(len(device.zones)):
                    # Get brightness and saturation for this zone
                    brightness, saturation = self.db.get_brightness_saturation(idx, zone_idx)
                    
                    # Apply brightness and saturation adjustments
                    adj_r, adj_g, adj_b = apply_brightness_saturation(r, g, b, brightness, saturation)
                    
                    logger.warning(f"   Zone {zone_idx}: RGB({r}, {g}, {b}) → RGB({adj_r}, {adj_g}, {adj_b}) [B:{brightness}% S:{saturation}%]")
                    
                    # Set the zone color with adjustments
                    zone_color = RGBColor(adj_r, adj_g, adj_b)
                    device.zones[zone_idx].set_color(zone_color)
                
                # Force update to hardware
                device.update()
                logger.warning(f"   ✅ Device updated\n")
    
    def set_zone_color(self, device_index, zone_index, r, g, b):
        """
        Set color for a specific zone while preserving other zones' colors
        
        Args:
            device_index: Device index
            zone_index: Zone index within the device
            r, g, b: RGB values (0-255)
        """
        device = self.client.devices[device_index]
        
        # Check if device is excluded
        if self.config.is_device_excluded(device.name):
            return  # Skip excluded device
        
        # Switch to Direct mode
        self._set_direct_mode(device)
        
        # Re-fetch device after mode change to get updated state
        device = self.client.devices[device_index]
        
        # Get the zone
        if zone_index >= len(device.zones):
            raise ValueError(f"Zone {zone_index} does not exist on {device.name}")
        
        zone = device.zones[zone_index]
        color = RGBColor(r, g, b)
        
        # Save this zone's color to database
        self.db.set_color(device_index, zone_index, r, g, b)
        logger.warning(f"\n🎨 Setting zone color for {device.name}")
        logger.warning(f"   Zone {zone_index} → RGB({r}, {g}, {b})")
        
        # Load all colors for this device from database
        device_colors = self.db.get_device_colors(device_index)
        
        # Build a dict of zone colors from database with brightness/saturation applied
        zone_colors = {}
        for z_idx, db_r, db_g, db_b in device_colors:
            # Get brightness and saturation for this zone
            brightness, saturation = self.db.get_brightness_saturation(device_index, z_idx)
            
            # Apply brightness and saturation adjustments
            adj_r, adj_g, adj_b = apply_brightness_saturation(db_r, db_g, db_b, brightness, saturation)
            
            zone_colors[z_idx] = RGBColor(adj_r, adj_g, adj_b)
            logger.warning(f"   DB: Zone {z_idx} → RGB({db_r}, {db_g}, {db_b}) → Adjusted RGB({adj_r}, {adj_g}, {adj_b}) [B:{brightness}% S:{saturation}%]")
        
        # Apply color to each zone
        logger.warning(f"\n   Applying colors to {len(device.zones)} zones:")
        for z_idx in range(len(device.zones)):
            if z_idx in zone_colors:
                zone_color = zone_colors[z_idx]
                device.zones[z_idx].set_color(zone_color)
                logger.warning(f"   ✓ Zone {z_idx} set to RGB({zone_color.red}, {zone_color.green}, {zone_color.blue})")
            else:
                logger.warning(f"   ⚠ Zone {z_idx} - No color in database (skipped)")
        
        device.update()
        logger.warning(f"   ✅ Device updated\n")
    
    def _set_direct_mode(self, device):
        """Helper to set device to Direct mode (or Custom/Static) for SDK control"""
        try:
            # Check current mode first
            current_mode = device.modes[device.active_mode] if device.active_mode < len(device.modes) else None
            
            # Look for modes in order of preference: Direct > Custom > Static
            mode_preferences = ['direct', 'custom', 'static']
            
            for preferred_mode in mode_preferences:
                # If already in a preferred mode, don't switch
                if current_mode and preferred_mode in current_mode.name.lower():
                    logger.warning(f"   ✓ Already in {current_mode.name} mode")
                    return
                
                # Otherwise try to find and set the mode
                for mode in device.modes:
                    if preferred_mode in mode.name.lower():
                        logger.warning(f"   → Switching to {mode.name} mode...")
                        device.set_mode(mode)
                        # Small delay to let the mode switch settle
                        import time
                        time.sleep(0.2)
                        logger.warning(f"   ✓ Set to {mode.name} mode")
                        return
            
            # If no preferred mode found, just log current mode
            if current_mode:
                logger.warning(f"   ℹ️  Using current mode: {current_mode.name}")
        except Exception as e:
            # If mode switching fails, log but continue anyway
            logger.warning(f"   ⚠️  Could not set mode: {e}")
            pass
    
    def rainbow_effect(self, duration=60, speed=1.0, device_index=None):
        """
        Create a rainbow effect
        
        Args:
            duration: How long to run (seconds)
            speed: Speed multiplier
            device_index: Specific device or None for all
        """
        if device_index is not None:
            device = self.client.devices[device_index]
            # Check if device is excluded
            if self.config.is_device_excluded(device.name):
                return  # Skip excluded device
            devices = [device]
        else:
            # Get only non-excluded devices
            devices = self.get_devices(include_excluded=False)
        
        # Set all devices to Direct mode
        for device in devices:
            self._set_direct_mode(device)
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            hue = (elapsed * speed * 60) % 360
            
            # HSV to RGB conversion
            h = hue / 60
            c = 1
            x = c * (1 - abs(h % 2 - 1))
            
            if 0 <= h < 1:
                r, g, b = c, x, 0
            elif 1 <= h < 2:
                r, g, b = x, c, 0
            elif 2 <= h < 3:
                r, g, b = 0, c, x
            elif 3 <= h < 4:
                r, g, b = 0, x, c
            elif 4 <= h < 5:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x
            
            color = RGBColor(int(r * 255), int(g * 255), int(b * 255))
            
            for device in devices:
                device.set_color(color)
                device.update()
            
            time.sleep(0.05)
    
    def breathing_effect(self, r, g, b, duration=60, speed=1.0, device_index=None):
        """
        Create a breathing effect (fade in/out)
        
        Args:
            r, g, b: Base RGB color (0-255)
            duration: How long to run (seconds)
            speed: Speed multiplier
            device_index: Specific device or None for all
        """
        if device_index is not None:
            device = self.client.devices[device_index]
            # Check if device is excluded
            if self.config.is_device_excluded(device.name):
                return  # Skip excluded device
            devices = [device]
        else:
            # Get only non-excluded devices
            devices = self.get_devices(include_excluded=False)
        
        # Set all devices to Direct mode
        for device in devices:
            self._set_direct_mode(device)
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            brightness = (math.sin(elapsed * speed * 2) + 1) / 2
            
            color = RGBColor(
                int(r * brightness),
                int(g * brightness),
                int(b * brightness)
            )
            
            for device in devices:
                device.set_color(color)
                device.update()
            
            time.sleep(0.05)
