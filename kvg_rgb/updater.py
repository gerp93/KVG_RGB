"""
Thin wrapper around kvg-updater (pinned in requirements.txt, see
KVG_Standards' update-check-versioning.md).
"""
from kvg_updater import check_for_update
from kvg_rgb import __version__ as CURRENT_VERSION

GITHUB_REPO = "gerp93/KVG_RGB"
APP_NAME = "KVG_RGB"


def check():
    """Return {"version": str, "download_url": str} if a newer release is
    available, else None. Only ever returns non-None for a packaged build
    with a real version — always None when running from source."""
    return check_for_update(GITHUB_REPO, APP_NAME, CURRENT_VERSION)
