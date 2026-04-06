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
