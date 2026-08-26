#!/usr/bin/env python3
"""
Generate all icon assets from assets/logo.png (the one source mark) —
per KVG_Standards' logo & branding checklist: never hand-export icon
sizes separately, always regenerate from the single padded source.

Usage:
    python scripts/generate-icons.py

Outputs:
    assets/icon.ico   - Windows, multi-resolution (16-256px)
    assets/icon.icns  - macOS
    kvg_rgb/static/logo.png - optimized copy for in-app UI use
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'assets' / 'logo.png'

ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]
ICNS_SIZES = [16, 32, 64, 128, 256, 512, 1024]
IN_APP_SIZE = 512


def load_padded_square(path):
    """Load the source mark and pad to square if it isn't already."""
    img = Image.open(path).convert('RGBA')
    if img.width == img.height:
        return img
    side = max(img.size)
    canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - img.width) // 2, (side - img.height) // 2), img)
    return canvas


def main():
    if not SOURCE.exists():
        raise SystemExit(f'Source mark not found: {SOURCE}')

    master = load_padded_square(SOURCE)
    print(f'Loaded {SOURCE} ({master.size[0]}x{master.size[1]})')

    # Windows .ico - Pillow packs every requested size into one file
    ico_path = ROOT / 'assets' / 'icon.ico'
    master.save(ico_path, format='ICO', sizes=[(s, s) for s in ICO_SIZES])
    print(f'Wrote {ico_path} ({len(ICO_SIZES)} sizes)')

    # macOS .icns
    icns_path = ROOT / 'assets' / 'icon.icns'
    resized = master.resize((1024, 1024), Image.LANCZOS) if master.size[0] < 1024 else master
    resized.save(icns_path, format='ICNS')
    print(f'Wrote {icns_path}')

    # In-app UI copy (served as a static asset by Flask)
    static_dir = ROOT / 'kvg_rgb' / 'static'
    static_dir.mkdir(parents=True, exist_ok=True)
    app_logo_path = static_dir / 'logo.png'
    master.resize((IN_APP_SIZE, IN_APP_SIZE), Image.LANCZOS).save(app_logo_path)
    print(f'Wrote {app_logo_path} ({IN_APP_SIZE}x{IN_APP_SIZE})')


if __name__ == '__main__':
    main()
