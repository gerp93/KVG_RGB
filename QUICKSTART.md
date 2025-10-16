# KVG RGB Controller - Quick Reference

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
```powershell
.\venv\Scripts\Activate.ps1
python build_exe.py
# Output: dist\kvg-rgb.exe
```

### Reinstall Package
```powershell
.\venv\Scripts\Activate.ps1
pip install -e .
```

## CLI Examples

```powershell
# List devices
kvg-rgb list

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
