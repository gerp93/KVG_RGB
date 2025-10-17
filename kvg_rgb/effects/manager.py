"""
Effect manager for per-zone animated effects.
"""
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
import time
import math
import threading
import json
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class EffectManager:
    """Manages per-zone effects in background threads."""
    
    def __init__(self, host='localhost', port=6742):
        """
        Initialize the effect manager.
        
        Args:
            host: OpenRGB server host
            port: OpenRGB server port
        """
        self.host = host
        self.port = port
        self.running = False
        self.thread = None
        self.active_effects = {}  # {(device_idx, zone_idx): {'type': ..., 'params': ...}}
        self.lock = threading.Lock()
    
    def start(self):
        """Start the effect manager thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_effects_loop, daemon=True)
        self.thread.start()
        logger.info("Effect manager started")
    
    def stop(self):
        """Stop the effect manager thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("Effect manager stopped")
    
    def set_effect(self, device_index: int, zone_index: int, effect_type: str, effect_params: Optional[str] = None):
        """
        Set an effect for a zone.
        
        Args:
            device_index: Device index
            zone_index: Zone index
            effect_type: Effect type ('static', 'rainbow', 'breathing', 'wave', 'cycle')
            effect_params: JSON string with effect parameters
        """
        with self.lock:
            key = (device_index, zone_index)
            
            if effect_type == 'static':
                # Remove effect (will show static color)
                if key in self.active_effects:
                    del self.active_effects[key]
            else:
                # Parse params
                params = json.loads(effect_params) if effect_params else {}
                self.active_effects[key] = {
                    'type': effect_type,
                    'params': params,
                    'start_time': time.time()
                }
            
            logger.info(f"Set effect for device {device_index}, zone {zone_index}: {effect_type}")
    
    def clear_effect(self, device_index: int, zone_index: int):
        """
        Clear effect for a zone.
        
        Args:
            device_index: Device index
            zone_index: Zone index
        """
        with self.lock:
            key = (device_index, zone_index)
            if key in self.active_effects:
                del self.active_effects[key]
                logger.info(f"Cleared effect for device {device_index}, zone {zone_index}")
    
    def load_effects_from_db(self, db):
        """
        Load all effects from database.
        
        Args:
            db: ColorDatabase instance
        """
        effects = db.get_all_effects()
        with self.lock:
            for device_idx, zone_idx, effect_type, effect_params in effects:
                if effect_type != 'static':
                    params = json.loads(effect_params) if effect_params else {}
                    key = (device_idx, zone_idx)
                    self.active_effects[key] = {
                        'type': effect_type,
                        'params': params,
                        'start_time': time.time()
                    }
        logger.info(f"Loaded {len(effects)} effects from database")
    
    def _run_effects_loop(self):
        """Main effect loop running in background thread."""
        # Create a separate OpenRGB client for the effect thread
        client = None
        
        try:
            client = OpenRGBClient(name="KVG_RGB_Effects", address=self.host, port=self.port)
            logger.info("Effect manager connected to OpenRGB")
            
            while self.running:
                with self.lock:
                    effects_to_apply = dict(self.active_effects)
                
                if effects_to_apply:
                    # Apply each effect
                    for (device_idx, zone_idx), effect_data in effects_to_apply.items():
                        try:
                            self._apply_effect(client, device_idx, zone_idx, effect_data)
                        except Exception as e:
                            logger.error(f"Error applying effect to device {device_idx}, zone {zone_idx}: {e}")
                
                time.sleep(0.05)  # 20 FPS update rate
                
        except Exception as e:
            logger.error(f"Effect manager loop error: {e}")
        finally:
            if client:
                try:
                    client.disconnect()
                except:
                    pass
    
    def _apply_effect(self, client: OpenRGBClient, device_idx: int, zone_idx: int, effect_data: dict):
        """
        Apply a single effect to a zone.
        
        Args:
            client: OpenRGB client
            device_idx: Device index
            zone_idx: Zone index
            effect_data: Effect data dict with 'type', 'params', 'start_time'
        """
        device = client.devices[device_idx]
        zone = device.zones[zone_idx]
        
        effect_type = effect_data['type']
        params = effect_data['params']
        elapsed = time.time() - effect_data['start_time']
        speed = params.get('speed', 1.0)
        
        if effect_type == 'rainbow':
            color = self._rainbow_color(elapsed, speed)
            zone.set_color(color)
            
        elif effect_type == 'breathing':
            base_color = params.get('color', {'r': 255, 'g': 0, 'b': 0})
            color = self._breathing_color(
                base_color['r'],
                base_color['g'],
                base_color['b'],
                elapsed,
                speed
            )
            zone.set_color(color)
            
        elif effect_type == 'wave':
            # Wave effect - color shifts through spectrum
            color = self._wave_color(elapsed, speed, zone_idx)
            zone.set_color(color)
            
        elif effect_type == 'cycle':
            # Cycle through preset colors
            colors = params.get('colors', [
                {'r': 255, 'g': 0, 'b': 0},
                {'r': 0, 'g': 255, 'b': 0},
                {'r': 0, 'g': 0, 'b': 255}
            ])
            color = self._cycle_color(colors, elapsed, speed)
            zone.set_color(color)
        
        device.update()
    
    def _rainbow_color(self, elapsed: float, speed: float) -> RGBColor:
        """Generate rainbow color based on time."""
        hue = (elapsed * speed * 60) % 360
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
        
        return RGBColor(int(r * 255), int(g * 255), int(b * 255))
    
    def _breathing_color(self, r: int, g: int, b: int, elapsed: float, speed: float) -> RGBColor:
        """Generate breathing effect color based on time."""
        brightness = (math.sin(elapsed * speed * 2) + 1) / 2
        return RGBColor(
            int(r * brightness),
            int(g * brightness),
            int(b * brightness)
        )
    
    def _wave_color(self, elapsed: float, speed: float, zone_idx: int) -> RGBColor:
        """Generate wave effect color based on time and zone position."""
        # Add phase shift based on zone index for wave effect
        hue = ((elapsed * speed * 60) + (zone_idx * 30)) % 360
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
        
        return RGBColor(int(r * 255), int(g * 255), int(b * 255))
    
    def _cycle_color(self, colors: list, elapsed: float, speed: float) -> RGBColor:
        """Cycle through a list of colors."""
        cycle_duration = 2.0 / speed  # 2 seconds per color at speed 1.0
        color_index = int((elapsed / cycle_duration) % len(colors))
        color = colors[color_index]
        return RGBColor(color['r'], color['g'], color['b'])
