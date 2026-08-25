# KVG RGB Controller

A desktop app for controlling RGB devices via [OpenRGB](https://openrgb.org/) — color picker, per-zone control, effects, and zone resizing, in a native window. A full CLI is also available if you run it from source.

This repo follows [KVG_Standards](https://github.com/gerp93/KVG_Standards) for theming, licensing, release/CI, update-check, and database-location conventions shared across gerp93's app repos.

## Quick Links

📦 [Installation Guide](docs/INSTALL.md) | 📖 [Quick Start Guide](docs/QUICKSTART.md) | 🚀 [Release Guide](docs/RELEASE.md) | 🔧 [Troubleshooting](docs/TROUBLESHOOTING.md) | 📝 [Changelog](docs/CHANGELOG.md)

## Features

- 🌐 **Desktop App** - Native window, no browser tab, no install step
- 🎨 **Color Picker & Presets** - Visual color selection with RGB sliders and quick presets
- 🎛️ **Per-Zone Control** - Individual zone/LED colors, gradients, brightness & saturation
- 🌈 **Effects** - Rainbow, breathing, wave, and cycle effects with speed control
- 📏 **Zone Management** - Resize addressable RGB zones on compatible devices
- ⚙️ **Settings** - VisualAssault theme picker, autostart, database location, self-update check
- 🖥️ **Full CLI** - Every action also available from the command line when running from source

## Installation

### For End Users (Recommended)

Download the build for your platform from the [latest release](https://github.com/gerp93/KVG_RGB/releases/latest) and run it directly — no installer, no Python required:

- **Windows** — `KVG_RGB-windows.exe`
- **macOS** — `KVG_RGB-macos` (make it executable first: `chmod +x KVG_RGB-macos`)
- **Linux** — `KVG_RGB-linux` (make it executable first: `chmod +x KVG_RGB-linux`)

These builds are unsigned, so Windows SmartScreen / macOS Gatekeeper will warn about an unrecognized publisher — click through to launch it. The app checks for updates itself (Settings → Updates inside the app).

**Your settings are preserved across updates!**
- All data is stored in `~/.kvg_rgb/` (or `%USERPROFILE%\.kvg_rgb\` on Windows), and relocatable via Settings → Database Location
- Colors, LED configurations, and profiles persist across updates

📦 **See the full [Installation Guide](docs/INSTALL.md)** for detailed instructions.

### For Developers (From Source)

Only needed if you want the CLI, want to modify the app, or want to build it yourself.

```powershell
cd C:\Users\kgerp\source\repos\KVG_RGB
.\venv\Scripts\Activate.ps1
pip install -e .
```

This installs the `kvg-rgb` command:

```powershell
kvg-rgb gui          # desktop window, same as the packaged app
kvg-rgb list          # CLI
```

## Prerequisites

- **OpenRGB** must be installed and running
- **SDK Server** must be enabled in OpenRGB:
  - Open OpenRGB
  - Go to Settings (gear icon)
  - Enable "Start SDK Server"
  - Default port is 6742

The app checks for OpenRGB itself at startup and shows a clear message in the window if it can't connect, instead of failing silently.

## Using the App

Launch it — double-click the executable, or `kvg-rgb gui` from source. Pick devices/zones on the right, colors and effects on the left. The ⚙️ **Settings** button (top right) covers:

- **Theme** — pick from 14 [VisualAssault](https://github.com/gerp93/VisualAssault) themes
- **Startup** — toggle launching KVG RGB when Windows starts
- **Desktop Shortcut** — create/remove one
- **Database Location** — relocate your data (e.g. into a synced folder)
- **Updates** — check for a newer release

### Auto-start on Windows Boot

**Easiest:** open Settings (⚙️) inside the app and toggle "Start KVG RGB Controller when Windows starts."

**From source, via the CLI:**

```powershell
kvg-rgb autostart            # interactive
kvg-rgb autostart --enable
kvg-rgb autostart --status
kvg-rgb autostart --disable
```

## Command-Line Interface (from source)

Installing from source (`pip install -e .`) also gives you the full CLI — useful for scripting, or controlling devices without opening the window:

```powershell
kvg-rgb --help                          # show all commands
kvg-rgb list                            # list all RGB devices
kvg-rgb zones                           # list devices with zone details
kvg-rgb resize 1 3 35                   # resize device 1, zone 3, to 35 LEDs
kvg-rgb color 255 0 0                   # set all devices to red
kvg-rgb color 0 255 0 --device 0        # set device 0 to green
kvg-rgb zone-color 1 3 255 0 0          # set device 1, zone 3 to red
kvg-rgb rainbow --duration 30           # 30s rainbow effect
kvg-rgb rainbow --duration 60 --speed 2 --device 1
kvg-rgb breathe 0 150 255               # breathing effect (cyan)
kvg-rgb web                             # browser tab instead of the desktop window
```

**Zone resizing** is useful when you've added or removed RGB strips from a motherboard's addressable headers. Not all zones can be resized — it depends on device capabilities. Example:

```
kvg-rgb zones
# [Device 1] ASUS PRIME Z890-P WIFI
#   Zones: 4
#     [Zone 0] Aura Mainboard - 1 LED
#     [Zone 1] Aura Addressable 1 - 30 LEDs
#     [Zone 2] Aura Addressable 2 - 30 LEDs
#     [Zone 3] Aura Addressable 3 - 35 LEDs

kvg-rgb resize 1 3 50   # resize device 1, zone 3 to 50 LEDs
```

### Using as a Python Module

```python
from kvg_rgb.core import RGBController

with RGBController() as controller:
    devices = controller.get_devices()
    controller.set_color(128, 0, 128)                    # purple, all devices
    controller.rainbow_effect(duration=10, speed=1.5)
```

See `kvg_rgb/core.py` for the full `RGBController` API.

## Building the Desktop App Locally

The distributed app is built and published automatically by CI on every release — see [RELEASE.md](docs/RELEASE.md). To build it locally instead (for testing packaging changes):

```powershell
.\venv\Scripts\Activate.ps1
pip install pyinstaller
pyinstaller --onefile --windowed --name KVG_RGB ^
  --add-data "kvg_rgb/templates;kvg_rgb/templates" ^
  --add-data "kvg_rgb/static;kvg_rgb/static" ^
  --add-data "kvg_rgb/scripts;kvg_rgb/scripts" ^
  kvg_rgb/gui.py
```

The `--add-data` flags matter — PyInstaller doesn't auto-detect Flask's `templates/`/`static/` folders, and omitting them produces a build that opens a blank window with a Flask "Internal Server Error" instead of the app.

## Project Structure

- `kvg_rgb/` - Main package
  - `core.py` - RGB controller class (used by CLI and GUI)
  - `web.py` - Flask backend + HTTP API
  - `gui.py` - Desktop window entry point (pywebview) — what CI packages
  - `cli.py` - Command-line interface
  - `database.py` / `paths.py` - SQLite persistence, relocatable via `kvg-dblocation`
  - `updater.py` - Self-update check via `kvg-updater`
  - `static/vendor/` - Vendored [VisualAssault](https://github.com/gerp93/VisualAssault) theme CSS
- `requirements.txt` / `requirements-dev.txt` - Runtime / build dependencies
- `.github/workflows/` - CI: `auto-release.yml` / `cut-release.yml` → KVG_Standards' `release-python-gui.yml`

## Troubleshooting

If you get a connection error:
1. Make sure OpenRGB is running
2. Check that SDK Server is enabled in OpenRGB settings
3. Verify the port (default: 6742)

For more, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Documentation

- 📖 [Quick Start Guide](docs/QUICKSTART.md) - Get up and running quickly
- 🚀 [Release Guide](docs/RELEASE.md) - How releases are built and published
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
