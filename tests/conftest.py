"""Shared test utilities — importable mock classes for headless testing."""


class MockStdscr:
    """Mock curses stdscr object."""

    def refresh(self):
        pass

    def addstr(self, *args):
        pass

    def getch(self):
        return ord('\n')


class MockTerminal:
    """Mock terminal that satisfies all GameTerminal method calls.

    Drop-in replacement for terminal.game_terminal.GameTerminal in tests.
    Every method is a no-op so tests can run without a real curses session.
    """

    MENU_Y_START = 20
    MENU_Y_END = 26
    PROMPT_INPUT_Y = 27

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

    def save_dialog_state(self):
        return None

    def restore_dialog_state(self, state):
        pass

    def get_menu_choice(self, menu_items, prompt=None):
        return 1
