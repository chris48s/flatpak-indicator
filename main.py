import logging
import threading

import gi

# this has to happen before
# from gi.repository import Gtk
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from flatpak_indicator.flatpak_runner import check_updates, run_updates
from flatpak_indicator.notifications import (
    notify_update_complete,
    notify_update_failed,
    notify_updates_available,
)
from flatpak_indicator.tray import TrayIcon

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 120 * 60  # 120 minutes


class AppState:
    def __init__(self):
        self.update_count: int = 0
        self.checking: bool = False
        self.updating: bool = False
        self.last_error: str | None = None


class App:
    def __init__(self):
        self.state = AppState()
        self.tray = TrayIcon(
            on_check=self.start_check,
            on_update=self.start_update,
            on_quit=Gtk.main_quit,
        )

    # check

    def start_check(self):
        if self.state.checking or self.state.updating:
            return
        self.state.checking = True
        self.tray.refresh(self.state)
        log.info("Checking for Flatpak updates...")
        threading.Thread(target=self._check_worker, daemon=True).start()

    def _check_worker(self):
        result = check_updates()
        GLib.idle_add(self._on_check_done, result)

    def _on_check_done(self, result):
        prev = self.state.update_count
        self.state.checking = False

        if result.error:
            self.state.last_error = result.error
            self.state.update_count = 0
            log.error("Check failed: %s", result.error)
        else:
            self.state.last_error = None
            self.state.update_count = result.count
            log.info("Found %d update(s).", result.count)
            if prev == 0 and result.count > 0:
                notify_updates_available(result.count)

        self.tray.refresh(self.state)
        return False

    # update

    def start_update(self):
        if self.state.updating or self.state.checking:
            return
        self.state.updating = True
        self.tray.refresh(self.state)
        log.info("Running flatpak update...")
        threading.Thread(target=self._update_worker, daemon=True).start()

    def _update_worker(self):
        result = run_updates()
        GLib.idle_add(self._on_update_done, result)

    def _on_update_done(self, result):
        self.state.updating = False

        if result.error:
            self.state.last_error = result.error
            log.error("Update failed: %s", result.error)
            notify_update_failed()
        else:
            self.state.last_error = None
            log.info("Update completed successfully.")
            notify_update_complete()

        self.tray.refresh(self.state)
        self.start_check()
        return False

    # run

    def _on_interval(self):
        self.start_check()
        return True  # keep timer alive

    def run(self):
        GLib.idle_add(self.start_check)
        GLib.timeout_add_seconds(CHECK_INTERVAL_SECONDS, self._on_interval)
        Gtk.main()


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
