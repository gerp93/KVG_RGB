#!/usr/bin/env python3
"""
Re-vendor kvg_rgb/static/vendor/visual-assault-themes.css from a given
VisualAssault tag. This is the deliberate, reviewable equivalent of
bumping a pinned dependency version for a plain-CSS consumer with no
package manager (Flask serves this file as a static asset) — see
KVG_Standards' themes-versioning.md, "Go / static-asset consumers".

Usage:
    python scripts/update-visual-assault-css.py v0.3.0
"""
import sys
import urllib.request
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / 'kvg_rgb' / 'static' / 'vendor' / 'visual-assault-themes.css'
RAW_URL = 'https://raw.githubusercontent.com/gerp93/VisualAssault/{tag}/packages/css/themes.css'


def main():
    if len(sys.argv) != 2:
        print('Usage: python scripts/update-visual-assault-css.py <tag>  (e.g. v0.3.0)')
        sys.exit(1)

    tag = sys.argv[1]
    url = RAW_URL.format(tag=tag)
    print(f'Fetching {url} ...')
    with urllib.request.urlopen(url) as response:
        body = response.read().decode('utf-8')

    header = (
        f'/* Vendored from gerp93/VisualAssault packages/css/themes.css @ {tag}\n'
        f'   Source: https://github.com/gerp93/VisualAssault/blob/{tag}/packages/css/themes.css\n'
        f'   Do not hand-edit. Re-vendor with scripts/update-visual-assault-css.py <tag> */\n\n'
    )
    TARGET.write_text(header + body, encoding='utf-8')
    print(f'Wrote {TARGET} ({tag})')


if __name__ == '__main__':
    main()
