# Installation Guide

## Prerequisites

- **OpenRGB** must be installed and running
  - Download from: https://openrgb.org/
  - Enable SDK Server in OpenRGB Settings

## Installation (End Users)

Download the build for your platform from the
[latest release](https://github.com/gerp93/KVG_RGB/releases/latest) and run
it directly — no installer, no Python required:

- **Windows** — `KVG_RGB-windows.exe`
- **macOS** — `KVG_RGB-macos` (make it executable first: `chmod +x KVG_RGB-macos`)
- **Linux** — `KVG_RGB-linux` (make it executable first: `chmod +x KVG_RGB-linux`)

These builds are unsigned (no code-signing certificate configured), so
Windows SmartScreen and macOS Gatekeeper will warn about an unrecognized
publisher — click through ("More info" → "Run anyway" on Windows,
right-click → "Open" on macOS) to launch it.

**✅ Your settings are automatically preserved across updates!**
- All data stored in `~/.kvg_rgb/` (Linux/macOS) or `%USERPROFILE%\.kvg_rgb\` (Windows)
- Colors, LED configurations, and profiles persist across updates
- Relocatable from inside the app: Settings → Database Location

## From Source (Developers)

```powershell
cd C:\Users\kgerp\source\repos\KVG_RGB
.\venv\Scripts\Activate.ps1
pip install -e .
kvg-rgb gui
```

See the main [README](../README.md#for-developers-from-source) for details.

## First Time Setup

1. **Start OpenRGB** and enable SDK Server
2. **Run the app** — double-click the downloaded executable, or `kvg-rgb gui` from source
3. **Configure autostart** (optional) — Settings → Startup inside the app, or `kvg-rgb autostart` from the CLI

## Uninstalling

Just delete the executable — there's nothing else installed.

To also remove your data (colors, settings, profiles):

```powershell
# Windows (PowerShell)
Remove-Item -Recurse -Force "$env:USERPROFILE\.kvg_rgb"
```

```bash
# Linux/macOS
rm -rf ~/.kvg_rgb
```

## Troubleshooting

### "Could not connect to OpenRGB"
1. Make sure OpenRGB is running
2. In OpenRGB → Settings → Enable "Start SDK Server"
3. Check the port is 6742 (default)

For more help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## What's Where

- **Data Directory**:
  - **Linux/macOS**: `~/.kvg_rgb/`
  - **Windows**: `%USERPROFILE%\.kvg_rgb\`
  - Contains:
    - `rgb_controller.db` - Your colors and settings
    - `config.json` - Configuration (auto-created)
- **Startup Script** (Windows only): `kvg_rgb\scripts\start_kvg_rgb.bat`

## Next Steps

- 📖 Read the [Quick Start Guide](QUICKSTART.md)
- 🚀 Set up autostart from Settings inside the app, or `kvg-rgb autostart`
- 🎨 Start controlling your RGB!
