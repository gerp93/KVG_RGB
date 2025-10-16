#!/usr/bin/env python3
"""
Flask web interface for KVG RGB Controller
Provides a local web UI for controlling RGB devices
"""
from flask import Flask, render_template, jsonify, request
from .core import RGBController
from .effect_manager import EffectManager
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
