# TODO

This app's own backlog of future features and fixes — not a KVG_Standards
compliance checklist (see [KVG_Standards](https://github.com/gerp93/KVG_Standards)
and its `REPO_SCOPE.md` entry for that). Just what's not built yet.

## Features

- Configuration profiles: save/load named device+zone+LED configurations, nestable, exportable/importable (HIGH priority — frequently requested)
- Favorite colors & gradients: save favorite colors/gradients beyond the recent-colors list, with names/tags
- Pre-made gradient library: built-in gradients (Rainbow, Fire, Ocean, Sunset, ...) with previews, click to apply
- LED pattern library (save/load custom LED patterns)
- Scheduling (time-based color changes)
- Integration with other apps (game events, music visualization, etc.)
- Native OS file picker for the Settings → Database Location "Set" action, instead of typing a path
- One-click restart after a database relocate or an applied update, instead of a manual restart
- Full-fidelity theming: the base palette (`--primary-color`, `--bg-card`, etc. in `style.css`) is sourced from the vendored VisualAssault theme, but the many translucent `rgba(...)` hover/glow/badge accents throughout `style.css` are still hand-tuned against the old indigo palette rather than derived from the active theme

## Fixes

- Zone flash and individual LED flash don't visibly work on keyboards (works fine on motherboards/other devices) — likely a keyboard firmware/driver limitation, low priority
- Device/zone settings are keyed by OpenRGB's device *index*. If OpenRGB enumerates devices in a different order (device unplugged, driver change), saved colors/names/brightness can attach to the wrong device. Keying on device name + serial instead would make this stable across re-enumeration.

---

## Completed

- Basic color control, device/zone selection and exclusion, SQLite persistence
- Zone resize, friendly names, per-zone brightness/saturation, per-zone effects (rainbow/breathing/wave/cycle/static)
- Individual LED control, gradients, device lock/toggle, recent colors
- Native desktop window (pywebview) replacing the browser-tab flow
- In-app Settings panel: VisualAssault theme picker, autostart toggle, desktop shortcut, database relocation, update check, About
- KVG_Standards compliance: AGPL-3.0 licensing reconciled, vendored VisualAssault theming, `kvg-updater`/`kvg-dblocation` wired in, CI release pipeline (`auto-release.yml`/`cut-release.yml` → `release-python-gui.yml`)
