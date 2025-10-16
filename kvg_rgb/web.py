#!/usr/bin/env python3
"""
Flask web interface for KVG RGB Controller
Provides a local web UI for controlling RGB devices
"""
from flask import Flask, render_template, jsonify, request
from .core import RGBController
import webbrowser
import threading
import time

# Global controller instance to maintain state across requests
_global_controller = None

def get_controller():
    """Get or create the global controller instance"""
    global _global_controller
    if _global_controller is None:
        _global_controller = RGBController()
    return _global_controller


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
                        zones.append({
                            'index': zone_idx,
                            'name': zone.name,
                            'type': zone.type,
                            'leds': len(zone.leds),
                            'leds_min': getattr(zone, 'leds_min', None),
                            'leds_max': getattr(zone, 'leds_max', None),
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
            duration = data.get('duration', 2)  # Default 2 seconds
            
            if device_index is None or zone_index is None:
                return jsonify({'success': False, 'error': 'Missing device_index or zone_index'}), 400
            
            # Flash in background thread
            def run_flash():
                import time
                from openrgb.utils import RGBColor
                
                controller = get_controller()
                device = controller.client.devices[device_index]
                
                # Save current color
                old_colors = []
                zone = device.zones[zone_index]
                for led in zone.leds:
                    old_colors.append(device.colors[led.id])
                
                # Flash white
                white = RGBColor(255, 255, 255)
                zone.set_color(white)
                device.update()
                
                time.sleep(duration)
                
                # Restore original colors
                for i, led in enumerate(zone.leds):
                    if i < len(old_colors):
                        device.leds[led.id].set_color(old_colors[i])
                device.update()
            
            thread = threading.Thread(target=run_flash, daemon=True)
            thread.start()
            
            return jsonify({'success': True})
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
    
    @app.route('/api/zone/resize', methods=['POST'])
    def resize_zone():
        """Resize a zone"""
        try:
            data = request.json
            device_index = int(data['device'])
            zone_index = int(data['zone'])
            new_size = int(data['size'])
            
            controller = get_controller()
            devices = controller.get_devices()
            device = devices[device_index]
            zone = device.zones[zone_index]
            zone.resize(new_size)
            
            # Refresh and verify
            time.sleep(0.3)
            devices = controller.get_devices()
            device = devices[device_index]
            zone = device.zones[zone_index]
            
            return jsonify({
                'success': True, 
                'new_size': len(zone.leds)
            })
        except Exception as e:
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
