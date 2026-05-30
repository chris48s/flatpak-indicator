import sys
from unittest.mock import MagicMock, patch

import pytest

sys.modules["gi"] = MagicMock()
sys.modules["gi.repository"] = MagicMock()
sys.modules["gi.repository.Gtk"] = MagicMock()
sys.modules["gi.repository.GLib"] = MagicMock()
sys.modules["gi.repository.Notify"] = MagicMock()
sys.modules["gi.repository.AyatanaAppIndicator3"] = MagicMock()
sys.modules["gi.repository.AppIndicator3"] = MagicMock()

# Make GLib.idle_add execute its callback synchronously so App's
# _on_check_done / _on_update_done run inline during tests.
from gi.repository import GLib  # noqa: E402

GLib.idle_add.side_effect = lambda fn, *args: fn(*args)


class SynchronousThread:
    """Drop-in for threading.Thread that runs target() inline on .start()."""

    def __init__(self, target=None, args=(), kwargs=None, **_):
        self._target = target
        self._args = args
        self._kwargs = kwargs or {}

    def start(self):
        if self._target:
            self._target(*self._args, **self._kwargs)


@pytest.fixture(autouse=True)
def synchronous_threads():
    """Patch threading.Thread globally for every test."""
    with patch("threading.Thread", SynchronousThread):
        yield
