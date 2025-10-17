# KVG RGB Controller - Quick Reference

## Getting Started (For End Users)

### 1. **Easiest: Use the Web Interface**
```powershell
# In your terminal:
kvg-rgb web
```
✅ Browser opens automatically at http://localhost:5000  
✅ Use the visual color picker and effect controls  
✅ No command-line knowledge needed!

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
│   └── cli.py            # CLI interface
├── main.py               # Entry point
├── rgb_utils.py          # Legacy utilities
├── build_exe.py          # Executable builder
├── requirements.txt      # Dependencies
├── requirements-dev.txt  # Dev dependencies
├── setup.py              # Package setup
├── pyproject.toml        # Modern package config
└── README.md             # Full documentation
```

## Quick Commands

### Development (in venv)
```powershell
.\venv\Scripts\Activate.ps1
kvg-rgb list
kvg-rgb color 255 0 0
```

### Build Executable
```bash
python release.py
# Output: dist\kvg-rgb.exe (Windows) or dist/kvg-rgb (Linux/macOS)
```

### Reinstall Package
```powershell
.\venv\Scripts\Activate.ps1
pip install -e .
```

## CLI Examples

```powershell
# Web interface (easiest!)
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

1. Build executable: `python build_exe.py`
2. Share `dist\kvg-rgb.exe` 
3. Recipients don't need Python!

## Future GUI

The `RGBController` class in `kvg_rgb/core.py` is designed to be reusable.
To add a GUI later, create `kvg_rgb/gui.py` and import the controller.
