# Release Process Guide

Releases are built and published by CI via
[KVG_Standards](https://github.com/gerp93/KVG_Standards)' shared
`release-python-gui.yml` workflow — there's no local `release.py` script to
run anymore.

## How it works

- **`.github/workflows/auto-release.yml`** fires on every push to `main`. It
  bumps the version (Conventional Commits patch/minor/major), tags it, and
  calls `release-python-gui.yml` to build and publish.
- **`.github/workflows/cut-release.yml`** is a manual `workflow_dispatch`
  you trigger from the Actions tab when you want a specific version number
  instead of the auto-bump.

Both call the same reusable build: PyInstaller `--onefile --windowed` builds
`kvg_rgb/gui.py` for Windows/macOS/Linux and uploads the three binaries
straight to a GitHub Release — no wheel, no separate installer.

## Forcing a release with no code change

`auto-release.yml` bumps on every push regardless of what changed. If you
need a release without a real code change (e.g. to pick up an updated
KVG_Standards workflow), add a dated one-line entry to
[`VERSION_BUMP.md`](../VERSION_BUMP.md) instead of an empty commit — that
gives the push a real, reviewable diff.

## Versioning

`release-python-gui.yml`'s `version_file: kvg_rgb/__init__.py` input writes
`__version__ = "X.Y.Z"` into that file at build time from the tag — you
don't need to hand-edit `kvg_rgb/__init__.py` before a release.

## Testing a build locally

```powershell
.\venv\Scripts\Activate.ps1
pip install pyinstaller
pyinstaller --onefile --windowed --name KVG_RGB kvg_rgb/gui.py
.\dist\KVG_RGB.exe
```

This mirrors what CI runs, useful for catching packaging issues (missing
`--add-data`, hidden imports) before pushing.

## Release notes

`release-python-gui.yml` prepends an "## Installing" blurb to each
release's auto-generated changelog — see the workflow itself in
KVG_Standards for the exact wording.
