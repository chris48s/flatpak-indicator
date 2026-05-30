import logging
import subprocess
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class CheckResult:
    count: int = 0
    error: str | None = None


@dataclass
class UpdateResult:
    error: str | None = None


def check_updates() -> CheckResult:
    """Run `flatpak remote-ls --updates` and return the number of available updates."""
    try:
        result = subprocess.run(
            ["flatpak", "remote-ls", "--updates"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            msg = (
                result.stderr.strip() or "flatpak remote-ls exited with non-zero status"
            )
            return CheckResult(error=msg)

        lines = [line for line in result.stdout.splitlines() if line.strip()]
        return CheckResult(count=len(lines))

    except FileNotFoundError:
        return CheckResult(error="flatpak executable not found")
    except Exception as exc:
        return CheckResult(error=str(exc))


def run_updates() -> UpdateResult:
    """Run `flatpak update -y` and return a result indicating success or failure."""
    try:
        result = subprocess.run(
            ["flatpak", "update", "-y"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            msg = result.stderr.strip() or "flatpak update exited with non-zero status"
            return UpdateResult(error=msg)

        return UpdateResult()

    except FileNotFoundError:
        return UpdateResult(error="flatpak executable not found")
    except Exception as exc:
        return UpdateResult(error=str(exc))
