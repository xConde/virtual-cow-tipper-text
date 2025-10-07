"""
Main menu system for Virtual Cow Tipper.
"""
import curses
import sys


TITLE_ART_LARGE = r"""
 _   _ _      _               _    _____                _____ _
| | | (_)    | |             | |  /  __ \              |_   _(_)
| | | |_ _ __| |_ _   _  __ _| |  | /  \/ _____      __ | |  _ _ __  _ __   ___ _ __
| | | | | '__| __| | | |/ _` | |  | |    / _ \ \ /\ / / | | | | '_ \| '_ \ / _ \ '__|
\ \_/ / | |  | |_| |_| | (_| | |  | \__/\ (_) \ V  V /  | | | | |_) | |_) |  __/ |
 \___/|_|_|   \__|\__,_|\__,_|_|   \____/\___/ \_/\_/   \_/ |_| .__/| .__/ \___|_|
                                                                | |   | |
                                                                |_|   |_|
"""

TITLE_ART_SMALL = r"""
 _   ___      _              _    ____               _____ _
| | | \ \ /\ / /            | |  / ___|___  _      _|_   (_)_ __ _ __   ___ _ __
| | | |\ V  V /   ______    | | | |   / _ \| | /\ | || |  | | '_ \ '_ \ / _ \ '__|
\ \_/ / \_/\_/   |______|   | | | |__| (_) \ V  V / | |  | | |_) | |_) |  __/ |
 \___/                      |_|  \____\___/ \_/\_/  |_|  |_| .__/| .__/ \___|_|
                                                            |_|   |_|
"""

TITLE_ART_MINIMAL = """
╔════════════════════════════════╗
║    VIRTUAL COW TIPPER         ║
╚════════════════════════════════╝
"""


class MainMenu:
    """Main menu with title screen and options."""

    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(True)

    def show(self) -> str:
        """
        Display main menu and return user choice.

        Returns:
            'new_game', 'continue', 'how_to_play', or 'quit'
        """
        from save_manager import SaveManager

        # Check if save exists
        has_save = SaveManager.save_exists()

        menu_options = [
            "1. New Game",
            "2. Continue" if has_save else "2. Continue (No save found)",
            "3. Career Progress",
            "4. How to Play",
            "5. Quit"
        ]

        selected = 0

        while True:
            self.stdscr.clear()

            # Choose title based on terminal width
            if curses.COLS >= 95:
                title_art = TITLE_ART_LARGE
            elif curses.COLS >= 85:
                title_art = TITLE_ART_SMALL
            else:
                title_art = TITLE_ART_MINIMAL

            # Draw title
            title_lines = title_art.strip().split('\n')
            start_y = 2
            for i, line in enumerate(title_lines):
                x = max(0, (curses.COLS - len(line)) // 2)
                try:
                    self.stdscr.addstr(start_y + i, x, line)
                except:
                    pass

            # Draw menu
            menu_start_y = start_y + len(title_lines) + 3
            for i, option in enumerate(menu_options):
                y = menu_start_y + i
                x = (curses.COLS - len(option)) // 2

                if i == selected:
                    try:
                        self.stdscr.addstr(y, x, f"> {option} <", curses.A_REVERSE)
                    except:
                        pass
                else:
                    try:
                        self.stdscr.addstr(y, x, f"  {option}  ")
                    except:
                        pass

            # Draw footer
            footer = "Arrow keys to navigate | Enter to select | Created 2023"
            footer_y = curses.LINES - 2
            footer_x = (curses.COLS - len(footer)) // 2
            try:
                self.stdscr.addstr(footer_y, footer_x, footer, curses.A_DIM)
            except:
                pass

            self.stdscr.refresh()

            # Get input
            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                selected = (selected - 1) % len(menu_options)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(menu_options)
            elif key == ord('\n') or key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
                if key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
                    selected = int(chr(key)) - 1

                # Map selection to action
                if selected == 1 and not has_save:
                    # Continue option but no save - do nothing
                    continue

                actions = ['new_game', 'continue', 'career', 'how_to_play', 'quit']
                return actions[selected]

    def show_career_progress(self):
        """Display career progress screen."""
        from career_stats import CareerStats

        career = CareerStats.load()

        self.stdscr.clear()
        career.show_progress()
        self.stdscr.getch()

    def show_how_to_play(self):
        """Display how to play screen."""
        from help_screen import HELP_TEXT

        self.stdscr.clear()
        lines = HELP_TEXT.split('\n')

        for i, line in enumerate(lines[:curses.LINES - 2]):
            try:
                self.stdscr.addstr(i, 0, line[:curses.COLS - 1])
            except:
                pass

        self.stdscr.addstr(curses.LINES - 1, 0, "Press any key to return to menu...", curses.A_REVERSE)
        self.stdscr.refresh()
        self.stdscr.getch()

    def cleanup(self):
        """Restore terminal to normal mode."""
        curses.echo()
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.endwin()
