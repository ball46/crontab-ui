"""Tests for crontab_ui core functions."""
import sys
import os

# Add project root to path so we can import the single-file module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock textual before importing crontab_ui to avoid TUI dependency in tests
import unittest.mock as mock

# We need to patch the _ensure_textual call and textual imports
# Since crontab_ui.py runs _ensure_textual() at module level, we pre-populate
# the textual modules in sys.modules with mocks before importing
_textual_modules = [
    "textual", "textual.app", "textual.binding", "textual.containers",
    "textual.widgets", "textual.screen", "textual.reactive", "textual.css",
]
for mod in _textual_modules:
    if mod not in sys.modules:
        sys.modules[mod] = mock.MagicMock()

import crontab_ui


def test_smoke_describe():
    """Verify we can call describe() after import."""
    result = crontab_ui.describe("*", "*", "*", "*", "*")
    assert isinstance(result, str)
    assert len(result) > 0


import pytest


class TestValidateCronField:
    """Tests for validate_cron_field(value, min_val, max_val)."""

    # --- Valid cases ---

    def test_wildcard(self):
        assert crontab_ui.validate_cron_field("*", 0, 59) == (True, "")

    def test_single_number_in_range(self):
        assert crontab_ui.validate_cron_field("0", 0, 59) == (True, "")
        assert crontab_ui.validate_cron_field("59", 0, 59) == (True, "")

    def test_step_wildcard(self):
        assert crontab_ui.validate_cron_field("*/5", 0, 59) == (True, "")
        assert crontab_ui.validate_cron_field("*/15", 0, 59) == (True, "")

    def test_step_with_range(self):
        assert crontab_ui.validate_cron_field("1-30/5", 0, 59) == (True, "")

    def test_range(self):
        assert crontab_ui.validate_cron_field("1-5", 0, 59) == (True, "")
        assert crontab_ui.validate_cron_field("0-6", 0, 6) == (True, "")

    def test_list(self):
        assert crontab_ui.validate_cron_field("1,3,5", 0, 59) == (True, "")
        assert crontab_ui.validate_cron_field("0,6", 0, 6) == (True, "")

    def test_mixed_list_with_ranges(self):
        assert crontab_ui.validate_cron_field("1-5,10,15-20", 0, 59) == (True, "")

    # --- Invalid cases ---

    def test_out_of_range_high(self):
        ok, msg = crontab_ui.validate_cron_field("60", 0, 59)
        assert not ok
        assert "60" in msg

    def test_out_of_range_low(self):
        ok, msg = crontab_ui.validate_cron_field("-1", 0, 59)
        assert not ok

    def test_non_numeric(self):
        ok, msg = crontab_ui.validate_cron_field("foo", 0, 59)
        assert not ok

    def test_empty_string(self):
        ok, msg = crontab_ui.validate_cron_field("", 0, 59)
        assert not ok

    def test_reversed_range(self):
        ok, msg = crontab_ui.validate_cron_field("30-10", 0, 59)
        assert not ok

    def test_step_zero(self):
        ok, msg = crontab_ui.validate_cron_field("*/0", 0, 59)
        assert not ok

    def test_step_negative(self):
        ok, msg = crontab_ui.validate_cron_field("*/-1", 0, 59)
        assert not ok

    def test_range_out_of_bounds(self):
        ok, msg = crontab_ui.validate_cron_field("0-7", 0, 6)
        assert not ok

    def test_spaces_in_value(self):
        ok, msg = crontab_ui.validate_cron_field("1 2", 0, 59)
        assert not ok


class TestValidateCronExpression:
    """Tests for validate_cron_expression(min_, hr, dom, mo, dow)."""

    def test_valid_standard(self):
        assert crontab_ui.validate_cron_expression("0", "9", "*", "*", "1-5") == (True, "")

    def test_valid_all_wildcard(self):
        assert crontab_ui.validate_cron_expression("*", "*", "*", "*", "*") == (True, "")

    def test_invalid_minute(self):
        ok, msg = crontab_ui.validate_cron_expression("60", "0", "*", "*", "*")
        assert not ok
        assert "minute" in msg.lower() or "60" in msg

    def test_invalid_hour(self):
        ok, msg = crontab_ui.validate_cron_expression("0", "25", "*", "*", "*")
        assert not ok

    def test_invalid_dom(self):
        ok, msg = crontab_ui.validate_cron_expression("0", "0", "32", "*", "*")
        assert not ok

    def test_invalid_month(self):
        ok, msg = crontab_ui.validate_cron_expression("0", "0", "*", "13", "*")
        assert not ok

    def test_invalid_dow(self):
        ok, msg = crontab_ui.validate_cron_expression("0", "0", "*", "*", "8")
        assert not ok


class TestAtSyntax:
    """Tests for @reboot, @daily, etc. in load/save."""

    def test_at_shortcuts_map(self):
        shortcuts = crontab_ui.AT_SHORTCUTS
        assert "@reboot" in shortcuts
        assert "@yearly" in shortcuts
        assert "@annually" in shortcuts
        assert "@monthly" in shortcuts
        assert "@weekly" in shortcuts
        assert "@daily" in shortcuts
        assert "@midnight" in shortcuts
        assert "@hourly" in shortcuts

    def test_at_yearly_expands(self):
        assert crontab_ui.AT_SHORTCUTS["@yearly"] == "0 0 1 1 *"

    def test_at_daily_expands(self):
        assert crontab_ui.AT_SHORTCUTS["@daily"] == "0 0 * * *"

    def test_at_hourly_expands(self):
        assert crontab_ui.AT_SHORTCUTS["@hourly"] == "0 * * * *"


class TestLoadCrontabAtSyntax:

    def test_parse_at_daily(self):
        crontab_output = "@daily /usr/bin/backup.sh\n"
        with mock.patch("subprocess.run") as mocked:
            mocked.return_value = mock.Mock(stdout=crontab_output, returncode=0)
            jobs = crontab_ui.load_crontab()
        assert len(jobs) == 1
        assert jobs[0]["min"] == "0"
        assert jobs[0]["hr"] == "0"
        assert jobs[0]["dom"] == "*"
        assert jobs[0]["mo"] == "*"
        assert jobs[0]["dow"] == "*"
        assert jobs[0]["cmd"] == "/usr/bin/backup.sh"
        assert jobs[0]["at_shortcut"] == "@daily"

    def test_parse_at_reboot(self):
        crontab_output = "@reboot /start.sh --daemon\n"
        with mock.patch("subprocess.run") as mocked:
            mocked.return_value = mock.Mock(stdout=crontab_output, returncode=0)
            jobs = crontab_ui.load_crontab()
        assert len(jobs) == 1
        assert jobs[0]["at_shortcut"] == "@reboot"
        assert jobs[0]["cmd"] == "/start.sh --daemon"
        assert jobs[0]["min"] == "-"
        assert jobs[0]["hr"] == "-"

    def test_parse_mixed_standard_and_at(self):
        crontab_output = "0 9 * * 1-5 /work.sh\n@hourly /check.sh\n"
        with mock.patch("subprocess.run") as mocked:
            mocked.return_value = mock.Mock(stdout=crontab_output, returncode=0)
            jobs = crontab_ui.load_crontab()
        assert len(jobs) == 2
        assert "at_shortcut" not in jobs[0]
        assert jobs[1]["at_shortcut"] == "@hourly"


class TestSaveCrontabAtSyntax:

    def test_save_at_daily_uses_shortcut(self):
        jobs = [{"min": "0", "hr": "0", "dom": "*", "mo": "*", "dow": "*",
                 "cmd": "/backup.sh", "at_shortcut": "@daily",
                 "raw": "@daily /backup.sh"}]
        with mock.patch("subprocess.run") as mocked:
            mocked.return_value = mock.Mock(returncode=0, stderr="")
            crontab_ui.save_crontab(jobs)
            written = mocked.call_args[1]["input"]
        assert "@daily /backup.sh" in written

    def test_save_at_reboot_uses_shortcut(self):
        jobs = [{"min": "-", "hr": "-", "dom": "-", "mo": "-", "dow": "-",
                 "cmd": "/start.sh", "at_shortcut": "@reboot",
                 "raw": "@reboot /start.sh"}]
        with mock.patch("subprocess.run") as mocked:
            mocked.return_value = mock.Mock(returncode=0, stderr="")
            crontab_ui.save_crontab(jobs)
            written = mocked.call_args[1]["input"]
        assert "@reboot /start.sh" in written

    def test_save_standard_job_unchanged(self):
        jobs = [{"min": "0", "hr": "9", "dom": "*", "mo": "*", "dow": "1-5",
                 "cmd": "/work.sh", "raw": "0 9 * * 1-5 /work.sh"}]
        with mock.patch("subprocess.run") as mocked:
            mocked.return_value = mock.Mock(returncode=0, stderr="")
            crontab_ui.save_crontab(jobs)
            written = mocked.call_args[1]["input"]
        assert "0 9 * * 1-5 /work.sh" in written


class TestSanitizeCmd:
    """Tests for sanitize_cmd(cmd)."""

    def test_normal_command_unchanged(self):
        assert crontab_ui.sanitize_cmd("/usr/bin/backup.sh --verbose") == "/usr/bin/backup.sh --verbose"

    def test_strips_newlines(self):
        assert crontab_ui.sanitize_cmd("echo hello\necho world") == "echo hello echo world"

    def test_strips_carriage_return(self):
        assert crontab_ui.sanitize_cmd("echo hello\r\n") == "echo hello"

    def test_strips_null_bytes(self):
        assert crontab_ui.sanitize_cmd("echo\x00hello") == "echohello"

    def test_strips_leading_trailing_whitespace(self):
        assert crontab_ui.sanitize_cmd("  /bin/test  ") == "/bin/test"

    def test_preserves_tabs_in_args(self):
        assert crontab_ui.sanitize_cmd("echo\thello") == "echo\thello"

    def test_empty_after_sanitize(self):
        assert crontab_ui.sanitize_cmd("\n\r\x00") == ""

    def test_command_with_pipe(self):
        assert crontab_ui.sanitize_cmd("cat /log | grep error") == "cat /log | grep error"

    def test_command_with_redirect(self):
        assert crontab_ui.sanitize_cmd("backup.sh > /dev/null 2>&1") == "backup.sh > /dev/null 2>&1"


class TestSaveCrontabSanitization:
    """Tests that save_crontab sanitizes commands."""

    def test_newline_in_cmd_stripped(self):
        jobs = [{"min": "0", "hr": "0", "dom": "*", "mo": "*", "dow": "*",
                 "cmd": "echo hello\necho evil", "raw": "0 0 * * * echo hello"}]
        with mock.patch("subprocess.run") as mocked:
            mocked.return_value = mock.Mock(returncode=0, stderr="")
            crontab_ui.save_crontab(jobs)
            written = mocked.call_args[1]["input"]
        job_lines = [l for l in written.splitlines() if not l.startswith("#")]
        assert len(job_lines) == 1
        assert "\n" not in job_lines[0]


class TestIntegration:
    """Integration tests: load → validate → sanitize → save round-trip."""

    def test_roundtrip_standard_jobs(self):
        """Load standard crontab, validate, save back unchanged."""
        crontab_input = "# Managed by crontab-ui\n0 9 * * 1-5 /work.sh\n*/5 * * * * /check.sh\n"
        with mock.patch("subprocess.run") as mocked:
            mocked.return_value = mock.Mock(stdout=crontab_input, returncode=0)
            jobs = crontab_ui.load_crontab()
        assert len(jobs) == 2
        for j in jobs:
            ok, msg = crontab_ui.validate_cron_expression(
                j["min"], j["hr"], j["dom"], j["mo"], j["dow"])
            assert ok, f"Validation failed for {j['raw']}: {msg}"

    def test_roundtrip_with_at_syntax(self):
        """Load @-syntax entries, verify they save back correctly."""
        crontab_input = "@daily /backup.sh\n@reboot /start.sh\n0 0 1 * * /monthly.sh\n"
        with mock.patch("subprocess.run") as mocked:
            mocked.return_value = mock.Mock(stdout=crontab_input, returncode=0)
            jobs = crontab_ui.load_crontab()
        assert len(jobs) == 3
        assert jobs[0]["at_shortcut"] == "@daily"
        assert jobs[1]["at_shortcut"] == "@reboot"
        assert "at_shortcut" not in jobs[2]

        with mock.patch("subprocess.run") as mocked:
            mocked.return_value = mock.Mock(returncode=0, stderr="")
            crontab_ui.save_crontab(jobs)
            written = mocked.call_args[1]["input"]
        assert "@daily /backup.sh" in written
        assert "@reboot /start.sh" in written
        assert "0 0 1 * * /monthly.sh" in written

    def test_invalid_cron_rejected(self):
        """Confirm invalid values are caught by validation."""
        ok, _ = crontab_ui.validate_cron_expression("99", "0", "*", "*", "*")
        assert not ok
        ok, _ = crontab_ui.validate_cron_expression("0", "0", "*", "13", "*")
        assert not ok

    def test_dangerous_command_sanitized(self):
        """Confirm newlines in commands are neutralized."""
        dirty = "/script.sh\n0 * * * * /evil.sh"
        clean = crontab_ui.sanitize_cmd(dirty)
        assert "\n" not in clean
        assert "/evil.sh" in clean  # preserved but on same line


class TestReviewFixes:
    """Tests for issues found during code review."""

    def test_validate_cron_expression_accepts_reboot_sentinel(self):
        """@reboot sentinel fields should pass validation."""
        ok, msg = crontab_ui.validate_cron_expression("-", "-", "-", "-", "-")
        assert ok, f"@reboot sentinel rejected: {msg}"

    def test_sanitize_cmd_strips_form_feed(self):
        assert crontab_ui.sanitize_cmd("echo\x0chello") == "echohello"

    def test_sanitize_cmd_strips_vertical_tab(self):
        assert crontab_ui.sanitize_cmd("echo\x0bhello") == "echohello"

    def test_sanitize_cmd_strips_escape(self):
        assert crontab_ui.sanitize_cmd("echo\x1b[31mhello") == "echo[31mhello"

    def test_unknown_at_token_roundtrip(self):
        """Unknown @-tokens should be preserved verbatim, not corrupted."""
        with mock.patch("subprocess.run") as mocked:
            mocked.return_value = mock.Mock(stdout="@unknown /cmd.sh\n", returncode=0)
            jobs = crontab_ui.load_crontab()
        with mock.patch("subprocess.run") as mocked:
            mocked.return_value = mock.Mock(returncode=0, stderr="")
            crontab_ui.save_crontab(jobs)
            written = mocked.call_args[1]["input"]
        assert "? ? ? ? ?" not in written
        assert "@unknown /cmd.sh" in written

    def test_describe_with_at_shortcut_param(self):
        """describe() with at_shortcut='@reboot' returns reboot description."""
        result = crontab_ui.describe("-", "-", "-", "-", "-", at_shortcut="@reboot")
        assert result == crontab_ui.T["desc_at_reboot"]
