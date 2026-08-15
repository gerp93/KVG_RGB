# OpenRGB Python Development Environment

This project provides Python scripts for controlling RGB devices using OpenRGB with a professional CLI interface.

This repo follows [KVG_Standards](https://github.com/gerp93/KVG_Standards) for theming, licensing, release/CI, update-check, and database-location conventions shared across gerp93's app repos.

## Quick Links

� [Installation Guide](docs/INSTALL.md) | �📖 [Quick Start Guide](docs/QUICKSTART.md) | 🚀 [Release Guide](docs/RELEASE.md) | 🔧 [Troubleshooting](docs/TROUBLESHOOTING.md) | 📝 [Changelog](docs/CHANGELOG.md)

## Features

- 🎨 Control all your RGB devices from the command line
- 🌈 Built-in effects (rainbow, breathing)
- 🌐 **Desktop App** - Native window UI (or a browser tab, if you prefer)
- 🔧 Extensible architecture for future GUI development
- 📦 Can be packaged as standalone executable for sharing
- 🎛️ Zone management - resize addressable RGB zones on compatible devices


## Installation

### For End Users (Distributed Package)

Download the build for your platform from the [latest release](https://github.com/gerp93/KVG_RGB/releases/latest) and run it directly — no installer needed:

- **Windows** — `KVG_RGB-windows.exe`
- **macOS** — `KVG_RGB-macos` (make it executable first: `chmod +x KVG_RGB-macos`)
- **Linux** — `KVG_RGB-linux` (make it executable first: `chmod +x KVG_RGB-linux`)

These builds are unsigned, so Windows SmartScreen / macOS Gatekeeper will warn about an unrecognized publisher — click through to launch it. The app checks for updates itself (see Settings inside the app).

**Your settings are preserved across updates!**
- All data is stored in `~/.kvg_rgb/` (or `%USERPROFILE%\.kvg_rgb\` on Windows), and relocatable via Settings → Database Location
- Colors, LED configurations, and profiles persist across updates
- Works on Windows, macOS, and Linux

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

Note: the app checks for OpenRGB itself at startup and shows a clear message in the window if it can't connect, instead of failing silently.

## Files

### Package Structure
- `kvg_rgb/` - Main package folder
  - `__init__.py` - Package initialization
  - `core.py` - Core RGB controller class (reusable by CLI or GUI)
  - `web.py` - Flask backend + HTTP API
  - `gui.py` - Desktop window entry point (pywebview) — what CI packages
  - `cli.py` - Command-line interface
- `main.py` - CLI-only entry point (used by `build_exe.py`)
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies (PyInstaller)
- `build_exe.py` - Script to build a standalone CLI-only executable

## Usage

### Desktop App (Recommended)

The easiest way to control your RGB devices — a native window, no browser tab:

```powershell
kvg-rgb gui
```

**Features:**
- 🎨 **Color Picker** - Visual color selection with RGB sliders
- 🎯 **Quick Presets** - One-click common colors
- ✨ **Effects** - Rainbow and breathing effects with speed control
- 🎛️ **Zone Management** - Resize addressable RGB zones
- 🖥️ **Device Selection** - Control all devices or specific ones
- ⚙️ **Settings panel** - Theme picker, autostart, database location, update check

Prefer a browser tab instead (e.g. for remote/headless use)?

```powershell
kvg-rgb web
kvg-rgb web --port 8080
kvg-rgb web --no-browser
```

### 🚀 Auto-start on Windows Boot

To make KVG RGB start automatically when you log in to Windows:

**Easiest: the app's own Settings panel** — open Settings (⚙️) inside the app and toggle "Start KVG RGB Controller when Windows starts."

**Option 1: CLI**

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

4. **Done!** The RGB controller will now start automatically (as a desktop window) when you log in.

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

## Building the Desktop App Locally

The distributed app (`kvg-rgb gui`) is built and published automatically by
CI on every release — see [RELEASE.md](docs/RELEASE.md). To build it
locally instead (for testing packaging changes):

```powershell
.\venv\Scripts\Activate.ps1
pip install pyinstaller
pyinstaller --onefile --windowed --name KVG_RGB kvg_rgb/gui.py
```

There's also a CLI-only executable (`build_exe.py`/`kvg-rgb.spec`) for
users who just want `kvg-rgb list`/`kvg-rgb color` without the desktop
window:

```powershell
pip install -r requirements-dev.txt
python build_exe.py
```

The CLI executable is created at `dist\kvg-rgb.exe`.

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

## License & Terms

This project is released under the **GNU Affero General Public License v3 (AGPLv3)** - see [LICENSE](LICENSE) for details.

**Key Points (summary):**
- 🔁 Strong copyleft: If you modify this software and run it as a network service,
   you must make the modified source code available under AGPLv3 to your users.
- ✅ You may use, modify, and distribute the software, but derived works must also be
   licensed under AGPLv3 when conveyed or offered over a network.
- 📋 Preserve copyright and license notices when redistributing.

For detailed terms of use, see [TERMS.md](TERMS.md).

## Contributing

Contributions are welcome! By contributing you agree to license your changes under AGPLv3.

- 🐛 Report bugs via GitHub Issues
- 💡 Suggest features via GitHub Issues
- 🔧 Submit pull requests
- ⭐ Star the repo if you find it useful

## Acknowledgments

- **OpenRGB Project** - For making RGB control possible
- **Python OpenRGB** - For the Python SDK
- **Flask** - For the web framework
- **pywebview** - For the native desktop window
- **All Contributors** - Thank you!
