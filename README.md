# OpenRGB Python Development Environment

This project provides Python scripts for controlling RGB devices using OpenRGB with a professional CLI interface.

## Quick Links

� [Installation Guide](docs/INSTALL.md) | �📖 [Quick Start Guide](docs/QUICKSTART.md) | 🚀 [Release Guide](docs/RELEASE.md) | 🔧 [Troubleshooting](docs/TROUBLESHOOTING.md) | 📝 [Changelog](docs/CHANGELOG.md)

## Features

- 🎨 Control all your RGB devices from the command line
- 🌈 Built-in effects (rainbow, breathing)
- 🌐 **Web UI** - Modern browser-based control interface
- 🔧 Extensible architecture for future GUI development
- 📦 Can be packaged as standalone executable for sharing
- 🎛️ Zone management - resize addressable RGB zones on compatible devices


## Installation

### For End Users (Distributed Package)

If you received a `.whl` file from a release:

```bash
# Fresh installation
pip install kvg_rgb-X.X.X-py3-none-any.whl

# Upgrade from previous version
pip install --upgrade --force-reinstall kvg_rgb-X.X.X-py3-none-any.whl
```

**Your settings are preserved across updates!** 
- All data is stored in `~/.kvg_rgb/` (or `%USERPROFILE%\.kvg_rgb\` on Windows)
- Colors, LED configurations, and profiles persist across updates
- Works on Windows, macOS, and Linux

📦 **See the full [Installation Guide](docs/INSTALL.md)** for detailed instructions.

### For Developers (From Source)

Install the package in development mode to use it from anywhere:

```powershell
# Navigate to the project directory
cd C:\Users\kgerp\source\repos\KVG_RGB

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install the package
pip install -e .
```

Now you can use `kvg-rgb` command from anywhere in your terminal!

```powershell
kvg-rgb list
kvg-rgb color 255 0 0
```

3. **Dependencies are already installed**, but if you need to reinstall:
   ```powershell
   pip install -r requirements.txt
   ```

## Prerequisites

- **OpenRGB** must be installed and running
- **SDK Server** must be enabled in OpenRGB:
  - Open OpenRGB
  - Go to Settings (gear icon)
  - Enable "Start SDK Server"
  - Default port is 6742

## Files

### Package Structure
- `kvg_rgb/` - Main package folder
  - `__init__.py` - Package initialization
  - `core.py` - Core RGB controller class (reusable by CLI or GUI)
  - `cli.py` - Command-line interface
- `main.py` - Entry point script
- `rgb_utils.py` - Legacy utility functions (for reference)
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies (PyInstaller)
- `build_exe.py` - Script to build standalone executable

## Usage

### Web Interface (Recommended)

The easiest way to control your RGB devices is through the web interface:

```powershell
# Start the web server (browser opens automatically)
kvg-rgb web

# Customize host/port if needed
kvg-rgb web --port 8080

# Start without auto-opening browser
kvg-rgb web --no-browser
```

**Features of the Web UI:**
- 🎨 **Color Picker** - Visual color selection with RGB sliders
- 🎯 **Quick Presets** - One-click common colors
- ✨ **Effects** - Rainbow and breathing effects with speed control
- 🎛️ **Zone Management** - Resize addressable RGB zones
- 🖥️ **Device Selection** - Control all devices or specific ones
- 📱 **Responsive** - Works on desktop, tablet, and mobile browsers

The web interface runs **locally on your machine** at `http://localhost:5000`. No internet connection needed!

### 🚀 Auto-start on Windows Boot

To make KVG RGB start automatically when you log in to Windows:

**Option 1: Automatic Setup (Easiest)**

```powershell
# Interactive setup - will guide you through the process
kvg-rgb autostart

# Or enable directly
kvg-rgb autostart --enable

# Check if autostart is enabled
kvg-rgb autostart --status

# Disable autostart
kvg-rgb autostart --disable
```

**Option 2: Manual Setup**

1. **Locate the startup script**:
   - After installation, find: `start_kvg_rgb.bat` in your Python installation
   - Typically located at: `C:\Python3XX\Lib\site-packages\kvg_rgb\scripts\start_kvg_rgb.bat`
   - Or use: `python -c "import kvg_rgb, os; print(os.path.join(os.path.dirname(kvg_rgb.__file__), 'scripts', 'start_kvg_rgb.bat'))"`

2. **Create a shortcut**:
   - Right-click `start_kvg_rgb.bat`
   - Select **"Create shortcut"**

3. **Add to Windows Startup**:
   - Press `Win + R`
   - Type: `shell:startup`
   - Press Enter
   - Move the shortcut to the Startup folder

4. **Done!** The RGB controller will now start automatically (minimized in background) when you log in.

To disable auto-start, use `kvg-rgb autostart --disable` or delete the shortcut from the Startup folder.

### Command-Line Interface

```powershell
# Show all available commands
kvg-rgb --help

# List all RGB devices
kvg-rgb list

# View devices with their zones and LED counts
kvg-rgb zones

# Resize a zone (e.g., device 1, zone 3, to 35 LEDs)
kvg-rgb resize 1 3 35

# Set all devices to red
kvg-rgb color 255 0 0

# Set specific device to green (use device index from list command)
kvg-rgb color 0 255 0 --device 0

# Run rainbow effect for 30 seconds
kvg-rgb rainbow --duration 30

# Run rainbow effect on specific device with custom speed
kvg-rgb rainbow --duration 60 --speed 2.0 --device 1

# Run breathing effect (cyan)
kvg-rgb breathe 0 150 255

# Run breathing effect with custom duration and speed
kvg-rgb breathe 255 0 0 --duration 45 --speed 1.5
```

### Zone Management

Many RGB devices (especially motherboards) have addressable RGB headers with resizable zones. You can view and resize these zones using the CLI:

```powershell
# View all devices with their zones
kvg-rgb zones

# Example output:
# [Device 1] ASUS PRIME Z890-P WIFI
#   Total LEDs: 96
#   Zones: 4
#
#   Zone Details:
#     [Zone 0] Aura Mainboard - 1 LED
#     [Zone 1] Aura Addressable 1 - 30 LEDs
#     [Zone 2] Aura Addressable 2 - 30 LEDs
#     [Zone 3] Aura Addressable 3 - 35 LEDs

# Resize a zone: kvg-rgb resize <device_index> <zone_index> <new_size>
kvg-rgb resize 1 3 50  # Resize device 1, zone 3 to 50 LEDs

# Interactive zone manager (standalone script)
python zone_manager.py
```

**Note**: Zone resizing is useful when you've added or removed RGB strips from your motherboard's addressable headers. Not all zones can be resized - it depends on the device capabilities.

### Using as Python Module

```python
from kvg_rgb.core import RGBController

# Connect to OpenRGB
with RGBController() as controller:
    # Get all devices
    devices = controller.get_devices()
    
    # Set all devices to purple
    controller.set_color(128, 0, 128)
    
    # Run rainbow effect for 10 seconds
    controller.rainbow_effect(duration=10, speed=1.5)
```

## Available Commands & Functions

### CLI Commands

- `list` - List all RGB devices with basic info
- `zones` - List all devices with detailed zone information
- `resize <device> <zone> <size>` - Resize a specific zone
- `color <r> <g> <b>` - Set device(s) to a solid color
- `rainbow` - Run rainbow cycling effect
- `breathe <r> <g> <b>` - Run breathing/pulsing effect

### Python API

See `kvg_rgb/core.py` for the full RGBController class:

- `get_devices()` - Get list of all RGB devices
- `set_color(r, g, b, device_index=None)` - Set device(s) to a color
- `rainbow_effect(duration, speed, device_index=None)` - Rainbow cycling effect
- `breathing_effect(r, g, b, duration, speed, device_index=None)` - Breathing/pulsing effect

See `kvg_rgb/cli.py` for CLI-specific functions:

- `list_devices()` - List all devices
- `list_zones()` - List devices with zone details
- `resize_zone_command(args)` - Resize a zone
- `set_color_command(args)` - Set color command handler
- `rainbow_command(args)` - Rainbow effect command handler
- `breathe_command(args)` - Breathing effect command handler

## Building Standalone Executable

To create a shareable `.exe` file that doesn't require Python:

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Install PyInstaller
pip install -r requirements-dev.txt

# Build the executable
python build_exe.py
```

The executable will be created in `dist\kvg-rgb.exe`. You can:
- Copy it to a folder in your PATH (like `C:\Windows\`)
- Share it with others (they don't need Python or OpenRGB SDK installed)
- Run it from anywhere: `kvg-rgb.exe list`

## Troubleshooting

If you get a connection error:
1. Make sure OpenRGB is running
2. Check that SDK Server is enabled in OpenRGB settings
3. Verify the port (default: 6742)

For more detailed troubleshooting, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Documentation

- 📖 [Quick Start Guide](docs/QUICKSTART.md) - Get up and running quickly
- 🚀 [Release Guide](docs/RELEASE.md) - How to build and release
- 🔧 [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions
- 📝 [Changelog](docs/CHANGELOG.md) - Version history and updates
- ✅ [TODO](TODO.md) - Development roadmap and planned features
