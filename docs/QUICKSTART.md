# KVG RGB Controller - Quick Reference

## Getting Started (For End Users)

### 1. **Easiest: Launch the App**

Double-click the downloaded executable (or, from source: `kvg-rgb gui`).
It opens as a normal desktop window — no browser tab, no terminal needed.
Use the visual color picker and effect controls right there.

Prefer a browser tab instead (e.g. for remote/headless use)? `kvg-rgb web`
still works and opens `http://localhost:5000`.

### 2. **Alternative: Command Line**
```powershell
# List your RGB devices
kvg-rgb list

# Set all devices to red
kvg-rgb color 255 0 0

# Run rainbow effect
kvg-rgb rainbow
```

---

## Project Structure
```
KVG_RGB/
├── kvg_rgb/              # Main package
│   ├── __init__.py       # Package init
│   ├── core.py           # RGB controller class
│   ├── web.py            # Flask backend + routes
│   ├── gui.py            # Desktop window entry point (pywebview)
│   ├── database.py       # SQLite persistence
│   ├── updater.py        # Self-update check
│   └── cli.py            # CLI interface
├── requirements.txt      # Dependencies
├── requirements-dev.txt  # Dev dependencies (PyInstaller)
├── setup.py              # Package setup
├── pyproject.toml        # Modern package config
└── README.md             # Full documentation
```

## Quick Commands

### Development (in venv)
```powershell
.\venv\Scripts\Activate.ps1
kvg-rgb gui
kvg-rgb list
kvg-rgb color 255 0 0
```

### Build a release

Releases are built by CI (see [RELEASE.md](RELEASE.md)) — push to `main`
or trigger `cut-release.yml` from the Actions tab. No local build script.

### Reinstall Package
```powershell
.\venv\Scripts\Activate.ps1
pip install -e .
```

## CLI Examples

```powershell
# Desktop window (easiest!)
kvg-rgb gui

# Or a browser tab instead
kvg-rgb web

# List devices
kvg-rgb list

# View zones
kvg-rgb zones

# Resize a zone (device 1, zone 3, to 35 LEDs)
kvg-rgb resize 1 3 35

# Set colors
kvg-rgb color 255 0 0              # All devices red
kvg-rgb color 0 255 0 --device 0   # Device 0 green

# Effects
kvg-rgb rainbow                    # 60 sec rainbow
kvg-rgb rainbow --duration 30      # 30 sec rainbow
kvg-rgb breathe 0 150 255          # Cyan breathing
```

## Python API

```python
from kvg_rgb.core import RGBController

with RGBController() as controller:
    # List devices
    devices = controller.get_devices()
    
    # Set color
    controller.set_color(255, 0, 0)  # Red
    
    # Effects
    controller.rainbow_effect(duration=30)
    controller.breathing_effect(0, 150, 255, duration=30)
```

## Sharing Your Tool

Point people at the [latest release](https://github.com/gerp93/KVG_RGB/releases/latest) —
CI builds and publishes the executable for Windows/macOS/Linux on every
release. Recipients don't need Python or a build step.
