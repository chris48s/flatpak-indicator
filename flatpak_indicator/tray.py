import os

import gi

try:
    gi.require_version("AyatanaAppIndicator3", "0.1")
    from gi.repository import AyatanaAppIndicator3 as AppIndicator3
except (ValueError, ImportError):
    gi.require_version("AppIndicator3", "0.1")
    from gi.repository import AppIndicator3

# this has to happen before
# from gi.repository import Gtk
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

ICONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")

# Map state keys to icon file names (without extension)
_ICON_NAMES = {
    "checking": "fpi-e673-checking",
    "updating": "fpi-e673-updating",
    "error": "fpi-e673-error",
    "updates-available": "fpi-e673-updates-available",
    "up-to-date": "fpi-e673-up-to-date",
}


class TrayIcon:
    def __init__(self, on_check, on_update, on_quit):
        self._on_check = on_check
        self._on_update = on_update

        self._indicator = AppIndicator3.Indicator.new(
            "flatpak-indicator",
            _ICON_NAMES["checking"],
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        self._indicator.set_icon_theme_path(ICONS_DIR)
        self._indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self._indicator.set_title("Checking for updates...")

        self._menu = Gtk.Menu()

        self._item_check = Gtk.MenuItem(label="Check for Updates")
        self._item_check.connect("activate", lambda _: self._on_check())
        self._menu.append(self._item_check)

        self._item_update = Gtk.MenuItem(label="Update Flatpaks")
        self._item_update.connect("activate", lambda _: self._on_update())
        self._menu.append(self._item_update)

        self._menu.append(Gtk.SeparatorMenuItem())

        item_quit = Gtk.MenuItem(label="Quit")
        item_quit.connect("activate", lambda _: on_quit())
        self._menu.append(item_quit)

        self._menu.show_all()
        self._indicator.set_menu(self._menu)

    def refresh(self, state):
        """Update icon, tooltip, and menu sensitivity from the current AppState."""
        if state.checking:
            icon_key = "checking"
            tooltip = "Checking for updates..."
        elif state.updating:
            icon_key = "updating"
            tooltip = "Updating Flatpaks..."
        elif state.last_error:
            icon_key = "error"
            tooltip = "Flatpak: check failed"
        elif state.update_count > 0:
            icon_key = "updates-available"
            tooltip = f"Flatpak: {state.update_count} update(s) available"
        else:
            icon_key = "up-to-date"
            tooltip = "Flatpaks Up to date"

        self._indicator.set_icon_full(_ICON_NAMES[icon_key], tooltip)
        self._indicator.set_title(tooltip)

        # Menu sensitivity:
        # - "Check for Updates" disabled while a check is already running
        # - "Update Flatpaks" disabled when no updates available or while updating
        self._item_check.set_sensitive(not state.checking)
        self._item_update.set_sensitive(not state.updating and state.update_count > 0)
