"""
Command-line interface for KVG RGB Controller
"""
import sys
import argparse
from kvg_rgb.core import RGBController


def list_devices():
    """List all connected RGB devices"""
    try:
        with RGBController() as controller:
            devices = controller.get_devices()
            print(f"\nFound {len(devices)} RGB device(s)\n")
            
            for i, device in enumerate(devices):
                print(f"{'='*60}")
                print(f"Device {i}: {device.name}")
                print(f"{'='*60}")
                print(f"  Type: {device.type}")
                print(f"  LEDs: {len(device.leds)}")
                print(f"  Zones: {len(device.zones)}")
                print(f"  Modes: {len(device.modes)}")
                
                print(f"\n  Available modes:")
                for mode in device.modes:
                    print(f"    - {mode.name}")
                print()
                
    except ConnectionError:
        print("Error: Could not connect to OpenRGB server.")
        print("Make sure OpenRGB is running and SDK Server is enabled.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def list_zones():
    """List all devices with their zones"""
    try:
        with RGBController() as controller:
            devices = controller.get_devices()
            print("\n" + "="*70)
            print("  OpenRGB Devices and Zones")
            print("="*70 + "\n")
            
            for dev_idx, device in enumerate(devices):
                print(f"[Device {dev_idx}] {device.name}")
                print(f"  Type: {device.type}")
                print(f"  Total LEDs: {len(device.leds)}")
                print(f"  Zones: {len(device.zones)}")
                
                if device.zones:
                    print(f"\n  Zone Details:")
                    for zone_idx, zone in enumerate(device.zones):
                        print(f"    [Zone {zone_idx}] {zone.name}")
                        print(f"      - Type: {zone.type}")
                        print(f"      - LEDs in zone: {len(zone.leds)}")
                else:
                    print("  No zones available")
                
                print()
                
    except ConnectionError:
        print("Error: Could not connect to OpenRGB server.")
        print("Make sure OpenRGB is running and SDK Server is enabled.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def resize_zone_command(args):
    """Resize a zone command"""
    try:
        with RGBController() as controller:
            devices = controller.get_devices()
            
            # Validate device index
            if args.device < 0 or args.device >= len(devices):
                print(f"Error: Invalid device index {args.device}")
                print(f"Available devices: 0-{len(devices)-1}")
                sys.exit(1)
            
            device = devices[args.device]
            
            # Validate zone index
            if args.zone < 0 or args.zone >= len(device.zones):
                print(f"Error: Invalid zone index {args.zone}")
                print(f"Available zones for {device.name}: 0-{len(device.zones)-1}")
                sys.exit(1)
            
            zone = device.zones[args.zone]
            
            print(f"Resizing: {device.name} - Zone {args.zone} ({zone.name})")
            print(f"Current size: {len(zone.leds)} LEDs")
            print(f"New size: {args.size} LEDs")
            
            # Perform resize
            zone.resize(args.size)
            
            # Refresh and verify
            import time
            time.sleep(0.3)
            device = controller.get_devices()[args.device]
            zone = device.zones[args.zone]
            
            print(f"✓ Successfully resized to {len(zone.leds)} LEDs!")
            
    except AttributeError:
        print("Error: This zone does not support resizing.")
        sys.exit(1)
    except ConnectionError:
        print("Error: Could not connect to OpenRGB server.")
        sys.exit(1)
    except Exception as e:
        print(f"Error resizing zone: {e}")
        sys.exit(1)


def list_devices():
    """List all connected RGB devices"""
    try:
        with RGBController() as controller:
            devices = controller.get_devices()
            print(f"\nFound {len(devices)} RGB device(s)\n")
            
            for i, device in enumerate(devices):
                print(f"{'='*60}")
                print(f"Device {i}: {device.name}")
                print(f"{'='*60}")
                print(f"  Type: {device.type}")
                print(f"  LEDs: {len(device.leds)}")
                print(f"  Zones: {len(device.zones)}")
                print(f"  Modes: {len(device.modes)}")
                
                print(f"\n  Available modes:")
                for mode in device.modes:
                    print(f"    - {mode.name}")
                print()
                
    except ConnectionError:
        print("Error: Could not connect to OpenRGB server.")
        print("Make sure OpenRGB is running and SDK Server is enabled.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def set_color_command(args):
    """Set color command"""
    try:
        with RGBController() as controller:
            controller.set_color(args.r, args.g, args.b, args.device)
            if args.device is not None:
                print(f"Set device {args.device} to RGB({args.r}, {args.g}, {args.b})")
            else:
                print(f"Set all devices to RGB({args.r}, {args.g}, {args.b})")
    except ConnectionError:
        print("Error: Could not connect to OpenRGB server.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def rainbow_command(args):
    """Rainbow effect command"""
    try:
        with RGBController() as controller:
            print(f"Starting rainbow effect for {args.duration} seconds...")
            print("Press Ctrl+C to stop\n")
            controller.rainbow_effect(duration=args.duration, speed=args.speed, device_index=args.device)
            print("\nRainbow effect complete!")
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except ConnectionError:
        print("Error: Could not connect to OpenRGB server.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def breathe_command(args):
    """Breathing effect command"""
    try:
        with RGBController() as controller:
            print(f"Starting breathing effect with RGB({args.r}, {args.g}, {args.b}) for {args.duration} seconds...")
            print("Press Ctrl+C to stop\n")
            controller.breathing_effect(args.r, args.g, args.b, duration=args.duration, speed=args.speed, device_index=args.device)
            print("\nBreathing effect complete!")
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except ConnectionError:
        print("Error: Could not connect to OpenRGB server.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def exclude_device_command(args):
    """Exclude a device from RGB control"""
    try:
        from kvg_rgb.config import get_config
        with RGBController() as controller:
            devices = controller.get_all_devices()
            if args.device < 0 or args.device >= len(devices):
                print(f"Error: Invalid device index {args.device}")
                print(f"Valid range: 0-{len(devices)-1}")
                sys.exit(1)
            
            device = devices[args.device]
            config = get_config()
            config.exclude_device(device.name)
            print(f"✓ Excluded device: {device.name}")
            print(f"  This device will no longer respond to RGB commands")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def include_device_command(args):
    """Include a previously excluded device"""
    try:
        from kvg_rgb.config import get_config
        with RGBController() as controller:
            devices = controller.get_all_devices()
            if args.device < 0 or args.device >= len(devices):
                print(f"Error: Invalid device index {args.device}")
                print(f"Valid range: 0-{len(devices)-1}")
                sys.exit(1)
            
            device = devices[args.device]
            config = get_config()
            if config.include_device(device.name):
                print(f"✓ Included device: {device.name}")
                print(f"  This device will now respond to RGB commands")
            else:
                print(f"Device '{device.name}' was not excluded")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def list_excluded_devices():
    """List all excluded devices"""
    try:
        from kvg_rgb.config import get_config
        config = get_config()
        excluded = config.get_excluded_devices()
        
        if not excluded:
            print("\nNo devices are currently excluded")
            print("All devices will respond to RGB commands")
        else:
            print(f"\n{'='*60}")
            print(f"  Excluded Devices ({len(excluded)})")
            print(f"{'='*60}\n")
            for device_name in excluded:
                print(f"  ✗ {device_name}")
            print(f"\nThese devices will NOT respond to RGB commands")
            print(f"Use 'kvg-rgb include <device_index>' to re-enable them\n")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="KVG RGB Controller - Control your RGB devices via OpenRGB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kvg-rgb list                              List all devices
  kvg-rgb zones                             List all devices and zones
  kvg-rgb color 255 0 0                     Set all devices to red
  kvg-rgb color 0 255 0 --device 0          Set device 0 to green
  kvg-rgb resize 1 3 35                     Resize device 1, zone 3 to 35 LEDs
  kvg-rgb rainbow --duration 30             30 second rainbow effect
  kvg-rgb breathe 0 150 255 --speed 2       Fast blue breathing effect
  kvg-rgb web                               Start web interface
  kvg-rgb exclude 2                         Exclude device 2 from RGB control
  kvg-rgb include 2                         Re-enable device 2
  kvg-rgb excluded                          List excluded devices
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    subparsers.add_parser('list', help='List all RGB devices')
    
    # Zones command
    subparsers.add_parser('zones', help='List all devices with zones')
    
    # Resize command
    resize_parser = subparsers.add_parser('resize', help='Resize a zone')
    resize_parser.add_argument('device', type=int, help='Device index')
    resize_parser.add_argument('zone', type=int, help='Zone index')
    resize_parser.add_argument('size', type=int, help='New size in LEDs')
    
    # Color command
    color_parser = subparsers.add_parser('color', help='Set device(s) to a specific color')
    color_parser.add_argument('r', type=int, help='Red value (0-255)')
    color_parser.add_argument('g', type=int, help='Green value (0-255)')
    color_parser.add_argument('b', type=int, help='Blue value (0-255)')
    color_parser.add_argument('--device', type=int, default=None, help='Specific device index (default: all)')
    
    # Rainbow command
    rainbow_parser = subparsers.add_parser('rainbow', help='Run rainbow effect')
    rainbow_parser.add_argument('--duration', type=int, default=60, help='Duration in seconds (default: 60)')
    rainbow_parser.add_argument('--speed', type=float, default=1.0, help='Speed multiplier (default: 1.0)')
    rainbow_parser.add_argument('--device', type=int, default=None, help='Specific device index (default: all)')
    
    # Breathe command
    breathe_parser = subparsers.add_parser('breathe', help='Run breathing effect')
    breathe_parser.add_argument('r', type=int, help='Red value (0-255)')
    breathe_parser.add_argument('g', type=int, help='Green value (0-255)')
    breathe_parser.add_argument('b', type=int, help='Blue value (0-255)')
    breathe_parser.add_argument('--duration', type=int, default=60, help='Duration in seconds (default: 60)')
    breathe_parser.add_argument('--speed', type=float, default=1.0, help='Speed multiplier (default: 1.0)')
    breathe_parser.add_argument('--device', type=int, default=None, help='Specific device index (default: all)')
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Start web interface')
    web_parser.add_argument('--host', type=str, default='127.0.0.1', help='Host address (default: 127.0.0.1)')
    web_parser.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    web_parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    
    # Exclude/Include commands
    exclude_parser = subparsers.add_parser('exclude', help='Exclude a device from RGB control')
    exclude_parser.add_argument('device', type=int, help='Device index to exclude')
    
    include_parser = subparsers.add_parser('include', help='Include a previously excluded device')
    include_parser.add_argument('device', type=int, help='Device index to include')
    
    subparsers.add_parser('excluded', help='List excluded devices')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Route to appropriate command
    if args.command == 'list':
        list_devices()
    elif args.command == 'zones':
        list_zones()
    elif args.command == 'resize':
        resize_zone_command(args)
    elif args.command == 'color':
        set_color_command(args)
    elif args.command == 'rainbow':
        rainbow_command(args)
    elif args.command == 'breathe':
        breathe_command(args)
    elif args.command == 'web':
        from kvg_rgb.web import run_web_server
        run_web_server(
            host=args.host,
            port=args.port,
            open_browser_window=not args.no_browser
        )
    elif args.command == 'exclude':
        exclude_device_command(args)
    elif args.command == 'include':
        include_device_command(args)
    elif args.command == 'excluded':
        list_excluded_devices()


if __name__ == "__main__":
    main()
