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
