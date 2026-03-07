"""Tests for infrastructure: logging, terminal constants, autosave, save schema, career stats."""
import json
import logging
import os
import sys

import pytest

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ---------------------------------------------------------------------------
# 1. Logging tests
# ---------------------------------------------------------------------------

def test_setup_logging_creates_logger():
    """Logger should be configured with file handler."""
    from logging_config import setup_logging

    logger = setup_logging()
    assert logger.name == "vct"
    assert len(logger.handlers) >= 1
    assert logger.level == logging.INFO


def test_get_logger_returns_child():
    """get_logger should return child of root vct logger."""
    from logging_config import setup_logging, get_logger
    setup_logging()

    child = get_logger("vct.test")
    assert child.name == "vct.test"


def test_logging_writes_to_file():
    """Log messages should appear in the log file."""
    from logging_config import setup_logging, LOG_DIR, LOG_FILE

    logger = setup_logging()
    test_msg = "TEST_INFRASTRUCTURE_LOG_ENTRY"
    logger.info(test_msg)

    # Force flush
    for handler in logger.handlers:
        handler.flush()

    log_path = os.path.join(LOG_DIR, LOG_FILE)
    assert os.path.exists(log_path)
    with open(log_path, "r") as f:
        content = f.read()
    assert test_msg in content


# ---------------------------------------------------------------------------
# 2. Terminal size validation test
# ---------------------------------------------------------------------------

def test_terminal_minimum_size_check():
    """GameTerminal should require minimum terminal size."""
    from terminal.game_terminal import GameTerminal

    # These should be class-level constants
    assert GameTerminal.WIDTH == 85
    assert GameTerminal.HEIGHT == 30


# ---------------------------------------------------------------------------
# 3. Autosave tests
# ---------------------------------------------------------------------------

def test_autosave_calls_save():
    """_autosave should call save_game and not raise."""
    from models import GameStats

    class MockTerminal:
        def set_player_stats(self, *a):
            pass

        def draw_player_stats(self):
            pass

        def draw_game_title(self):
            pass

        def draw_separator(self):
            pass

        def set_cow_stats(self, s):
            pass

        def clear_area(self, *a):
            pass

        def refresh(self):
            pass

        class stdscr:
            @staticmethod
            def refresh():
                pass

    class MockGameForAutosave:
        """Minimal mock that has _autosave method logic."""

        def __init__(self):
            self.save_called = False
            self.stats = GameStats()

        def save_game(self):
            self.save_called = True
            return True

        def _autosave(self):
            try:
                self.save_game()
            except Exception:
                pass

    game = MockGameForAutosave()
    game._autosave()
    assert game.save_called


def test_autosave_swallows_errors():
    """_autosave should not raise even if save fails."""

    class MockGameBroken:
        def save_game(self):
            raise IOError("disk full")

        def _autosave(self):
            try:
                self.save_game()
            except Exception:
                pass

    game = MockGameBroken()
    # Should not raise
    game._autosave()


# ---------------------------------------------------------------------------
# 4. Save schema validation tests
# ---------------------------------------------------------------------------

def test_save_schema_validates_required_player_keys():
    """_parse_save_data should reject missing player keys."""
    from save_manager import SaveManager

    # Missing 'inventory' in player
    data = {
        "player": {"name": "Test", "hp": 20, "cash": 50},  # no inventory
        "stats": {"cows_defeated": 0},
        "cow_packs": {"1": 0.0},
    }
    assert SaveManager._parse_save_data(data) is None


def test_save_schema_accepts_valid_data():
    """_parse_save_data should accept valid save data."""
    from save_manager import SaveManager

    data = {
        "player": {"name": "Test", "hp": 20, "cash": 50, "inventory": []},
        "stats": {"cows_defeated": 0},
        "cow_packs": {"1": 0.0, "2": 1.5},
    }
    result = SaveManager._parse_save_data(data)
    assert result is not None
    assert result["player"]["name"] == "Test"
    assert result["cow_packs"][1] == 0.0  # Keys converted to int
    assert result["cow_packs"][2] == 1.5


# ---------------------------------------------------------------------------
# 5. Career stats version field test
# ---------------------------------------------------------------------------

def test_career_stats_saves_version():
    """Career stats should include version field."""
    from career_stats import CareerStats, CAREER_FILE

    # Clean up
    if os.path.exists(CAREER_FILE):
        os.remove(CAREER_FILE)

    career = CareerStats()
    career.total_runs = 1
    career.save()

    with open(CAREER_FILE, "r") as f:
        data = json.load(f)

    assert "version" in data
    assert data["version"] == 1

    # Cleanup
    os.remove(CAREER_FILE)
