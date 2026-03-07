import curses
import os
from .pause_menu import PauseMenu
from .dialog_history import DialogHistory

class GameTerminal:
    WIDTH = 85  # Reduced from 100 to create natural margins for print() text
    HEIGHT = 30
    LEFT_MARGIN = 2   # Add left margin for readability
    RIGHT_MARGIN = 2  # Add right margin

    # Header section (top)
    PLAYER_INFO_Y = 0
    COW_INFO_Y = 0
    COW_INFO_X = 50
    TITLE_Y = 2
    SEPARATOR_Y = 4

    # Main content area (reorganized for left-aligned flow)
    DIALOG_Y_START = 6   # Dialogue starts right after separator
    DIALOG_Y_END = 16    # Compact dialogue area (10 lines) - leave room for menu

    # Art section (optional, overlaps with dialogue area)
    ART_Y_START = 6
    ART_Y_END = 16
    PAUSE_DIALOG_LINES = 5

    # Instructions area
    INSTRUCTIONS_Y_START = 17
    INSTRUCTIONS_Y_END = INSTRUCTIONS_Y_START + 1

    # Input/menu section (bottom)
    PROMPT_INPUT_Y = 18

    MENU_Y_START = 19
    MENU_Y_END = MENU_Y_START + 6  # 7 lines for menu options

    def __init__(self, title="Virtual Cow Tipper"):
        self.title = title
        self.stdscr = curses.initscr()

        # Clear the screen immediately to prevent bleed-through
        self.stdscr.clear()
        self.stdscr.refresh()

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(True)

        # Use full terminal size instead of fixed resize
        # This prevents bleed-through from terminal content
        max_height, max_width = self.stdscr.getmaxyx()

        # Validate minimum terminal size
        MIN_HEIGHT = 25
        MIN_WIDTH = 60
        if max_height < MIN_HEIGHT or max_width < MIN_WIDTH:
            curses.endwin()
            raise RuntimeError(
                f"Terminal too small ({max_width}x{max_height}). "
                f"Minimum: {MIN_WIDTH}x{MIN_HEIGHT}"
            )

        # Adjust our constants to fit the actual terminal
        self.HEIGHT = min(self.HEIGHT, max_height)
        self.WIDTH = min(self.WIDTH, max_width)

        # Set background character to fill entire screen
        try:
            self.stdscr.bkgd(' ', curses.A_NORMAL)
        except curses.error:
            pass

        # Clear entire terminal, not just our window
        self.stdscr.clear()
        self.stdscr.refresh()

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
        except curses.error:
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
        """Draw menu with safe margins - FIXED to actually show items."""
        self.clear_area(self.MENU_Y_START, self.MENU_Y_END + 1)

        # Calculate one x position for all items (centered)
        max_item_width = max(len(item) for item in menu_items) if menu_items else 40
        menu_x = max(self.LEFT_MARGIN, (self.WIDTH - max_item_width - 4) // 2)

        for i, item in enumerate(menu_items):
            y = self.MENU_Y_START + i

            # Make sure y is within bounds
            if y >= curses.LINES - 1:
                break

            self.stdscr.move(y, 0)
            self.stdscr.clrtoeol()

            if i == selected_index:
                # Selected: > Item <
                display_text = f"> {item} <"
                try:
                    self.stdscr.addstr(y, menu_x, display_text)
                    self.stdscr.chgat(y, menu_x, len(display_text), curses.A_REVERSE)
                except curses.error:
                    pass
            else:
                # Unselected:   Item   (aligned with selected)
                display_text = f"  {item}  "
                try:
                    self.stdscr.addstr(y, menu_x, display_text)
                except curses.error:
                    pass

        # Always refresh after drawing menu so it's immediately visible
        self.stdscr.refresh()

    def get_key_variables(self):
        # Use curses constants for arrow keys (more reliable)
        KEY_UP = curses.KEY_UP
        KEY_DOWN = curses.KEY_DOWN
        # Support multiple enter keys
        KEY_ENTER = [ord('\n'), ord('\r'), curses.KEY_ENTER, 10, 13]
        # Support space key for selection
        KEY_SPACE = ord(' ')
        KEY_ESCAPE = 27
        NUM_OFFSET = 49

        return KEY_UP, KEY_DOWN, KEY_ENTER, KEY_SPACE, KEY_ESCAPE, NUM_OFFSET

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
        KEY_UP, KEY_DOWN, KEY_ENTER, KEY_SPACE, KEY_ESCAPE, NUM_OFFSET = self.get_key_variables()

        selected_index = 0
        self.enable_mouse()
        while True:
            key = self.prompt_and_draw_menu(menu_items, selected_index, prompt)

            # Check for enter keys (multiple supported)
            if key in KEY_ENTER or key == KEY_SPACE:
                # Select current item
                break
            elif key == KEY_UP:
                selected_index = (selected_index - 1) % len(menu_items)
            elif key == KEY_DOWN:
                selected_index = (selected_index + 1) % len(menu_items)
            elif key == KEY_ESCAPE:
                self.pause_menu.pause()
                continue
            elif NUM_OFFSET <= key <= NUM_OFFSET + len(menu_items) - 1:
                # Number key pressed
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
        # Draw a clean separator line
        separator_width = self.WIDTH - self.LEFT_MARGIN - self.RIGHT_MARGIN
        separator = "-" * separator_width
        self.draw(self.SEPARATOR_Y - offset, 0, separator)
        self.stdscr.refresh()

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
        # Draw cow stats on the right side of the screen
        # Use explicit x position to ensure it's on the right
        cow_x = self.COW_INFO_X
        try:
            self.stdscr.addstr(self.COW_INFO_Y, cow_x, self.cow_stats)
        except curses.error:
            pass
        self.stdscr.refresh()

    def save_dialog_state(self) -> str:
        """
        Save current dialogue text for restoration later.

        Uses the last dialog from dialog_history, which stores the original
        text before word-wrapping. This ensures perfect restoration.

        Returns:
            String containing dialogue text, or empty string if nothing to save.
        """
        if self.dialog_history.dialog_history:
            timestamp, last_dialog = self.dialog_history.dialog_history[-1]
            return last_dialog
        return ""

    def restore_dialog_state(self, saved_text: str):
        """
        Restore previously saved dialogue text.

        Args:
            saved_text: Original text to restore (from save_dialog_state)

        Safe to call with empty string - will skip restoration.
        """
        if saved_text:
            self.draw_dialog(saved_text)

    def draw_dialog(self, text):
        """Draw dialog with word wrapping to fit margins."""
        self.clear_area(self.DIALOG_Y_START, self.DIALOG_Y_END)
        self.dialog_history.add_dialog(text)

        # Respect newlines in the text - split by newline first
        max_width = self.WIDTH - self.LEFT_MARGIN - self.RIGHT_MARGIN - 4
        input_lines = text.split('\n')
        lines = []

        # Process each line separately to preserve intentional line breaks
        for input_line in input_lines:
            if not input_line.strip():
                # Empty line - preserve it
                lines.append("")
                continue

            # Word wrap this line
            words = input_line.split(' ')
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

        # Draw wrapped lines - now support up to 12 lines (DIALOG_Y_END - DIALOG_Y_START)
        max_lines = self.DIALOG_Y_END - self.DIALOG_Y_START
        for idx, line in enumerate(lines[:max_lines]):
            self.draw(self.DIALOG_Y_START + idx, 0, line)

        # Always refresh after drawing dialog so it's immediately visible
        self.stdscr.refresh()

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
        """Clear the screen using curses."""
        # Use curses clear instead of os.system to prevent interference
        self.stdscr.clear()
        # Erase the entire window to prevent any bleed-through
        self.stdscr.erase()
        # Fill with background
        try:
            self.stdscr.bkgd(' ', curses.A_NORMAL)
        except curses.error:
            pass

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
