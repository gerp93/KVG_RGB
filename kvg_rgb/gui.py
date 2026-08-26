"""
Native desktop window for KVG RGB Controller.

Runs the existing Flask app (kvg_rgb.web) in a background thread and
displays it in a native OS window via pywebview, instead of opening a
browser tab. This is the entry point PyInstaller builds for the packaged
desktop app.
"""
import socket
import sys
import threading
from pathlib import Path

import webview

from kvg_rgb.web import create_app


def _free_port():
    """Ask the OS for an unused local port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def _app_root():
    """Repo root when running from source, or the PyInstaller extraction dir when frozen."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def _window_icon():
    """
    Path to the icon pywebview should use, or None.

    Windows needs an actual .ico (System.Drawing.Icon can't load a plain
    PNG); GTK/Cocoa can load the PNG directly, so only Windows gets the
    separate assets/icon.ico.
    """
    root = _app_root()
    candidate = root / 'assets' / 'icon.ico' if sys.platform == 'win32' else root / 'kvg_rgb' / 'static' / 'logo.png'
    return str(candidate) if candidate.exists() else None


def run_gui():
    """Start the Flask backend in a background thread and show it in a native window."""
    port = _free_port()
    app = create_app()
    print(f"KVG RGB Controller starting on http://127.0.0.1:{port}")

    server_thread = threading.Thread(
        target=lambda: app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False),
        daemon=True,
    )
    server_thread.start()

    webview.create_window(
        'KVG RGB Controller',
        f'http://127.0.0.1:{port}',
        width=1200,
        height=800,
        min_size=(900, 600),
    )
    webview.start(icon=_window_icon())


if __name__ == '__main__':
    run_gui()
