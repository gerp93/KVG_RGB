"""
Core RGB control functionality (can be used by CLI or GUI)
"""
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
import time
import math


class RGBController:
    """Core RGB controller class"""
    
    def __init__(self, host='localhost', port=6742):
        """Initialize connection to OpenRGB"""
        self.client = OpenRGBClient(name="KVG_RGB", address=host, port=port)
        
    def disconnect(self):
        """Disconnect from OpenRGB"""
        self.client.disconnect()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    
    def get_devices(self):
        """Get list of all RGB devices"""
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
            self.client.devices[device_index].set_color(color)
        else:
            for device in self.client.devices:
                device.set_color(color)
    
    def rainbow_effect(self, duration=60, speed=1.0, device_index=None):
        """
        Create a rainbow effect
        
        Args:
            duration: How long to run (seconds)
            speed: Speed multiplier
            device_index: Specific device or None for all
        """
        devices = [self.client.devices[device_index]] if device_index is not None else self.client.devices
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
        devices = [self.client.devices[device_index]] if device_index is not None else self.client.devices
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
            
            time.sleep(0.05)
