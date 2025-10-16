"""
Core RGB control functionality (can be used by CLI or GUI)
"""
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
from .config import get_config
import time
import math


class RGBController:
    """Core RGB controller class"""
    
    def __init__(self, host='localhost', port=6742):
        """Initialize connection to OpenRGB"""
        self.client = OpenRGBClient(name="KVG_RGB", address=host, port=port)
        self.config = get_config()
        # Track zone colors to preserve them across updates
        self._device_zone_colors = {}  # {device_index: {zone_index: RGBColor}}
        
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
        color = RGBColor(r, g, b)
        
        if device_index is not None:
            device = self.client.devices[device_index]
            # Check if device is excluded
            if self.config.is_device_excluded(device.name):
                return  # Skip excluded device
            # Clear zone color tracking when setting entire device
            if device_index in self._device_zone_colors:
                del self._device_zone_colors[device_index]
            # Switch to Direct mode if available
            self._set_direct_mode(device)
            # Set color for all LEDs
            device.set_color(color)
            # Force update to hardware
            device.update()
        else:
            # Get only non-excluded devices
            devices = self.get_devices(include_excluded=False)
            for idx, device in enumerate(devices):
                # Clear zone color tracking
                if idx in self._device_zone_colors:
                    del self._device_zone_colors[idx]
                # Switch to Direct mode if available
                self._set_direct_mode(device)
                # Set color for all LEDs
                device.set_color(color)
                # Force update to hardware
                device.update()
    
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
        
        # Get the zone
        if zone_index >= len(device.zones):
            raise ValueError(f"Zone {zone_index} does not exist on {device.name}")
        
        zone = device.zones[zone_index]
        color = RGBColor(r, g, b)
        
        # Initialize device in zone colors tracking if not present
        if device_index not in self._device_zone_colors:
            self._device_zone_colors[device_index] = {}
        
        # Store this zone's color
        self._device_zone_colors[device_index][zone_index] = color
        
        # Apply ALL tracked zone colors for this device to preserve colors
        for tracked_zone_index, tracked_color in self._device_zone_colors[device_index].items():
            if tracked_zone_index < len(device.zones):
                tracked_zone = device.zones[tracked_zone_index]
                # Set color for each LED in the tracked zone
                for led in tracked_zone.leds:
                    try:
                        device.leds[led.id].set_color(tracked_color)
                    except Exception as e:
                        print(f"Warning: Could not set LED {led.id}: {e}")
        
        device.update()
    
    def _set_direct_mode(self, device):
        """Helper to set device to Direct mode for SDK control"""
        try:
            # Look for 'Direct' mode
            for mode in device.modes:
                if 'direct' in mode.name.lower():
                    device.set_mode(mode)
                    return
        except Exception:
            # If mode switching fails, continue anyway
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
