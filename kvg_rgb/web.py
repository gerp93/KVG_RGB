#!/usr/bin/env python3
"""
Flask web interface for KVG RGB Controller
Provides a local web UI for controlling RGB devices
"""
from flask import Flask, render_template, jsonify, request
from .core import RGBController, apply_brightness_saturation
from .effects import EffectManager
from .logbuffer import get_handler
import webbrowser
import threading
import time
import logging

logger = logging.getLogger(__name__)

# Global controller instance to maintain state across requests
_global_controller = None
_effect_manager = None
_keepalive_thread = None
_keepalive_enabled = True

# How often the keepalive re-asserts mode + colors, in seconds.
KEEPALIVE_INTERVAL = 5.0

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


def build_led_colors(controller, device_index, zone_index, num_leds):
    """
    Build the RGBColor list for a zone's per-LED colors.

    Per-LED colors are stored raw in the database and adjusted here at write
    time, exactly like static zone colors are — which is what makes the
    brightness/saturation sliders behave the same in gradient/per-LED mode as
    they do everywhere else. LEDs with no stored color fall back to the zone
    color.
    """
    from openrgb.utils import RGBColor

    led_colors = controller.db.get_led_colors(device_index, zone_index)
    fallback = controller.db.get_color(device_index, zone_index) or (0, 0, 0)
    brightness, saturation = controller.db.get_brightness_saturation(device_index, zone_index)

    colors = []
    for i in range(num_leds):
        r, g, b = led_colors.get(i, fallback)
        colors.append(RGBColor(*apply_brightness_saturation(r, g, b, brightness, saturation)))
    return colors


def _keepalive_loop():
    """
    Periodically re-assert Direct mode + stored colors.

    ASUS Aura boards fall back to their onboard effect when the SDK goes
    quiet, and since the protocol is write-only nothing tells us it happened
    — the app keeps reporting success while the lights cycle a hardware
    pattern. Re-asserting on a timer is what actually holds control.
    """
    logger.warning(f"🫀 Keepalive started (every {KEEPALIVE_INTERVAL:.0f}s)")
    while True:
        time.sleep(KEEPALIVE_INTERVAL)
        if not _keepalive_enabled:
            continue
        try:
            controller = get_controller()
            applied = controller.reassert_colors()
            if applied:
                logger.info(f"🫀 Keepalive re-asserted {applied} zone colors")
        except Exception as e:
            logger.error(f"🫀 Keepalive error: {e}")


def start_keepalive():
    """Start the keepalive thread once per process."""
    global _keepalive_thread
    if _keepalive_thread is None:
        _keepalive_thread = threading.Thread(target=_keepalive_loop, daemon=True)
        _keepalive_thread.start()


def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)

    # Capture logs in memory so the UI's Logs tab can show them. The packaged
    # app is windowed (no console), so this is the only way to see them.
    get_handler()
    
    @app.route('/')
    def index():
        """
        Main control page.

        Deliberately does NOT go through get_controller(): that opens the
        OpenRGB connection, so with OpenRGB closed this route raised and the
        user got a bare Flask "Internal Server Error" page instead of the app
        — no Reconnect button, no Settings, no way to see what was wrong. The
        theme lives in SQLite and needs no hardware, so render regardless and
        let the device list report the connection problem.
        """
        from .database import ColorDatabase, DEFAULT_THEME
        try:
            theme = ColorDatabase().get_theme()
        except Exception as e:
            logger.error(f"Could not read theme, falling back to default: {e}")
            theme = DEFAULT_THEME
        return render_template('index.html', theme=theme)
    
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
        except (ConnectionError, OSError) as e:
            # The most common failure by far, and "timed out" on its own tells
            # the user nothing they can act on.
            logger.error(f"Could not reach OpenRGB while listing devices: {e}")
            return jsonify({
                'success': False,
                'error': "Can't reach OpenRGB — check that it's running and that "
                         "\"Start SDK Server\" is enabled in its settings, then click Reconnect.",
                'detail': str(e),
            }), 503
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

            # Re-apply whatever this zone is actually showing. Which of the three
            # modes it's in matters: blindly writing the flat zone color here used
            # to wipe a gradient off the hardware the moment you touched a slider.
            effect = controller.db.get_effect(device_index, zone_index)
            if effect and effect[0] != 'static':
                # The effects thread re-reads brightness/saturation on its own —
                # writing here would just fight it for a frame.
                pass
            elif controller.db.is_led_control_enabled(device_index, zone_index):
                device = controller.client.devices[device_index]
                zone = device.zones[zone_index]
                num_leds = len(zone.leds) if hasattr(zone, 'leds') else zone.leds_count
                zone.set_colors(build_led_colors(controller, device_index, zone_index, num_leds), fast=True)
                device.show()
            else:
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
                # An effect owns the whole zone, so it and per-LED/gradient control
                # are mutually exclusive. Turn LED control off so the stored state
                # matches what the hardware is actually doing — the saved LED colors
                # stay in the database and come back when it's re-enabled.
                controller.db.set_led_control_enabled(device_index, zone_index, False)
            
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
                
                # Force device to Direct mode, and persist it to the controller's
                # onboard memory so it survives a reboot / power cycle. Only done
                # here (an explicit user action) because it writes to flash.
                controller._set_direct_mode(device, save=True)
                
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
    
    @app.route('/api/logs')
    def get_logs():
        """Live log feed for the Logs tab (poll with ?since=<seq>)"""
        try:
            since = int(request.args.get('since', 0))
        except (TypeError, ValueError):
            since = 0

        entries, latest = get_handler().entries_since(since)
        return jsonify({'success': True, 'entries': entries, 'latest': latest})

    @app.route('/api/logs/clear', methods=['POST'])
    def clear_logs():
        """Clear the in-memory log buffer"""
        get_handler().clear()
        logger.warning("🧹 Log buffer cleared")
        return jsonify({'success': True})

    @app.route('/api/settings/keepalive', methods=['GET', 'POST'])
    def keepalive_setting():
        """Get or set whether the keepalive re-asserts colors periodically"""
        global _keepalive_enabled
        if request.method == 'POST':
            try:
                _keepalive_enabled = bool(request.json.get('enabled', True))
                logger.warning(f"🫀 Keepalive {'enabled' if _keepalive_enabled else 'disabled'}")
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        return jsonify({
            'success': True,
            'enabled': _keepalive_enabled,
            'interval': KEEPALIVE_INTERVAL,
        })

    @app.route('/api/reconnect', methods=['POST'])
    def reconnect_openrgb():
        """Force a fresh connection to OpenRGB — escape hatch if lights stop responding"""
        try:
            controller = get_controller()
            reconnected = controller.ensure_connected(force=True)
            device_count = len(controller.client.devices)
            return jsonify({
                'success': True,
                'reconnected': reconnected,
                'devices': device_count,
                'message': (
                    f'Reconnected to OpenRGB — {device_count} devices'
                    if reconnected else
                    f'Connection is healthy — {device_count} devices'
                ),
            })
        except Exception as e:
            logger.error(f"Error reconnecting to OpenRGB: {e}")
            return jsonify({'success': False, 'error': f'Could not reach OpenRGB: {e}'}), 500

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
            
            num_leds = len(zone.leds) if hasattr(zone, 'leds') else zone.leds_count
            colors = build_led_colors(controller, device_index, zone_index, num_leds)

            # Set zone to Direct mode and apply colors
            if device.active_mode != 0:  # 0 is usually Direct mode
                # Try to find and set Direct mode
                for i, mode in enumerate(device.modes):
                    if 'direct' in mode.name.lower():
                        device.set_mode(i)
                        print(f"✓ Set device to Direct mode")
                        break
            
            # Set LEDs
            # fast=True skips openrgb-python's default post-write behavior of
            # reading the *entire device* back from the SDK server to refresh
            # its local cache -- a synchronous round-trip nothing here reads
            # afterward. Left at the default, gradients/LED fills competed
            # with the effects thread's own per-frame reads for the same
            # connection, which is what made both "sporadic".
            print(f"🎨 Setting {len(colors)} LED colors for device {device_index}, zone {zone_index}")
            for idx, color in enumerate(colors):
                print(f"  LED {idx}: {color}")
            zone.set_colors(colors, fast=True)
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
                zone.set_colors(colors, fast=True)
                device.show()
                time.sleep(0.15)
                
                # Turn LED off
                colors[led_index] = RGBColor(0, 0, 0)
                zone.set_colors(colors, fast=True)
                device.show()
                time.sleep(0.15)
            
            # Restore original color
            colors[led_index] = RGBColor(*original_color)
            zone.set_colors(colors, fast=True)
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
            colors = build_led_colors(controller, device_index, zone_index, num_leds)
            
            # Set zone to Direct mode
            if device.active_mode != 0:
                for i, mode in enumerate(device.modes):
                    if 'direct' in mode.name.lower():
                        device.set_mode(i)
                        break
            
            # Apply colors
            zone.set_colors(colors, fast=True)
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
            colors = build_led_colors(controller, device_index, zone_index, num_leds)
            
            # Set zone to Direct mode
            if device.active_mode != 0:
                for i, mode in enumerate(device.modes):
                    if 'direct' in mode.name.lower():
                        device.set_mode(i)
                        break
            
            # Apply colors in one operation
            zone.set_colors(colors, fast=True)
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
            
            # Reapply zone color (honoring brightness/saturation, same as static mode)
            zone_color = controller.db.get_color(device_index, zone_index)
            if zone_color:
                brightness, saturation = controller.db.get_brightness_saturation(device_index, zone_index)
                device = controller.client.devices[device_index]
                zone = device.zones[zone_index]
                zone.set_color(RGBColor(*apply_brightness_saturation(*zone_color, brightness, saturation)), fast=True)
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
                if controller.db.get_led_colors(device_index, zone_index):
                    num_leds = len(zone.leds) if hasattr(zone, 'leds') else zone.leds_count
                    zone.set_colors(build_led_colors(controller, device_index, zone_index, num_leds), fast=True)
                    device.show()
            else:
                # Disable LED control - apply zone color
                zone_color = controller.db.get_color(device_index, zone_index)
                if zone_color:
                    brightness, saturation = controller.db.get_brightness_saturation(device_index, zone_index)
                    zone.set_color(RGBColor(*apply_brightness_saturation(*zone_color, brightness, saturation)), fast=True)
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

            # Start this first and unconditionally. It used to run at the end of
            # the try block below, so if OpenRGB happened to be down on first
            # request the restore raised and the keepalive never started at all
            # for the life of the process — the app then stayed passive even
            # after OpenRGB came back.
            start_keepalive()

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
    
    @app.route('/api/settings/info')
    def settings_info():
        """Basic app info for the About section of the Settings panel"""
        import sys
        from kvg_rgb import __version__
        from kvg_rgb.paths import DATA_DIR
        from kvg_rgb.autostart import is_autostart_enabled

        return jsonify({
            'success': True,
            'version': __version__,
            'license': 'AGPL-3.0-or-later',
            'repo_url': 'https://github.com/gerp93/KVG_RGB',
            'standards_url': 'https://github.com/gerp93/KVG_Standards',
            'data_dir': str(DATA_DIR),
            'is_windows': sys.platform == 'win32',
            'autostart_enabled': is_autostart_enabled() if sys.platform == 'win32' else False,
        })

    @app.route('/api/settings/autostart', methods=['POST'])
    def set_autostart():
        """Enable/disable launching KVG RGB on Windows login"""
        import sys
        if sys.platform != 'win32':
            return jsonify({'success': False, 'error': 'Autostart is only available on Windows'}), 400

        from kvg_rgb.autostart import create_startup_shortcut, remove_startup_shortcut

        try:
            data = request.json
            enable = bool(data.get('enable', False))

            if enable:
                success, message = create_startup_shortcut()
            else:
                success, message = remove_startup_shortcut()

            return jsonify({'success': success, 'message': message, 'enabled': enable if success else not enable})
        except Exception as e:
            logger.error(f"Error toggling autostart: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/settings/database')
    def get_database_location():
        """Current + default SQLite database path"""
        from kvg_rgb.paths import db_location

        return jsonify({
            'success': True,
            'current_path': str(db_location.get_effective_db_path()),
            'default_path': str(db_location.get_default_db_path()),
            'is_default': db_location.is_using_default_location(),
        })

    @app.route('/api/settings/database/relocate', methods=['POST'])
    def relocate_database():
        """Point the app at a different SQLite file (existing or new). Requires a restart to take effect."""
        from pathlib import Path
        from kvg_rgb.paths import db_location

        try:
            data = request.json
            new_path = data.get('path', '').strip()
            if not new_path:
                return jsonify({'success': False, 'error': 'Path is required'}), 400

            # ColorDatabase opens/closes a fresh sqlite3 connection per call rather
            # than holding one open, so there's no persistent handle to close here.
            db_location.set_db_path(Path(new_path))
            return jsonify({'success': True, 'path': new_path, 'restart_required': True})
        except Exception as e:
            logger.error(f"Error relocating database: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/settings/database/reset', methods=['POST'])
    def reset_database_location():
        """Reset the database path back to the default location. Requires a restart to take effect."""
        from kvg_rgb.paths import db_location

        try:
            _global_controller_close()
            db_location.reset_to_default_db_path()
            return jsonify({'success': True, 'restart_required': True})
        except Exception as e:
            logger.error(f"Error resetting database location: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/settings/update-check')
    def update_check():
        """Check GitHub Releases for a newer build (no-op when running from source)"""
        from kvg_rgb import __version__
        from kvg_rgb.updater import check

        try:
            info = check()
            return jsonify({
                'success': True,
                'current_version': __version__,
                'update_available': info is not None,
                'latest_version': info['version'] if info else None,
                'download_url': info['download_url'] if info else None,
            })
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/settings/shortcut', methods=['POST'])
    def desktop_shortcut():
        """Create or remove a Desktop shortcut that launches the app"""
        import sys
        if sys.platform != 'win32':
            return jsonify({'success': False, 'error': 'Shortcuts are only available on Windows'}), 400

        from kvg_rgb.autostart import create_desktop_shortcut, remove_desktop_shortcut

        try:
            data = request.json
            action = data.get('action')

            if action == 'create':
                success, message = create_desktop_shortcut()
            elif action == 'remove':
                success, message = remove_desktop_shortcut()
            else:
                return jsonify({'success': False, 'error': f'Unknown action: {action}'}), 400

            return jsonify({'success': success, 'message': message})
        except Exception as e:
            logger.error(f"Error managing desktop shortcut: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/settings/theme')
    def get_theme():
        """Current theme + the full list of available VisualAssault themes"""
        from kvg_rgb.database import VALID_THEMES

        controller = get_controller()
        return jsonify({'success': True, 'theme': controller.db.get_theme(), 'themes': VALID_THEMES})

    @app.route('/api/settings/theme', methods=['POST'])
    def set_theme():
        """Persist the chosen theme (applied client-side without a reload)"""
        from kvg_rgb.database import VALID_THEMES

        try:
            data = request.json
            theme = data.get('theme')
            if theme not in VALID_THEMES:
                return jsonify({'success': False, 'error': f'Unknown theme: {theme}'}), 400

            controller = get_controller()
            controller.db.set_theme(theme)
            return jsonify({'success': True, 'theme': theme})
        except Exception as e:
            logger.error(f"Error setting theme: {e}")
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
