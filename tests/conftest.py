"""Shared fixtures for all test modules."""
import pytest


class MockStdscr:
    """Mock curses stdscr object."""

    def refresh(self):
        pass

    def addstr(self, *args):
        pass


class MockTerminal:
    """Mock terminal that satisfies all GameTerminal method calls.

    Drop-in replacement for terminal.game_terminal.GameTerminal in tests.
    Every method is a no-op so tests can run without a real curses session.
    """

    def __init__(self):
        self.stdscr = MockStdscr()

    def set_player_stats(self, *args):
        pass

    def draw_player_stats(self):
        pass

    def draw_game_title(self):
        pass

    def draw_separator(self):
        pass

    def draw_dialog(self, text):
        pass

    def refresh(self):
        pass

    def close_game_terminal(self):
        pass

    def clear_screen(self):
        pass

    def set_cow_stats(self, *args):
        pass

    def clear_area(self, *args):
        pass


class MockPlayer:
    """Lightweight mock player with configurable hp and cash."""

    def __init__(self, hp=20, cash=50):
        self.hp = hp
        self.cash = cash


@pytest.fixture
def mock_terminal():
    """Provide a fresh MockTerminal instance."""
    return MockTerminal()


@pytest.fixture
def mock_player():
    """Provide a MockPlayer factory.

    Usage:
        def test_something(mock_player):
            player = mock_player()          # defaults: hp=20, cash=50
            player = mock_player(hp=1, cash=0)  # custom values
    """
    def _factory(hp=20, cash=50):
        return MockPlayer(hp=hp, cash=cash)
    return _factory
