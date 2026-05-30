from unittest.mock import patch

import pytest

from flatpak_indicator.flatpak_runner import CheckResult, UpdateResult
from main import App

# Patch targets are resolved in the main module's namespace.
PATCH_CHECK = "main.check_updates"
PATCH_RUN = "main.run_updates"
PATCH_NOTIFY_AVAILABLE = "main.notify_updates_available"
PATCH_NOTIFY_COMPLETE = "main.notify_update_complete"
PATCH_NOTIFY_FAILED = "main.notify_update_failed"
PATCH_TRAY = "main.TrayIcon"


@pytest.fixture()
def app():
    """Return an App instance with TrayIcon mocked out."""
    with patch(PATCH_TRAY):
        instance = App()
    # Reset the tray mock so call counts start clean for each test.
    instance.tray.reset_mock()
    return instance


class TestAppCheckCycle:
    def test_no_updates_no_notification(self, app):
        with patch(PATCH_CHECK, return_value=CheckResult(count=0)):
            with patch(PATCH_NOTIFY_AVAILABLE) as mock_notify:
                app.start_check()

        assert app.state.update_count == 0
        assert app.state.checking is False
        mock_notify.assert_not_called()
        app.tray.refresh.assert_called()

    def test_updates_found_first_time_notifies(self, app):
        with patch(PATCH_CHECK, return_value=CheckResult(count=3)):
            with patch(PATCH_NOTIFY_AVAILABLE) as mock_notify:
                app.start_check()

        assert app.state.update_count == 3
        mock_notify.assert_called_once_with(3)

    def test_updates_found_already_known_no_second_notification(self, app):
        app.state.update_count = 2  # already knew about updates
        with patch(PATCH_CHECK, return_value=CheckResult(count=3)):
            with patch(PATCH_NOTIFY_AVAILABLE) as mock_notify:
                app.start_check()

        mock_notify.assert_not_called()

    def test_check_error_sets_last_error(self, app):
        with patch(PATCH_CHECK, return_value=CheckResult(error="oops")):
            with patch(PATCH_NOTIFY_AVAILABLE) as mock_notify:
                app.start_check()

        assert app.state.last_error == "oops"
        assert app.state.update_count == 0
        mock_notify.assert_not_called()

    def test_check_clears_previous_error_on_success(self, app):
        app.state.last_error = "previous error"
        with patch(PATCH_CHECK, return_value=CheckResult(count=0)):
            app.start_check()

        assert app.state.last_error is None


class TestAppConcurrencyGuards:
    def test_start_check_while_checking_is_noop(self, app):
        app.state.checking = True
        with patch(PATCH_CHECK) as mock_check:
            app.start_check()
        mock_check.assert_not_called()

    def test_start_check_while_updating_is_noop(self, app):
        app.state.updating = True
        with patch(PATCH_CHECK) as mock_check:
            app.start_check()
        mock_check.assert_not_called()

    def test_start_update_while_updating_is_noop(self, app):
        app.state.updating = True
        with patch(PATCH_RUN) as mock_run:
            app.start_update()
        mock_run.assert_not_called()

    def test_start_update_while_checking_is_noop(self, app):
        app.state.checking = True
        with patch(PATCH_RUN) as mock_run:
            app.start_update()
        mock_run.assert_not_called()


class TestAppUpdateCycle:
    def test_update_success_notifies_complete(self, app):
        with patch(PATCH_RUN, return_value=UpdateResult()):
            with patch(PATCH_CHECK, return_value=CheckResult(count=0)):
                with patch(PATCH_NOTIFY_COMPLETE) as mock_notify:
                    app.start_update()

        mock_notify.assert_called_once()
        assert app.state.updating is False

    def test_update_error_notifies_failed(self, app):
        with patch(PATCH_RUN, return_value=UpdateResult(error="fail")):
            with patch(PATCH_CHECK, return_value=CheckResult(count=0)):
                with patch(PATCH_NOTIFY_FAILED) as mock_notify:
                    app.start_update()

        mock_notify.assert_called_once()

    def test_update_error_clears_on_next_success(self, app):
        app.state.last_error = "old error"
        with patch(PATCH_RUN, return_value=UpdateResult()):
            with patch(PATCH_CHECK, return_value=CheckResult(count=0)):
                app.start_update()

        assert app.state.last_error is None

    def test_update_triggers_recheck(self, app):
        with patch(PATCH_RUN, return_value=UpdateResult()):
            with patch(PATCH_CHECK, return_value=CheckResult(count=0)) as mock_check:
                app.start_update()

        # check_updates is called once by the re-check triggered in _on_update_done
        mock_check.assert_called_once()
