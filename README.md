# Flatpak Update Tray

A lightweight Linux system tray application that monitors Flatpak package updates and lets you apply them with one click.

## Requirements

- Python 3.10+
- PyGObject (`python3-gi`)
- Ayatana AppIndicator (`gir1.2-ayatanaappindicator3-0.1`) — or the older `gir1.2-appindicator3-0.1`
- libnotify (`gir1.2-notify-0.7`)
- Flatpak

### Ubuntu / Debian

```bash
sudo apt install python3-gi gir1.2-ayatanaappindicator3-0.1 gir1.2-notify-0.7 flatpak
```

## Usage

```bash
python3 main.py
```

## Autostart on login

Copy the included desktop file to your XDG autostart directory and set the correct path:

```bash
cp flatpak-tray.desktop ~/.config/autostart/flatpak-tray.desktop
nano ~/.config/autostart/flatpak-tray.desktop
```

Update the `Exec` line to the absolute path of `main.py` on your system, for example:

```ini
Exec=python3 /home/yourname/flatpak-indicator/main.py
```

The file is picked up automatically on next login by any XDG-compliant desktop environment (GNOME, KDE, XFCE, etc.).

## Project structure

```
.
├── main.py                # Entry point, app state, threading
├── tray.py                # AppIndicator tray icon and menu
├── flatpak_runner.py      # Flatpak subprocess calls
├── notifications.py       # Desktop notifications via libnotify
├── flatpak-tray.desktop   # XDG autostart template
└── icons/
    ├── up-to-date.svg
    ├── updates-available.svg
    ├── checking.svg
    ├── updating.svg
    └── error.svg
```

## Tray states

| Icon | Meaning |
|------|---------|
| Green ✓ | Up to date |
| Orange ! | Updates available |
| Grey ··· | Checking for updates |
| Blue ↓ | Applying updates |
| Red ✗ | Last check failed |
