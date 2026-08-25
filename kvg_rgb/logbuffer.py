"""
In-memory log buffer so the app can show its own logs in the UI.

The packaged app is built with PyInstaller --windowed, which means there is
no console and sys.stdout goes nowhere — so without this, everything the
app logs about what it's doing to the hardware is invisible to the user.
"""
import logging
import threading
import time
from collections import deque

DEFAULT_CAPACITY = 1000


class RingBufferHandler(logging.Handler):
    """Keeps the most recent log records in memory for the /api/logs endpoint."""

    def __init__(self, capacity=DEFAULT_CAPACITY):
        super().__init__()
        self._records = deque(maxlen=capacity)
        self._lock = threading.Lock()
        self._seq = 0

    def emit(self, record):
        try:
            message = self.format(record)
        except Exception:
            try:
                message = record.getMessage()
            except Exception:
                return

        with self._lock:
            self._seq += 1
            self._records.append({
                'seq': self._seq,
                'time': time.strftime('%H:%M:%S', time.localtime(record.created)),
                'level': record.levelname,
                'logger': record.name,
                'message': message,
            })

    def entries_since(self, since=0):
        """Return (entries newer than `since`, latest seq)."""
        with self._lock:
            entries = [r for r in self._records if r['seq'] > since]
            return entries, self._seq

    def clear(self):
        with self._lock:
            self._records.clear()


_handler = None
_install_lock = threading.Lock()


def get_handler():
    """The process-wide buffer handler, installing it on first use."""
    global _handler
    with _install_lock:
        if _handler is None:
            handler = RingBufferHandler()
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(logging.Formatter('%(message)s'))

            # Attach to the package logger so every kvg_rgb.* module is captured.
            package_logger = logging.getLogger('kvg_rgb')
            package_logger.setLevel(logging.DEBUG)
            package_logger.addHandler(handler)

            _handler = handler
        return _handler
