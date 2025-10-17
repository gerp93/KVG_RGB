# Installation Guide

## Prerequisites

- **Python 3.7 or higher** (Windows, macOS, or Linux)
- **OpenRGB** must be installed and running
  - Download from: https://openrgb.org/
  - Enable SDK Server in OpenRGB Settings

## Installation

### Fresh Installation

```bash
pip install kvg_rgb-X.X.X-py3-none-any.whl
```

### Upgrading from Previous Version

**Option 1: Automatic upgrade (Recommended)**
```bash
pip install --upgrade --force-reinstall kvg_rgb-X.X.X-py3-none-any.whl
```

**Option 2: Manual upgrade**
```bash
# Uninstall old version
pip uninstall kvg-rgb -y

# Install new version
pip install kvg_rgb-X.X.X-py3-none-any.whl
```

**✅ Your settings are automatically preserved!**
- All data stored in `~/.kvg_rgb/` (Linux/macOS) or `%USERPROFILE%\.kvg_rgb\` (Windows)
- Colors, LED configurations, and profiles persist across updates
- Database is never touched during uninstall/upgrade

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

## Uninstalling

```bash
# Remove the package
pip uninstall kvg-rgb

# Optionally remove your data (colors, settings, profiles)
# Linux/macOS:
rm -rf ~/.kvg_rgb

# Windows (PowerShell):
Remove-Item -Recurse -Force "$env:USERPROFILE\.kvg_rgb"

# Windows (Command Prompt):
rmdir /s /q "%USERPROFILE%\.kvg_rgb"
```

**Note:** Uninstalling the package does NOT delete your data by default. Your settings remain in `~/.kvg_rgb/` so you can reinstall later without losing anything.

## Troubleshooting

### "Python is not installed or not in PATH"
- Install Python from https://python.org
- **Windows**: Make sure to check "Add Python to PATH" during installation
- **Linux**: Use your package manager (`apt install python3` or `dnf install python3`)
- **macOS**: Use Homebrew (`brew install python3`)

### "Could not connect to OpenRGB"
1. Make sure OpenRGB is running
2. In OpenRGB → Settings → Enable "Start SDK Server"
3. Check the port is 6742 (default)

For more help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## What Gets Installed

- **Command**: `kvg-rgb` - Main CLI tool (cross-platform)
- **Web Interface**: Accessible at `http://localhost:5000`
- **Data Directory**: 
  - **Linux/macOS**: `~/.kvg_rgb/`
  - **Windows**: `%USERPROFILE%\.kvg_rgb\`
  - Contains:
    - `rgb_controller.db` - Your colors and settings
    - `config.json` - Configuration (auto-created)
- **Startup Script** (Windows only): `kvg_rgb\scripts\start_kvg_rgb.bat`

## Next Steps

- 📖 Read the [Quick Start Guide](QUICKSTART.md)
- 🚀 Set up [autostart](../README.md#-auto-start-on-windows-boot)
- 🎨 Start controlling your RGB!
