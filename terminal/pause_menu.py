import curses
import sys

class PauseMenu:
    def __init__(self, game_terminal):
        self.game_terminal = game_terminal
        self.dialog_history = game_terminal.dialog_history
        self.KEY_UP, self.KEY_DOWN, self.KEY_ENTER, self.KEY_SPACE, self.KEY_ESCAPE, self.NUM_OFFSET = game_terminal.get_key_variables()

    def pause(self):
        self.game_terminal.stdscr.clear()
        self.game_terminal.stdscr.refresh()

        self.game_terminal.draw_player_stats(show_equiptment=False)
        self.game_terminal.draw_cow_stats()
        self.draw_pause_menu_title()
        self.game_terminal.draw_separator(2)
        self.show_dialog_history()
        self.set_menu_start_position()

        self.game_terminal.stdscr.nodelay(True)
        try:
            pause_menu_items = ['1. Continue', '2. Help/Controls', '3. Quit Game']
            selected_index = 0

            while True:
                key = self.game_terminal.prompt_and_draw_menu(pause_menu_items, selected_index)
                key_actions = self.get_pause_menu_key_actions(selected_index, pause_menu_items)

                action = key_actions.get(key)
                if action:
                    new_index = action()
                    if new_index is not None:
                        selected_index = new_index
                    else:
                        if selected_index == 0:
                            self.game_terminal.stdscr.clear()
                            self.game_terminal.stdscr.refresh()
                            break
                        elif selected_index == 1:
                            self.show_options()
                        elif selected_index == 2:
                            self.game_terminal.close_game_terminal()
                            sys.exit(0)
                elif key == self.KEY_ESCAPE:
                    self.game_terminal.stdscr.clear()
                    self.game_terminal.stdscr.refresh()
                    break
                elif self.NUM_OFFSET <= key <= self.NUM_OFFSET + len(pause_menu_items) - 1:
                    selected_index = key - self.NUM_OFFSET
                    continue
        finally:
            self.game_terminal.stdscr.nodelay(False)
        self.game_terminal.refresh()

    def set_menu_start_position(self):
        consecutive_empty_lines = 0
        for y in range(1, self.game_terminal.PROMPT_INPUT_Y):
            if not self.game_terminal.is_line_populated(y):
                consecutive_empty_lines += 1
                if consecutive_empty_lines == 2:
                    self.game_terminal.PROMPT_INPUT_Y = y 
                    self.game_terminal.MENU_Y_START = y + 1
                    break
            else:
                consecutive_empty_lines = 0

    def draw_pause_menu_title(self):
        title = "Pause Menu"
        start_x = (self.game_terminal.WIDTH - len(title)) // 2
        self.game_terminal.stdscr.addstr(0, start_x, title, curses.A_BOLD)

    def get_pause_menu_key_actions(self, selected_index, menu_items):
        KEY_UP, KEY_DOWN, KEY_ENTER, KEY_SPACE, KEY_ESCAPE, _ = self.game_terminal.get_key_variables()

        # Build key actions dict
        # KEY_ENTER is a list, KEY_SPACE is a single value
        key_actions = {
            KEY_UP: lambda: (selected_index - 1) % len(menu_items),
            KEY_DOWN: lambda: (selected_index + 1) % len(menu_items),
            KEY_SPACE: lambda: None,
            KEY_ESCAPE: lambda: None,
        }

        # Add all enter key variants
        for enter_code in KEY_ENTER:
            key_actions[enter_code] = lambda: None

        return key_actions

    def draw_pause_menu(self, menu_items, selected_index=None):
        start_y = (self.game_terminal.HEIGHT - len(menu_items)) // 2
        start_x = (self.game_terminal.WIDTH - len(menu_items[0])) // 2
        for i, item in enumerate(menu_items):
            self.game_terminal.stdscr.move(start_y + i, start_x)
            self.game_terminal.stdscr.clrtoeol()
            if i == selected_index:
                self.game_terminal.stdscr.addstr(start_y + i, start_x, item.ljust(self.game_terminal.WIDTH), curses.A_REVERSE)
            else:
                self.game_terminal.stdscr.addstr(start_y + i, start_x, item.ljust(self.game_terminal.WIDTH))

    def show_dialog_history(self):
        self.game_terminal.clear_area(self.game_terminal.DIALOG_Y_START - 2, self.game_terminal.DIALOG_Y_END - 2)
        available_lines = min(3, self.game_terminal.DIALOG_Y_END - self.game_terminal.DIALOG_Y_START + 2)
        recent_messages = list(reversed(self.game_terminal.dialog_history.dialog_history[-available_lines:]))
        
        for idx, item in enumerate(recent_messages):
            timestamp, message = item

            if len(message) > self.game_terminal.dialog_history.message_max_chars:
                truncate_position = self.game_terminal.dialog_history.message_max_chars - 3
                if message[truncate_position - 1] == " ":
                    truncate_position -= 1
                message = message[:truncate_position] + "..."

            self.game_terminal.draw(self.game_terminal.DIALOG_Y_START - 2 + idx, 0, f"{timestamp} {message}")
        self.game_terminal.stdscr.refresh()

    def show_options(self):
        """Show help/controls screen."""
        from help_screen import show_help
        show_help(self.game_terminal)
