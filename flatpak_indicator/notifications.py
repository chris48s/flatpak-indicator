import gi

# this has to happen before
# from gi.repository import Notify
gi.require_version("Notify", "0.7")
from gi.repository import Notify

_initialized = False


def _ensure_init() -> None:
    global _initialized
    if not _initialized:
        Notify.init("Flatpak Tray")
        _initialized = True


def _send(summary: str, body: str = "", icon: str = "dialog-information") -> None:
    _ensure_init()
    notification = Notify.Notification.new(summary, body, icon)
    notification.show()


def notify_updates_available(count: int) -> None:
    _send(
        f"{count} Flatpak update(s) available.",
        icon="software-update-available",
    )


def notify_update_complete() -> None:
    _send("Flatpak updates completed.", icon="emblem-default")


def notify_update_failed() -> None:
    _send("Flatpak update failed.", icon="dialog-error")
