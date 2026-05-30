from subprocess import CompletedProcess
from unittest.mock import patch

from flatpak_indicator.flatpak_runner import (
    CheckResult,
    UpdateResult,
    check_updates,
    run_updates,
)


def make_proc(returncode=0, stdout="", stderr=""):
    return CompletedProcess(
        args=[], returncode=returncode, stdout=stdout, stderr=stderr
    )


class TestCheckUpdates:
    def test_success_with_updates(self):
        output = "org.gnome.Platform\norg.freedesktop.Platform\n"
        with patch("subprocess.run", return_value=make_proc(stdout=output)):
            result = check_updates()
        assert result == CheckResult(count=2, error=None)

    def test_success_blank_lines_not_counted(self):
        output = "org.gnome.Platform\n\n   \norg.freedesktop.Platform\n"
        with patch("subprocess.run", return_value=make_proc(stdout=output)):
            result = check_updates()
        assert result == CheckResult(count=2, error=None)

    def test_success_no_updates(self):
        with patch("subprocess.run", return_value=make_proc(stdout="")):
            result = check_updates()
        assert result == CheckResult(count=0, error=None)

    def test_nonzero_returncode_uses_stderr(self):
        with patch(
            "subprocess.run", return_value=make_proc(returncode=1, stderr="some error")
        ):
            result = check_updates()
        assert result == CheckResult(count=0, error="some error")

    def test_nonzero_returncode_empty_stderr_fallback(self):
        with patch("subprocess.run", return_value=make_proc(returncode=1, stderr="")):
            result = check_updates()
        assert result == CheckResult(
            count=0, error="flatpak remote-ls exited with non-zero status"
        )

    def test_file_not_found(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = check_updates()
        assert result == CheckResult(count=0, error="flatpak executable not found")

    def test_generic_exception(self):
        with patch("subprocess.run", side_effect=RuntimeError("boom")):
            result = check_updates()
        assert result == CheckResult(count=0, error="boom")


class TestRunUpdates:
    def test_success(self):
        with patch("subprocess.run", return_value=make_proc(returncode=0)):
            result = run_updates()
        assert result == UpdateResult(error=None)

    def test_nonzero_returncode_uses_stderr(self):
        with patch(
            "subprocess.run",
            return_value=make_proc(returncode=1, stderr="update failed"),
        ):
            result = run_updates()
        assert result == UpdateResult(error="update failed")

    def test_nonzero_returncode_empty_stderr_fallback(self):
        with patch("subprocess.run", return_value=make_proc(returncode=1, stderr="")):
            result = run_updates()
        assert result == UpdateResult(
            error="flatpak update exited with non-zero status"
        )

    def test_file_not_found(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = run_updates()
        assert result == UpdateResult(error="flatpak executable not found")

    def test_generic_exception(self):
        with patch("subprocess.run", side_effect=RuntimeError("boom")):
            result = run_updates()
        assert result == UpdateResult(error="boom")
