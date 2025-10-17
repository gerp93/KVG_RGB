# Installation Guide

## Prerequisites

- **Windows 10/11**
- **Python 3.7 or higher** installed and in PATH
- **OpenRGB** must be installed and running
  - Download from: https://openrgb.org/
  - Enable SDK Server in OpenRGB Settings

## Installation Methods

### Method 1: Using Install Script (Recommended)

1. **Download the package**:
   - Get `kvg_rgb-X.X.X-py3-none-any.whl` from the latest release
   - Get `install.bat` (included with the wheel)

2. **Run the installer**:
   ```cmd
   install.bat
   ```
   
   The script will:
   - ✅ Check for Python
   - ✅ Auto-uninstall old versions if present
   - ✅ Install the new version
   - ✅ Preserve all your settings
   - ✅ Offer to start the web interface

### Method 2: Manual Installation

```powershell
# If upgrading, uninstall old version first
pip uninstall kvg-rgb -y

# Install new version
pip install kvg_rgb-X.X.X-py3-none-any.whl

# Start the web interface
kvg-rgb web
```

## First Time Setup

After installation:

1. **Start OpenRGB** and enable SDK Server
2. **Run the web interface**:
   ```cmd
   kvg-rgb web
   ```
3. **Configure autostart** (optional):
   ```cmd
   kvg-rgb autostart
   ```

## Upgrading

### Using Install Script
Simply run `install.bat` with the new wheel file. Your settings are automatically preserved.

### Manual Upgrade
```powershell
pip uninstall kvg-rgb -y
pip install kvg_rgb-NEW_VERSION-py3-none-any.whl
```

**Your data is safe!** All settings are stored in `%USERPROFILE%\.kvg_rgb\` and persist across:
- Package updates
- Uninstalls/reinstalls  
- Python version changes

## Uninstalling

### Using Uninstall Script
```cmd
uninstall.bat
```

The script will:
- Remove the package
- Optionally delete your saved data
- Clean up autostart shortcuts

### Manual Uninstall
```powershell
# Remove package
pip uninstall kvg-rgb -y

# Optionally remove data
rmdir /s /q "%USERPROFILE%\.kvg_rgb"
```

## Troubleshooting

### "Python is not installed or not in PATH"
- Install Python from https://python.org
- Make sure to check "Add Python to PATH" during installation

### "No wheel file found"
- Make sure the `.whl` file is in the same folder as `install.bat`
- Download it from the latest GitHub release

### "Could not connect to OpenRGB"
1. Make sure OpenRGB is running
2. In OpenRGB → Settings → Enable "Start SDK Server"
3. Check the port is 6742 (default)

For more help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## What Gets Installed

- **Command**: `kvg-rgb` - Main CLI tool
- **Web Interface**: Accessible at `http://localhost:5000`
- **Data Directory**: `%USERPROFILE%\.kvg_rgb\`
  - `rgb_controller.db` - Your colors and settings
  - `config.json` - Configuration
- **Startup Script**: `kvg_rgb\scripts\start_kvg_rgb.bat`

## Next Steps

- 📖 Read the [Quick Start Guide](QUICKSTART.md)
- 🚀 Set up [autostart](../README.md#-auto-start-on-windows-boot)
- 🎨 Start controlling your RGB!
