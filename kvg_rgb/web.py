#!/usr/bin/env python3
"""
Flask web interface for KVG RGB Controller
Provides a local web UI for controlling RGB devices
"""
from flask import Flask, render_template, jsonify, request
from .core import RGBController
from .effects import EffectManager
import webbrowser
import threading
import time
import logging

logger = logging.getLogger(__name__)

# Global controller instance to maintain state across requests
_global_controller = None
_effect_manager = None

def get_controller():
    """Get or create the global controller instance"""
    global _global_controller
    if _global_controller is None:
        _global_controller = RGBController()
    return _global_controller

def get_effect_manager():
    """Get or create the global effect manager instance"""
    global _effect_manager
    if _effect_manager is None:
        _effect_manager = EffectManager()
        _effect_manager.start()
        # Load effects from database
        controller = get_controller()
        _effect_manager.load_effects_from_db(controller.db)
    return _effect_manager


def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        """Main control page"""
        return render_template('index.html')
    
    @app.route('/api/devices')
    def get_devices():
        """Get all RGB devices with their details"""
        try:
            controller = get_controller()
            all_devices = controller.get_all_devices()
            device_list = []
            
            for idx, device in enumerate(all_devices):
                zones = []
                if device.zones:
                    for zone_idx, zone in enumerate(device.zones):
                        friendly_name = controller.db.get_friendly_name(idx, zone_idx)
                        brightness, saturation = controller.db.get_brightness_saturation(idx, zone_idx)
                        effect_data = controller.db.get_effect(idx, zone_idx)
                        effect_type = effect_data[0] if effect_data else 'static'
                        effect_params = effect_data[1] if effect_data else None
                        # Get zone color from database
                        zone_color = controller.db.get_color(idx, zone_idx)
                        # Check if LED control is enabled
                        led_control_enabled = controller.db.is_led_control_enabled(idx, zone_idx)
                        # Check if there are saved LED colors
                        led_colors = controller.db.get_led_colors(idx, zone_idx)
                        has_led_colors = len(led_colors) > 0
                        # Check if zone is resizable by checking if it has the resize method
                        is_resizable = hasattr(zone, 'resize')
                        zones.append({
                            'index': zone_idx,
                            'name': zone.name,
                            'friendly_name': friendly_name,
                            'type': zone.type,
                            'leds': len(zone.leds),
                            'leds_min': getattr(zone, 'leds_min', None),
                            'leds_max': getattr(zone, 'leds_max', None),
                            'resizable': is_resizable,
                            'brightness': brightness,
                            'saturation': saturation,
                            'color': {'r': zone_color[0], 'g': zone_color[1], 'b': zone_color[2]} if zone_color else None,
                            'effect': effect_type,
                            'effect_params': effect_params,
                            'led_control_enabled': led_control_enabled,
                            'has_led_colors': has_led_colors,
                            'excluded': controller.config.is_zone_excluded(device.name, zone_idx)
                        })
                
                device_list.append({
                    'index': idx,
                    'name': device.name,
                    'type': device.type,
                    'leds': len(device.leds),
                    'zones': zones,
                    'excluded': controller.config.is_device_excluded(device.name)
                })
            
            return jsonify({'success': True, 'devices': device_list})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/device/toggle', methods=['POST'])
    def toggle_device():
        """Toggle device exclusion status"""
        try:
            data = request.json
            device_name = data['device_name']
            
            controller = get_controller()
            is_excluded = controller.config.toggle_device(device_name)
            return jsonify({
                'success': True,
                'device_name': device_name,
                'excluded': is_excluded
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/toggle', methods=['POST'])
    def toggle_zone():
        """Toggle zone exclusion status"""
        try:
            data = request.json
            device_index = int(data['device'])
            zone_index = int(data['zone'])
            
            controller = get_controller()
            devices = controller.client.devices
            device = devices[device_index]
            is_excluded = controller.config.toggle_zone(device.name, zone_index)
            return jsonify({
                'success': True,
                'device': device_index,
                'zone': zone_index,
                'excluded': is_excluded
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/color', methods=['POST'])
    def set_color():
        """Set color for device(s)"""
        try:
            data = request.json
            r = int(data['r'])
            g = int(data['g'])
            b = int(data['b'])
            device_index = data.get('device', None)
            
            controller = get_controller()
            controller.set_color(r, g, b, device_index)
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/color', methods=['POST'])
    def set_zone_color():
        """Set color for a specific zone"""
        try:
            data = request.json
            device_index = int(data['device'])
            zone_index = int(data['zone'])
            r = int(data['r'])
            g = int(data['g'])
            b = int(data['b'])
            
            controller = get_controller()
            controller.set_zone_color(device_index, zone_index, r, g, b)
            
            # Disable LED-level control when zone color is set
            # This preserves LED colors in DB but zone color takes precedence
            controller.db.set_led_control_enabled(device_index, zone_index, False)
            
            return jsonify({'success': True})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/flash', methods=['POST'])
    def flash_zone():
        """Flash a zone to identify it visually"""
        try:
            data = request.json
            device_index = data.get('device_index')
            zone_index = data.get('zone_index')
            flashes = data.get('flashes', 5)  # Default 5 flashes
            
            if device_index is None or zone_index is None:
                return jsonify({'success': False, 'error': 'Missing device_index or zone_index'}), 400
            
            # Flash in background thread
            def run_flash():
                import time
                from openrgb.utils import RGBColor
                
                # Create a separate connection for this thread
                flash_controller = RGBController()
                try:
                    device = flash_controller.client.devices[device_index]
                    zone = device.zones[zone_index]
                    
                    # Save current colors
                    old_colors = []
                    for led in zone.leds:
                        old_colors.append(device.colors[led.id])
                    
                    # Check if all LEDs in zone have the same color
                    uniform_color = None
                    if len(old_colors) > 0:
                        first_color = old_colors[0]
                        if all(c.red == first_color.red and c.green == first_color.green and c.blue == first_color.blue 
                               for c in old_colors):
                            uniform_color = RGBColor(first_color.red, first_color.green, first_color.blue)
                    
                    # Flash white/black alternating
                    white = RGBColor(255, 255, 255)
                    black = RGBColor(0, 0, 0)
                    
                    for i in range(flashes):
                        # Flash white
                        zone.set_color(white)
                        device.update()
                        time.sleep(0.2)
                        
                        # Flash black
                        zone.set_color(black)
                        device.update()
                        time.sleep(0.2)
                    
                    # Restore original colors
                    if uniform_color:
                        # Zone had uniform color - restore with zone.set_color()
                        zone.set_color(uniform_color)
                        device.update()
                    else:
                        # Zone had mixed colors - restore individual LEDs
                        for i, led in enumerate(zone.leds):
                            if i < len(old_colors):
                                device.colors[led.id] = old_colors[i]
                        device.update()
                finally:
                    # Always disconnect the thread's connection
                    flash_controller.disconnect()
            
            thread = threading.Thread(target=run_flash, daemon=True)
            thread.start()
            
            return jsonify({'success': True})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/rename', methods=['POST'])
    def rename_zone():
        """Set friendly name for a zone"""
        try:
            data = request.json
            device_index = int(data['device'])
            zone_index = int(data['zone'])
            friendly_name = data.get('name', '').strip()
            
            controller = get_controller()
            controller.db.set_friendly_name(device_index, zone_index, friendly_name)
            
            return jsonify({
                'success': True,
                'device': device_index,
                'zone': zone_index,
                'friendly_name': friendly_name
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/brightness', methods=['POST'])
    def set_zone_brightness_saturation():
        """Set brightness and saturation for a zone"""
        try:
            data = request.json
            device_index = int(data['device'])
            zone_index = int(data['zone'])
            brightness = int(data.get('brightness', 100))
            saturation = int(data.get('saturation', 100))
            
            # Validate ranges
            brightness = max(0, min(100, brightness))
            saturation = max(0, min(100, saturation))
            
            controller = get_controller()
            controller.db.set_brightness_saturation(device_index, zone_index, brightness, saturation)
            
            # Re-apply current color with new brightness/saturation
            color = controller.db.get_color(device_index, zone_index)
            if color:
                r, g, b = color
                controller.set_zone_color(device_index, zone_index, r, g, b)
            
            return jsonify({
                'success': True,
                'device': device_index,
                'zone': zone_index,
                'brightness': brightness,
                'saturation': saturation
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/effect', methods=['POST'])
    def set_zone_effect():
        """Set effect for a zone"""
        try:
            data = request.json
            device_index = int(data['device'])
            zone_index = int(data['zone'])
            effect_type = data.get('effect_type', 'static')
            effect_params = data.get('effect_params', None)
            
            controller = get_controller()
            effect_manager = get_effect_manager()
            
            # Save to database
            if effect_type == 'static':
                controller.db.clear_effect(device_index, zone_index)
                effect_manager.clear_effect(device_index, zone_index)
                
                # Apply the stored static color when switching to static mode
                color = controller.db.get_color(device_index, zone_index)
                if color:
                    r, g, b = color
                    controller.set_zone_color(device_index, zone_index, r, g, b)
                    logger.warning(f"Applied static color RGB({r}, {g}, {b}) to device {device_index}, zone {zone_index}")
            else:
                import json
                params_json = json.dumps(effect_params) if effect_params else None
                controller.db.set_effect(device_index, zone_index, effect_type, params_json)
                effect_manager.set_effect(device_index, zone_index, effect_type, params_json)
            
            return jsonify({
                'success': True,
                'device': device_index,
                'zone': zone_index,
                'effect': effect_type
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/reset-modes', methods=['POST'])
    def reset_device_modes():
        """Force all devices back to Direct mode and reapply colors"""
        try:
            controller = get_controller()
            all_devices = controller.get_all_devices()
            reset_count = 0
            
            for device_idx, device in enumerate(all_devices):
                if controller.config.is_device_excluded(device.name):
                    continue
                
                # Force device to Direct mode
                controller._set_direct_mode(device)
                
                # Reapply all zone colors
                for zone_idx in range(len(device.zones)):
                    color = controller.db.get_color(device_idx, zone_idx)
                    if color:
                        r, g, b = color
                        controller.set_zone_color(device_idx, zone_idx, r, g, b)
                        reset_count += 1
            
            return jsonify({
                'success': True,
                'message': f'Reset {reset_count} zones to Direct mode and reapplied colors'
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/resize', methods=['POST'])
    def resize_zone():
        """Resize a zone (change number of LEDs)"""
        try:
            data = request.json
            device_index = int(data['device'])
            zone_index = int(data['zone'])
            new_size = int(data['size'])
            
            controller = get_controller()
            device = controller.client.devices[device_index]
            
            # Check if device is excluded
            if controller.config.is_device_excluded(device.name):
                return jsonify({'success': False, 'error': 'Device is excluded'}), 400
            
            # Check if zone exists
            if zone_index >= len(device.zones):
                return jsonify({'success': False, 'error': 'Zone does not exist'}), 400
            
            zone = device.zones[zone_index]
            
            # Check if zone is resizable (has resize method)
            if not hasattr(zone, 'resize'):
                return jsonify({'success': False, 'error': 'Zone does not support resizing'}), 400
            
            # Get min/max if available
            leds_min = getattr(zone, 'leds_min', None)
            leds_max = getattr(zone, 'leds_max', None)
            
            # Validate new size if min/max are available
            if leds_min is not None and leds_max is not None:
                if new_size < leds_min or new_size > leds_max:
                    return jsonify({
                        'success': False, 
                        'error': f'Size must be between {leds_min} and {leds_max}'
                    }), 400
            else:
                # No min/max reported, use reasonable defaults for validation
                if new_size < 1 or new_size > 500:
                    return jsonify({
                        'success': False, 
                        'error': 'Size must be between 1 and 500 LEDs'
                    }), 400
            
            # Resize the zone using OpenRGB SDK
            old_size = len(zone.leds)
            zone.resize(new_size)
            
            # Wait a moment and verify the resize worked
            import time
            time.sleep(0.2)
            
            # Re-fetch device to get updated zone info
            device = controller.client.devices[device_index]
            zone = device.zones[zone_index]
            actual_size = len(zone.leds)
            
            # Check if resize actually worked
            if actual_size == old_size and old_size != new_size:
                return jsonify({
                    'success': False,
                    'error': f'Zone resize failed - zone may not support resizing (fixed at {actual_size} LEDs)'
                }), 400
            
            return jsonify({
                'success': True,
                'device': device_index,
                'zone': zone_index,
                'new_size': actual_size
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/effect/rainbow', methods=['POST'])
    def rainbow_effect():
        """Start rainbow effect"""
        try:
            data = request.json
            duration = data.get('duration', 30)
            speed = data.get('speed', 1.0)
            device_index = data.get('device', None)
            
            # Run effect in background thread
            def run_effect():
                with RGBController() as controller:
                    controller.rainbow_effect(duration, speed, device_index)
            
            thread = threading.Thread(target=run_effect, daemon=True)
            thread.start()
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/effect/breathe', methods=['POST'])
    def breathe_effect():
        """Start breathing effect"""
        try:
            data = request.json
            r = int(data['r'])
            g = int(data['g'])
            b = int(data['b'])
            duration = data.get('duration', 30)
            speed = data.get('speed', 1.0)
            device_index = data.get('device', None)
            
            # Run effect in background thread
            def run_effect():
                with RGBController() as controller:
                    controller.breathing_effect(r, g, b, duration, speed, device_index)
            
            thread = threading.Thread(target=run_effect, daemon=True)
            thread.start()
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/colors/recent')
    def get_recent_colors():
        """Get recent colors"""
        try:
            controller = get_controller()
            recent = controller.db.get_recent_colors(limit=8)
            colors = [{'r': r, 'g': g, 'b': b} for r, g, b in recent]
            return jsonify({'success': True, 'colors': colors})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/colors/recent', methods=['POST'])
    def add_recent_color():
        """Add a color to recent colors"""
        try:
            data = request.json
            r = int(data['r'])
            g = int(data['g'])
            b = int(data['b'])
            
            controller = get_controller()
            controller.db.add_recent_color(r, g, b)
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/device/<int:device_index>/lock', methods=['GET'])
    def get_device_lock(device_index):
        """Get device lock state"""
        try:
            controller = get_controller()
            locked = controller.db.get_device_lock(device_index)
            return jsonify({'success': True, 'locked': locked})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/device/<int:device_index>/lock', methods=['POST'])
    def set_device_lock(device_index):
        """Set device lock state"""
        try:
            data = request.json
            locked = bool(data.get('locked', False))
            
            controller = get_controller()
            controller.db.set_device_lock(device_index, locked)
            
            return jsonify({'success': True, 'locked': locked})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/device/locks', methods=['GET'])
    def get_all_device_locks():
        """Get all device lock states"""
        try:
            controller = get_controller()
            locks = controller.db.get_all_device_locks()
            return jsonify({'success': True, 'locks': locks})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/<int:device_index>/<int:zone_index>/leds', methods=['GET'])
    def get_zone_leds(device_index, zone_index):
        """Get LED colors for a zone"""
        try:
            controller = get_controller()
            led_colors = controller.db.get_led_colors(device_index, zone_index)
            led_control_enabled = controller.db.is_led_control_enabled(device_index, zone_index)
            # Convert to list format: [{index: 0, r: 255, g: 0, b: 0}, ...]
            leds = [{'index': idx, 'r': r, 'g': g, 'b': b} 
                   for idx, (r, g, b) in sorted(led_colors.items())]
            return jsonify({'success': True, 'leds': leds, 'enabled': led_control_enabled})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/<int:device_index>/<int:zone_index>/led/<int:led_index>/color', methods=['POST'])
    def set_led_color(device_index, zone_index, led_index):
        """Set color for an individual LED"""
        try:
            data = request.json
            r = int(data['r'])
            g = int(data['g'])
            b = int(data['b'])
            
            controller = get_controller()
            
            # Save to database
            controller.db.set_led_color(device_index, zone_index, led_index, r, g, b)
            
            # Enable LED-level control for this zone
            controller.db.set_led_control_enabled(device_index, zone_index, True)
            
            # Apply to hardware
            device = controller.client.devices[device_index]
            zone = device.zones[zone_index]
            
            # Get all LED colors for this zone
            led_colors = controller.db.get_led_colors(device_index, zone_index)
            
            # Create LED color array - use zone.leds instead of zone.leds_count
            from openrgb.utils import RGBColor
            colors = []
            num_leds = len(zone.leds) if hasattr(zone, 'leds') else zone.leds_count
            for i in range(num_leds):
                if i in led_colors:
                    led_r, led_g, led_b = led_colors[i]
                    colors.append(RGBColor(led_r, led_g, led_b))
                else:
                    # Use zone color if no LED color is set
                    zone_color = controller.db.get_color(device_index, zone_index)
                    if zone_color:
                        colors.append(RGBColor(*zone_color))
                    else:
                        colors.append(RGBColor(0, 0, 0))
            
            # Set zone to Direct mode and apply colors
            if device.active_mode != 0:  # 0 is usually Direct mode
                # Try to find and set Direct mode
                for i, mode in enumerate(device.modes):
                    if 'direct' in mode.name.lower():
                        device.set_mode(i)
                        print(f"✓ Set device to Direct mode")
                        break
            
            # Set LEDs
            print(f"🎨 Setting {len(colors)} LED colors for device {device_index}, zone {zone_index}")
            for idx, color in enumerate(colors):
                print(f"  LED {idx}: {color}")
            zone.set_colors(colors)
            device.show()
            print(f"✅ LED colors applied successfully")
            
            return jsonify({'success': True})
        except Exception as e:
            print(f"ERROR setting LED color: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/<int:device_index>/<int:zone_index>/led/<int:led_index>/flash', methods=['POST'])
    def flash_single_led(device_index, zone_index, led_index):
        """Flash a single LED to identify its location"""
        try:
            from openrgb.utils import RGBColor
            import time
            
            controller = get_controller()
            device = controller.client.devices[device_index]
            zone = device.zones[zone_index]
            
            # Get current LED colors
            led_colors = controller.db.get_led_colors(device_index, zone_index)
            num_leds = len(zone.leds) if hasattr(zone, 'leds') else zone.leds_count
            
            # Store original color of the LED
            original_color = led_colors.get(led_index)
            if not original_color:
                # If no saved color, get from zone color
                zone_color = controller.db.get_color(device_index, zone_index)
                original_color = zone_color if zone_color else (0, 0, 0)
            
            # Create colors array with all LEDs at their current state
            colors = []
            for i in range(num_leds):
                if i in led_colors:
                    colors.append(RGBColor(*led_colors[i]))
                else:
                    zone_color = controller.db.get_color(device_index, zone_index)
                    colors.append(RGBColor(*zone_color) if zone_color else RGBColor(0, 0, 0))
            
            # Set zone to Direct mode
            if device.active_mode != 0:
                for i, mode in enumerate(device.modes):
                    if 'direct' in mode.name.lower():
                        device.set_mode(i)
                        break
            
            # Flash sequence: 3 flashes
            for _ in range(3):
                # Turn LED white
                colors[led_index] = RGBColor(255, 255, 255)
                zone.set_colors(colors)
                device.show()
                time.sleep(0.15)
                
                # Turn LED off
                colors[led_index] = RGBColor(0, 0, 0)
                zone.set_colors(colors)
                device.show()
                time.sleep(0.15)
            
            # Restore original color
            colors[led_index] = RGBColor(*original_color)
            zone.set_colors(colors)
            device.show()
            
            return jsonify({'success': True})
        except Exception as e:
            print(f"ERROR flashing LED: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/<int:device_index>/<int:zone_index>/gradient', methods=['POST'])
    def set_zone_gradient(device_index, zone_index):
        """Apply a gradient to a zone"""
        try:
            data = request.json
            start_r = int(data['start_r'])
            start_g = int(data['start_g'])
            start_b = int(data['start_b'])
            end_r = int(data['end_r'])
            end_g = int(data['end_g'])
            end_b = int(data['end_b'])
            
            controller = get_controller()
            device = controller.client.devices[device_index]
            zone = device.zones[zone_index]
            
            # Get LED count
            num_leds = len(zone.leds) if hasattr(zone, 'leds') else zone.leds_count
            
            # Apply gradient in database
            controller.db.set_zone_gradient(
                device_index, zone_index, num_leds,
                start_r, start_g, start_b,
                end_r, end_g, end_b
            )
            
            # Enable LED-level control for this zone
            controller.db.set_led_control_enabled(device_index, zone_index, True)
            
            # Get gradient colors and apply to hardware
            from openrgb.utils import RGBColor
            led_colors = controller.db.get_led_colors(device_index, zone_index)
            colors = [RGBColor(*led_colors.get(i, (0, 0, 0))) for i in range(num_leds)]
            
            # Set zone to Direct mode
            if device.active_mode != 0:
                for i, mode in enumerate(device.modes):
                    if 'direct' in mode.name.lower():
                        device.set_mode(i)
                        break
            
            # Apply colors
            zone.set_colors(colors)
            device.show()
            
            return jsonify({'success': True})
        except Exception as e:
            print(f"ERROR applying gradient: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/<int:device_index>/<int:zone_index>/leds/fill', methods=['POST'])
    def fill_zone_leds(device_index, zone_index):
        """Set all LEDs in a zone to the same color"""
        try:
            data = request.json
            r = int(data['r'])
            g = int(data['g'])
            b = int(data['b'])
            
            controller = get_controller()
            device = controller.client.devices[device_index]
            zone = device.zones[zone_index]
            
            # Get LED count
            num_leds = len(zone.leds) if hasattr(zone, 'leds') else zone.leds_count
            
            # Set all LEDs to the same color in database
            for i in range(num_leds):
                controller.db.set_led_color(device_index, zone_index, i, r, g, b)
            
            # Enable LED-level control for this zone
            controller.db.set_led_control_enabled(device_index, zone_index, True)
            
            # Apply to hardware - much faster than individual updates
            from openrgb.utils import RGBColor
            color = RGBColor(r, g, b)
            colors = [color] * num_leds
            
            # Set zone to Direct mode
            if device.active_mode != 0:
                for i, mode in enumerate(device.modes):
                    if 'direct' in mode.name.lower():
                        device.set_mode(i)
                        break
            
            # Apply colors in one operation
            zone.set_colors(colors)
            device.show()
            
            return jsonify({'success': True})
        except Exception as e:
            print(f"ERROR filling LEDs: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/<int:device_index>/<int:zone_index>/leds/clear', methods=['POST'])
    def clear_zone_leds(device_index, zone_index):
        """Clear individual LED colors and revert to zone color"""
        try:
            from openrgb.utils import RGBColor
            controller = get_controller()
            controller.db.clear_led_colors(device_index, zone_index)
            
            # Disable LED control
            controller.db.set_led_control_enabled(device_index, zone_index, False)
            
            # Reapply zone color
            zone_color = controller.db.get_color(device_index, zone_index)
            if zone_color:
                device = controller.client.devices[device_index]
                zone = device.zones[zone_index]
                zone.set_color(RGBColor(*zone_color))
                device.show()
            
            return jsonify({'success': True})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/zone/<int:device_index>/<int:zone_index>/leds/toggle', methods=['POST'])
    def toggle_led_control(device_index, zone_index):
        """Toggle LED-level control on/off for a zone"""
        try:
            from openrgb.utils import RGBColor
            controller = get_controller()
            current_state = controller.db.is_led_control_enabled(device_index, zone_index)
            new_state = not current_state
            
            controller.db.set_led_control_enabled(device_index, zone_index, new_state)
            
            # Apply appropriate colors to hardware
            device = controller.client.devices[device_index]
            zone = device.zones[zone_index]
            
            if new_state:
                # Re-enable LED control - apply saved LED colors
                led_colors = controller.db.get_led_colors(device_index, zone_index)
                if led_colors:
                    num_leds = len(zone.leds) if hasattr(zone, 'leds') else zone.leds_count
                    colors = []
                    for i in range(num_leds):
                        if i in led_colors:
                            colors.append(RGBColor(*led_colors[i]))
                        else:
                            zone_color = controller.db.get_color(device_index, zone_index)
                            colors.append(RGBColor(*zone_color) if zone_color else RGBColor(0, 0, 0))
                    zone.set_colors(colors)
                    device.show()
            else:
                # Disable LED control - apply zone color
                zone_color = controller.db.get_color(device_index, zone_index)
                if zone_color:
                    zone.set_color(RGBColor(*zone_color))
                    device.show()
            
            return jsonify({'success': True, 'enabled': new_state})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Initialize and restore colors on startup
    @app.before_request
    def restore_static_colors_once():
        """Restore all static colors on first request"""
        # Use a flag to only run once
        if not hasattr(restore_static_colors_once, 'done'):
            restore_static_colors_once.done = True
            try:
                controller = get_controller()
                effect_manager = get_effect_manager()
                
                # Get all devices and restore their colors
                all_devices = controller.get_all_devices()
                restored_count = 0
                
                for device_idx, device in enumerate(all_devices):
                    if controller.config.is_device_excluded(device.name):
                        continue
                    
                    for zone_idx in range(len(device.zones)):
                        # Check if zone has an effect
                        effect_data = controller.db.get_effect(device_idx, zone_idx)
                        
                        # Only restore if no effect or static effect
                        if not effect_data or effect_data[0] == 'static':
                            color = controller.db.get_color(device_idx, zone_idx)
                            if color:
                                r, g, b = color
                                controller.set_zone_color(device_idx, zone_idx, r, g, b)
                                restored_count += 1
                
                if restored_count > 0:
                    logger.warning(f"🎨 Restored {restored_count} static colors on startup")
            except Exception as e:
                logger.error(f"Error restoring static colors: {e}")
    
    @app.route('/api/settings/launch', methods=['POST'])
    def launch_settings():
        """Launch the settings manager (Windows only)"""
        import platform
        if platform.system() != 'Windows':
            return jsonify({'success': False, 'error': 'Settings manager is only available on Windows'}), 400
        
        try:
            import subprocess
            import sys
            
            # Launch kvg-rgb settings command
            subprocess.Popen([sys.executable, '-m', 'kvg_rgb.cli', 'settings'])
            
            return jsonify({'success': True, 'message': 'Settings manager launched'})
        except Exception as e:
            logger.error(f"Error launching settings: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return app


def open_browser(port):
    """Open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open(f'http://localhost:{port}')


def run_web_server(host='127.0.0.1', port=5000, debug=False, open_browser_window=True):
    """Run the Flask web server"""
    app = create_app()
    
    print("\n" + "="*70)
    print("  KVG RGB Web Controller")
    print("="*70)
    print(f"\n🌐 Starting web server on http://{host}:{port}")
    print(f"📱 Open this URL in your browser to control your RGB devices")
    print(f"\n⚠️  Press CTRL+C to stop the server\n")
    
    if open_browser_window:
        # Open browser in a separate thread
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")


if __name__ == '__main__':
    run_web_server()
