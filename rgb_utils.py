"""
Utility functions for OpenRGB device control
"""
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType
from typing import List, Optional


def get_client(host: str = "localhost", port: int = 6742) -> OpenRGBClient:
    """
    Connect to OpenRGB server
    
    Args:
        host: Server hostname (default: localhost)
        port: Server port (default: 6742)
    
    Returns:
        OpenRGBClient instance
    """
    try:
        client = OpenRGBClient(host, port)
        return client
    except ConnectionError:
        raise ConnectionError(
            "Could not connect to OpenRGB. "
            "Ensure OpenRGB is running with SDK Server enabled."
        )


def set_all_devices_color(client: OpenRGBClient, color: RGBColor) -> None:
    """
    Set all devices to a specific color
    
    Args:
        client: OpenRGBClient instance
        color: RGBColor to set
    """
    for device in client.devices:
        device.set_color(color)
        print(f"Set {device.name} to RGB{color}")


def set_device_by_name(
    client: OpenRGBClient, 
    device_name: str, 
    color: RGBColor
) -> bool:
    """
    Set a specific device to a color by name
    
    Args:
        client: OpenRGBClient instance
        device_name: Name of the device to control
        color: RGBColor to set
    
    Returns:
        True if device was found and set, False otherwise
    """
    for device in client.devices:
        if device_name.lower() in device.name.lower():
            device.set_color(color)
            print(f"Set {device.name} to RGB{color}")
            return True
    
    print(f"Device '{device_name}' not found")
    return False


def list_all_devices(client: OpenRGBClient) -> List[dict]:
    """
    Get information about all connected devices
    
    Args:
        client: OpenRGBClient instance
    
    Returns:
        List of device information dictionaries
    """
    devices_info = []
    
    for device in client.devices:
        info = {
            "name": device.name,
            "type": device.type,
            "modes": [mode.name for mode in device.modes],
            "led_count": len(device.leds),
            "zone_count": len(device.zones)
        }
        devices_info.append(info)
    
    return devices_info


def set_mode_by_name(
    client: OpenRGBClient, 
    device_name: str, 
    mode_name: str
) -> bool:
    """
    Set a device to a specific mode by name
    
    Args:
        client: OpenRGBClient instance
        device_name: Name of the device to control
        mode_name: Name of the mode to activate
    
    Returns:
        True if successful, False otherwise
    """
    for device in client.devices:
        if device_name.lower() in device.name.lower():
            for mode in device.modes:
                if mode_name.lower() in mode.name.lower():
                    device.set_mode(mode)
                    print(f"Set {device.name} to mode: {mode.name}")
                    return True
            print(f"Mode '{mode_name}' not found on device '{device.name}'")
            return False
    
    print(f"Device '{device_name}' not found")
    return False


# Predefined color constants
class Colors:
    RED = RGBColor(255, 0, 0)
    GREEN = RGBColor(0, 255, 0)
    BLUE = RGBColor(0, 0, 255)
    WHITE = RGBColor(255, 255, 255)
    BLACK = RGBColor(0, 0, 0)
    YELLOW = RGBColor(255, 255, 0)
    CYAN = RGBColor(0, 255, 255)
    MAGENTA = RGBColor(255, 0, 255)
    ORANGE = RGBColor(255, 165, 0)
    PURPLE = RGBColor(128, 0, 128)
