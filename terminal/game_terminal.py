import curses
import os
from .pause_menu import PauseMenu
from .dialog_history import DialogHistory

class GameTerminal:
    WIDTH = 85  # Reduced from 100 to create natural margins for print() text
    HEIGHT = 30
    LEFT_MARGIN = 2   # Add left margin for readability
    RIGHT_MARGIN = 2  # Add right margin

    PLAYER_INFO_Y = 0
    COW_INFO_Y = 0
    COW_INFO_X = 50
    TITLE_Y = 2
    SEPARATOR_Y = 4
    PAUSE_DIALOG_LINES = 5

    ART_Y_START = 5
    ART_Y_END = 19

    DIALOG_Y_START = 20
    DIALOG_Y_END = DIALOG_Y_START + 1

    INSTRUCTIONS_Y_START = 22
    INSTRUCTIONS_Y_END = INSTRUCTIONS_Y_START + 1

    PROMPT_INPUT_Y = 24

    MENU_Y_START = 25
    MENU_Y_END = MENU_Y_START + 3

    def __init__(self, title="Virtual Cow Tipper"):
        self.title = title
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(True)
        self.stdscr.resize(self.HEIGHT, self.WIDTH)
        self.show_art = False
        self.player_stats = ''
        self.player_weapon = ''
        self.player_shield = ''
        self.cow_stats = 'Diary of a Cow | Solid'
        self.dialog_history = DialogHistory()
        self.pause_menu = PauseMenu(self)

    def draw(self, y, x, text, custom_attr=0, align='left'):
        """Draw text with margin consideration."""
        # Apply left margin
        x = x + self.LEFT_MARGIN

        if align == 'right':
            x = self.WIDTH - len(text) - self.RIGHT_MARGIN

        # Truncate text if it would exceed right margin
        max_width = self.WIDTH - self.LEFT_MARGIN - self.RIGHT_MARGIN
        if len(text) > max_width:
            text = text[:max_width - 3] + "..."

        try:
            self.stdscr.addstr(y, x, text, custom_attr)
        except:
            pass  # Ignore if out of bounds

    def generate_pointer(self, menu_item_length, total_width):
        """Generate menu pointer - simplified to prevent wrapping."""
        # Use simple arrows instead of long equal signs
        # This prevents the wrap issue you're seeing
        pointer_left = ">"
        pointer_right = "<"
        spaces = " " * 4

        return f"{pointer_left}{spaces}{pointer_right}"

    def draw_menu(self, menu_items, selected_index=None):
        """Draw menu with safe margins."""
        self.clear_area(self.MENU_Y_START, self.MENU_Y_END + 1)

        for i, item in enumerate(menu_items):
            y = self.MENU_Y_START + i
            self.stdscr.move(y, 0)
            self.stdscr.clrtoeol()

            if i == selected_index:
                # Simple pointer: >    <  Item text
                pointer = self.generate_pointer(len(item), self.WIDTH)
                display_text = f"{pointer} {item}"

                # Use draw() for margin support
                x = self.LEFT_MARGIN
                try:
                    self.stdscr.addstr(y, x, display_text[:self.WIDTH - self.LEFT_MARGIN - self.RIGHT_MARGIN])
                    # Highlight the item text
                    self.stdscr.chgat(y, x, len(display_text), curses.A_REVERSE)
                except:
                    pass
            else:
                # Unselected: just show item with margin
                try:
                    self.stdscr.addstr(y, self.LEFT_MARGIN, item)
                except:
                    pass

        self.stdscr.refresh()
                
    def get_key_variables(self):
        KEY_UP = 450
        KEY_DOWN = 456
        KEY_ENTER = ord('\n')
        KEY_ESCAPE = 27
        NUM_OFFSET = 49

        return KEY_UP, KEY_DOWN, KEY_ENTER, KEY_ESCAPE, NUM_OFFSET

    def prompt_and_draw_menu(self, menu_items, selected_index, prompt=None):
        prompt_message = prompt if prompt is not None else 'Select an option:'
        self.draw_menu(menu_items, selected_index)
        self.clear_area(self.PROMPT_INPUT_Y)
        self.draw(self.PROMPT_INPUT_Y, 0, prompt_message)
        self.stdscr.chgat(self.PROMPT_INPUT_Y, 0, len(prompt_message), 0)
        self.stdscr.refresh()
        key = self.stdscr.getch()
        return key

    def get_menu_choice(self, menu_items, prompt=None):
        KEY_UP, KEY_DOWN, KEY_ENTER, KEY_ESCAPE, NUM_OFFSET = self.get_key_variables()

        key_actions = {
            KEY_UP: lambda: (selected_index - 1) % len(menu_items),
            KEY_DOWN: lambda: (selected_index + 1) % len(menu_items),
            KEY_ENTER: lambda: None,
            KEY_ESCAPE: lambda: self.pause_menu.pause(),
        }

        selected_index = 0
        self.enable_mouse()
        while True:
            key = self.prompt_and_draw_menu(menu_items, selected_index, prompt)

            if key in key_actions:
                action = key_actions[key]
                result = action()
                if result is None:
                    break
                elif key == KEY_ESCAPE:
                    continue
                else:
                    selected_index = result
            elif NUM_OFFSET <= key <= NUM_OFFSET + len(menu_items) - 1:
                selected_index = key - NUM_OFFSET
                break

        self.disable_mouse()
        self.clear_area(self.DIALOG_Y_START, self.DIALOG_Y_END)
        self.clear_area(self.PROMPT_INPUT_Y)
        self.stdscr.refresh()
        return selected_index + 1

    def draw_art(self):
        self.clear_area(self.ART_Y_START, self.ART_Y_END)
        for idx, line in enumerate(self.art):
            self.draw(self.ART_Y_START + idx, 0, line)

    def draw_separator(self, offset=0):
        self.draw(self.SEPARATOR_Y - offset, 0, "-" * self.WIDTH)

    def draw_game_title(self):
        x = (self.WIDTH - len(self.title)) // 2
        self.draw(self.TITLE_Y, x, self.title, curses.A_BOLD)

    def draw_player_stats(self, show_equiptment=True):
        self.clear_area(self.PLAYER_INFO_Y, self.PLAYER_INFO_Y + 3)  
        self.draw(self.PLAYER_INFO_Y, 0, self.player_stats)
        if show_equiptment:
            self.draw(self.PLAYER_INFO_Y + 1, 0, self.player_weapon)
            self.draw(self.PLAYER_INFO_Y + 2, 0, self.player_shield)

    def draw_cow_stats(self):
        self.draw(y=self.COW_INFO_Y, x=0, text=self.cow_stats, align='right')

    def draw_dialog(self, text):
        """Draw dialog with word wrapping to fit margins."""
        self.clear_area(self.DIALOG_Y_START, self.DIALOG_Y_END)
        self.dialog_history.add_dialog(text)

        # Word wrap text to fit within margins
        max_width = self.WIDTH - self.LEFT_MARGIN - self.RIGHT_MARGIN - 4
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_width:
                current_line += (word + " ")
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        # Draw wrapped lines
        for idx, line in enumerate(lines[:2]):  # Max 2 lines of dialog
            self.draw(self.DIALOG_Y_START + idx, 0, line)

    def set_player_stats(self, stats, weapon, shield):
        self.player_stats = stats
        self.player_weapon = weapon
        self.player_shield = shield

    def set_cow_stats(self, stats):
        self.cow_stats = stats

    def toggle_art_display(self, art=None):
        self.show_art = not self.show_art
        if art:
            self.art = art.split("\n")

    def handle_pause(self):
        self.pause_menu.pause()

    def enable_mouse(self):
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

    def disable_mouse(self):
        curses.mousemask(0)

    def is_line_populated(self, line_number):
        line_content = self.stdscr.instr(line_number, 0, self.WIDTH).decode('utf-8')
        line_content_stripped = ''.join(line_content.split())
        return len(line_content_stripped) > 0

    def set_section_positions(self, start_y):
        end_y = start_y + self.is_line_populated(start_y)
        next_start_y = end_y + 1
        return start_y, end_y, next_start_y

    def update_section_positions(self):
        current_y = 5

        if self.show_art:
            current_y = self.ART_Y_END + 1
        else:
            self.DIALOG_Y_START, self.DIALOG_Y_END, current_y = self.set_section_positions(current_y)
            self.INSTRUCTIONS_Y_START, self.INSTRUCTIONS_Y_END, current_y = self.set_section_positions(current_y)

            self.PROMPT_INPUT_Y = current_y
            current_y += 1

        self.MENU_Y_START = current_y
        self.MENU_Y_END = self.MENU_Y_START + 3

    def clear_area(self, start_line, end_line=None):
        if end_line is None:
            end_line = start_line

        for line in range(start_line, end_line + 1):
            self.stdscr.move(line, 0)
            self.stdscr.clrtoeol()

    def clear_screen(self):
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def refresh(self):
        self.clear_screen()
        self.update_section_positions()
        self.draw_player_stats()
        self.draw_game_title()
        self.draw_cow_stats()
        self.draw_separator()

        if self.show_art:
            self.draw_art()

        self.stdscr.refresh()

    def close_game_terminal(self):
        curses.echo()
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.endwin()
