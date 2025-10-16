#!/usr/bin/env python3
"""
Zone management script for OpenRGB devices
Allows viewing and resizing zones for RGB devices
"""
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType
import sys


def list_devices_and_zones():
    """List all devices with their zones"""
    try:
        client = OpenRGBClient()
        print("\n" + "="*70)
        print("  OpenRGB Devices and Zones")
        print("="*70 + "\n")
        
        devices = client.devices
        
        if not devices:
            print("No devices found!")
            client.disconnect()
            return None, None
        
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
                    
                    # Check if zone has resize capability
                    try:
                        if hasattr(zone, 'leds_min') and hasattr(zone, 'leds_max'):
                            print(f"      - Min Size: {zone.leds_min}")
                            print(f"      - Max Size: {zone.leds_max}")
                            if zone.leds_min != zone.leds_max:
                                print(f"      - ✓ Resizable (can be {zone.leds_min}-{zone.leds_max} LEDs)")
                            else:
                                print(f"      - ✗ Fixed size (cannot be resized)")
                        else:
                            # Try to get zone info from device metadata
                            print(f"      - ℹ Resize capability unknown")
                    except Exception:
                        print(f"      - ℹ Resize capability unknown")
            else:
                print("  No zones available")
            
            print()
        
        return client, devices
        
    except ConnectionError:
        print("Error: Could not connect to OpenRGB server.")
        print("Make sure OpenRGB is running and SDK Server is enabled.")
        return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None


def resize_zone(client, devices):
    """Interactive zone resizing"""
    try:
        # Get device
        device_idx = int(input("\nEnter device number: "))
        if device_idx < 0 or device_idx >= len(devices):
            print("Invalid device number!")
            return False
        
        device = devices[device_idx]
        
        if not device.zones:
            print("This device has no zones!")
            return False
        
        # Get zone
        zone_idx = int(input(f"Enter zone number (0-{len(device.zones)-1}): "))
        if zone_idx < 0 or zone_idx >= len(device.zones):
            print("Invalid zone number!")
            return False
        
        zone = device.zones[zone_idx]
        
        print(f"\nSelected: {device.name} - Zone {zone_idx} ({zone.name})")
        current_size = len(zone.leds)
        print(f"Current size: {current_size} LEDs")

        # Try to read allowed bounds from various possible attribute names
        leds_min = getattr(zone, 'leds_min', None)
        if leds_min is None:
            leds_min = getattr(zone, 'min_leds', None)
        leds_max = getattr(zone, 'leds_max', None)
        if leds_max is None:
            leds_max = getattr(zone, 'max_leds', None)

        if leds_min is not None and leds_max is not None:
            print(f"Allowed range: {leds_min} - {leds_max} LEDs")
            # Check if resizable
            if leds_min == leds_max:
                print("\n❌ This zone cannot be resized (fixed size).")
                return False
            # Prompt within known bounds
            prompt = f"\nEnter new size ({leds_min}-{leds_max}): "
        else:
            print("Allowed range: unknown (SDK didn't report min/max)")
            print("We'll attempt to resize; device may reject unsupported sizes.")
            # Use a generic prompt
            prompt = "\nEnter new size (>0): "

        # Get new size
        new_size = int(input(prompt))

        # Validate if we know bounds; otherwise just basic sanity
        if leds_min is not None and leds_max is not None:
            if new_size < leds_min or new_size > leds_max:
                print(f"❌ Invalid size! Must be between {leds_min} and {leds_max}.")
                return False
        else:
            if new_size <= 0:
                print("❌ Invalid size! Must be greater than 0.")
                return False
        
        # Confirm
        confirm = input(f"\nResize '{zone.name}' from {len(zone.leds)} to {new_size} LEDs? (y/n): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return False
        
        # Perform resize using zone.resize() method
        try:
            zone.resize(new_size)
        except AttributeError:
            print("\n❌ This zone does not support resizing (no resize method).")
            return False
        except Exception as e:
            print(f"\n❌ Resize failed: {e}")
            return False

        print(f"\n✓ Successfully resized zone to {new_size} LEDs!")
        
        # Show updated info
        device = client.devices[device_idx]  # Refresh device data
        zone = device.zones[zone_idx]
        print(f"New zone size: {len(zone.leds)} LEDs")
        
        return True
        
    except ValueError:
        print("Invalid input! Please enter a number.")
        return False
    except Exception as e:
        print(f"Error resizing zone: {e}")
        return False


def main():
    """Main interactive loop"""
    print("\n" + "="*70)
    print("  OpenRGB Zone Manager")
    print("="*70)
    print("\nThis tool allows you to view and resize zones on your RGB devices.")
    print("Note: Not all zones can be resized (depends on device).")
    
    # List devices first
    client, devices = list_devices_and_zones()
    
    if not client or not devices:
        return
    
    try:
        while True:
            print("\n" + "-"*70)
            print("Options:")
            print("  [1] List devices and zones again")
            print("  [2] Resize a zone")
            print("  [q] Quit")
            print("-"*70)
            
            choice = input("\nChoice: ").strip().lower()
            
            if choice == '1':
                list_devices_and_zones()
            elif choice == '2':
                resize_zone(client, devices)
                # Refresh device list after resize
                devices = client.devices
            elif choice == 'q':
                print("\nGoodbye!")
                break
            else:
                print("Invalid choice!")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
