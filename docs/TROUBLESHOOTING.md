# Troubleshooting

## "Could not connect to OpenRGB" / status bar shows a connection error

1. Make sure OpenRGB is running.
2. In OpenRGB → Settings, enable **"Start SDK Server"**.
3. Check the port — KVG RGB expects the default, `6742`.
4. Restart KVG RGB after starting OpenRGB.

## The app window doesn't appear

- On Windows, the native window is rendered via WebView2 (bundled with
  Windows 10/11 and most Edge installs). If it's missing, install the
  [Evergreen WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/).
- Check whether the process is already running — look for `KVG_RGB.exe` (or
  `python -m kvg_rgb.gui` if running from source) in Task Manager; only one
  instance is needed.

## Devices don't show up, or colors don't apply

- Confirm the device shows up in OpenRGB itself first — if OpenRGB can't
  see it, KVG RGB can't either.
- Some devices need to be in "Direct" mode for per-LED control; KVG RGB
  attempts to set this automatically, but a device that doesn't expose a
  Direct mode won't support it.

## Update check fails or reports the wrong version

- Update-check only works in a packaged (frozen) build — running from
  source via `kvg-rgb gui`/`python -m kvg_rgb.gui` always reports the dev
  version and skips the check.
- It reads from GitHub Releases directly; a corporate proxy or firewall
  blocking `api.github.com` will make it fail silently.

## Something else

Open an issue at [gerp93/KVG_RGB](https://github.com/gerp93/KVG_RGB/issues)
with what you were doing and the console output if you have it (run
`kvg-rgb web` instead of `kvg-rgb gui` to see live console logs alongside
the UI).
