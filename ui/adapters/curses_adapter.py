"""
CursesAdapter - Bridge the existing curses implementation to the BaseUI interface.
This adapter wraps the current curses-based UI to work with the abstraction layer.
"""

import asyncio
import curses
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
import sys

# Add parent directory to path to import from terminal
sys.path.insert(0, '.')

from ui.interfaces.base_ui import BaseUI, UIMode, MenuChoice
from terminal.game_terminal import GameTerminal
from terminal.pause_menu import PauseMenu


class CursesAdapter(BaseUI):
    """
    Adapter that wraps the existing curses implementation.
    Provides async interface while maintaining backward compatibility.
    """

    def __init__(self):
        """Initialize the curses adapter."""
        self.terminal: Optional[GameTerminal] = None
        self.stdscr = None
        self.is_initialized = False
        self._screen_stack = []
        self._current_screen = "main"

    async def initialize(self) -> None:
        """Setup curses system."""
        try:
            # Initialize curses
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            curses.curs_set(0)
            self.stdscr.keypad(True)

            # Create game terminal wrapper
            self.terminal = GameTerminal()
            self.is_initialized = True

        except Exception as e:
            raise RuntimeError(f"Failed to initialize curses: {e}")

    async def shutdown(self) -> None:
        """Cleanup curses system."""
        if self.is_initialized and self.terminal:
            try:
                # Restore terminal settings
                curses.echo()
                curses.nocbreak()
                if self.stdscr:
                    self.stdscr.keypad(False)
                curses.endwin()
                self.is_initialized = False
            except:
                pass  # Ignore errors during cleanup

    # ==================== Display Methods ====================

    async def show_text(
        self,
        text: str,
        style: Optional[str] = None,
        duration: Optional[float] = None
    ) -> None:
        """Display text to the user."""
        if not self.terminal:
            print(text)  # Fallback to regular print
            return

        # Map style to curses attributes
        attr = 0
        if style == "error":
            attr = curses.A_BOLD | curses.color_pair(1)  # Red if colors available
        elif style == "success":
            attr = curses.A_BOLD
        elif style == "warning":
            attr = curses.A_DIM

        # Display using terminal's dialog system
        self.terminal.draw_dialog(text)
        self.terminal.refresh()

        if duration:
            # Auto-dismiss after duration
            await asyncio.sleep(duration)
        else:
            # Wait for user input
            self.terminal.stdscr.getch()

    async def show_menu(
        self,
        items: List[str],
        title: Optional[str] = None,
        allow_cancel: bool = True
    ) -> Optional[MenuChoice]:
        """Display menu and return user selection."""
        if not self.terminal:
            # Fallback implementation
            for i, item in enumerate(items):
                print(f"{i+1}. {item}")
            try:
                choice = int(input("Choose: ")) - 1
                if 0 <= choice < len(items):
                    return MenuChoice(index=choice, label=items[choice], value=choice)
            except:
                pass
            return None

        # Display title if provided
        if title:
            self.terminal.draw_title(title)

        # Format menu items with numbers
        menu_items = [f"{i+1}. {item}" for i, item in enumerate(items)]

        # Get choice using existing terminal menu system
        choice_num = self.terminal.get_menu_choice(menu_items)

        if choice_num and 1 <= choice_num <= len(items):
            idx = choice_num - 1
            return MenuChoice(index=idx, label=items[idx], value=idx)

        return None if allow_cancel else await self.show_menu(items, title, False)

    async def get_input(
        self,
        prompt: str,
        validator: Optional[Callable[[str], bool]] = None,
        default: Optional[str] = None
    ) -> str:
        """Get text input from user with validation."""
        while True:
            if self.terminal:
                # Use curses text input
                curses.echo()
                self.terminal.clear_area(self.terminal.PROMPT_INPUT_Y)
                self.terminal.draw(self.terminal.PROMPT_INPUT_Y, 0, f"{prompt}: ")
                self.terminal.refresh()

                # Get input
                input_str = self.terminal.stdscr.getstr().decode('utf-8')
                curses.noecho()
            else:
                # Fallback to standard input
                input_str = input(f"{prompt}: ")

            # Use default if empty
            if not input_str and default:
                input_str = default

            # Validate if validator provided
            if validator:
                if validator(input_str):
                    return input_str
                else:
                    await self.show_text("Invalid input. Please try again.", style="error")
            else:
                return input_str

    # ==================== Game-Specific Displays ====================

    async def update_stats(
        self,
        player_stats: Dict[str, Any],
        cow_stats: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update status displays."""
        if not self.terminal:
            return

        # Update player info
        stats_text = f"HP: {player_stats.get('hp', 0)}/{player_stats.get('max_hp', 20)}"
        stats_text += f" | Cash: ${player_stats.get('cash', 0)}"
        stats_text += f" | Floor: {player_stats.get('floor', 1)}"

        if player_stats.get('weapon'):
            stats_text += f" | Weapon: {player_stats['weapon']}"
        if player_stats.get('shield'):
            stats_text += f" | Shield: {player_stats['shield']}"

        self.terminal.set_player_stats(stats_text)

        # Update cow info if present
        if cow_stats:
            cow_text = f"{cow_stats.get('name', 'Cow')} | "
            cow_text += f"HP: {cow_stats.get('hp', [0,0])[0]}/{cow_stats.get('hp', [0,0])[1]} | "
            cow_text += f"Type: {cow_stats.get('type', 'Unknown')} | "
            cow_text += f"Mood: {cow_stats.get('mood', 'Neutral')}"
            self.terminal.set_cow_stats(cow_text)
        else:
            self.terminal.set_cow_stats('')

        self.terminal.refresh()

    async def show_combat(
        self,
        player_hp: tuple,
        cow_hp: tuple,
        combat_log: List[str]
    ) -> None:
        """Display combat state."""
        if not self.terminal:
            # Fallback
            print(f"Player HP: {player_hp[0]}/{player_hp[1]}")
            print(f"Cow HP: {cow_hp[0]}/{cow_hp[1]}")
            for msg in combat_log[-5:]:  # Show last 5 messages
                print(f"  {msg}")
            return

        # Update HP displays
        await self.update_stats(
            {'hp': player_hp[0], 'max_hp': player_hp[1]},
            {'hp': cow_hp}
        )

        # Show combat log
        log_text = "\n".join(combat_log[-5:])  # Last 5 messages
        self.terminal.draw_dialog(log_text)
        self.terminal.refresh()

    async def show_dialogue(
        self,
        speaker: str,
        text: str,
        choices: Optional[List[str]] = None
    ) -> Optional[int]:
        """Display dialogue with optional choices."""
        # Format dialogue
        dialogue = f"[{speaker}]: {text}"

        if not choices:
            # Just show dialogue
            await self.show_text(dialogue)
            return None

        # Show dialogue with choices
        if self.terminal:
            self.terminal.draw_dialog(dialogue)
            self.terminal.refresh()

        # Display choices as menu
        result = await self.show_menu(choices, allow_cancel=False)
        return result.index if result else None

    async def show_inventory(
        self,
        items: List[Dict[str, Any]],
        equipped: Dict[str, Any]
    ) -> None:
        """Display inventory screen."""
        inv_text = "=== INVENTORY ===\n\n"

        # Show equipped items
        inv_text += "EQUIPPED:\n"
        if equipped.get('weapon'):
            inv_text += f"  Weapon: {equipped['weapon']['name']} (DMG: {equipped['weapon']['damage']})\n"
        if equipped.get('shield'):
            inv_text += f"  Shield: {equipped['shield']['name']} (DEF: {equipped['shield']['defense']})\n"

        # Show inventory items
        inv_text += "\nITEMS:\n"
        if items:
            for i, item in enumerate(items[:10]):  # Show max 10 items
                inv_text += f"  {i+1}. {item.get('name', 'Unknown')} - {item.get('description', '')}\n"
        else:
            inv_text += "  (empty)\n"

        await self.show_text(inv_text)

    async def show_shop(
        self,
        shop_items: List[Dict[str, Any]],
        player_cash: int,
        player_inventory: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Display shop interface."""
        shop_text = f"=== SHOP === (Your cash: ${player_cash})\n\n"

        # Create menu items for shop
        menu_items = []
        for item in shop_items:
            price = item.get('price', 0)
            name = item.get('name', 'Unknown')
            can_afford = "✓" if player_cash >= price else "✗"
            menu_items.append(f"{name} - ${price} {can_afford}")

        menu_items.append("Exit Shop")

        # Show shop menu
        result = await self.show_menu(menu_items, title=shop_text)

        if result and result.index < len(shop_items):
            selected_item = shop_items[result.index]
            if player_cash >= selected_item.get('price', 0):
                return {
                    'action': 'buy',
                    'item': selected_item,
                    'price': selected_item.get('price', 0)
                }
            else:
                await self.show_text("Not enough cash!", style="error", duration=2)
                return await self.show_shop(shop_items, player_cash, player_inventory)

        return None

    # ==================== Event Handlers ====================

    async def on_pause(self) -> bool:
        """Handle pause request."""
        if self.terminal and hasattr(self.terminal, 'pause_menu'):
            # Use existing pause menu
            result = self.terminal.pause_menu.pause()
            return result != 'quit'
        else:
            # Simple pause menu
            result = await self.show_menu(
                ["Resume", "Save", "Quit"],
                title="GAME PAUSED"
            )
            return result and result.label != "Quit"

    async def show_error(
        self,
        message: str,
        fatal: bool = False
    ) -> None:
        """Display error message."""
        prefix = "FATAL ERROR" if fatal else "ERROR"
        await self.show_text(f"{prefix}: {message}", style="error")

        if fatal:
            await self.shutdown()
            sys.exit(1)

    async def show_notification(
        self,
        message: str,
        notification_type: str = "info"
    ) -> None:
        """Display temporary notification."""
        style_map = {
            "info": None,
            "success": "success",
            "warning": "warning",
            "error": "error"
        }

        await self.show_text(
            message,
            style=style_map.get(notification_type),
            duration=3.0  # Auto-dismiss after 3 seconds
        )

    # ==================== Screen Management ====================

    async def push_screen(
        self,
        screen_name: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Push a new screen onto the navigation stack."""
        self._screen_stack.append(self._current_screen)
        self._current_screen = screen_name
        await self.clear_screen()

    async def pop_screen(self) -> None:
        """Pop current screen from navigation stack."""
        if self._screen_stack:
            self._current_screen = self._screen_stack.pop()
            await self.clear_screen()

    async def clear_screen(self) -> None:
        """Clear the current screen display."""
        if self.terminal:
            self.terminal.clear_screen()
        elif self.stdscr:
            self.stdscr.clear()

    async def refresh(self) -> None:
        """Refresh the current screen."""
        if self.terminal:
            self.terminal.refresh()
        elif self.stdscr:
            self.stdscr.refresh()

    # ==================== Utility Methods ====================

    def get_mode(self) -> UIMode:
        """Get the UI mode of this implementation."""
        return UIMode.CURSES

    # ==================== Helper Methods ====================

    def _ensure_initialized(self) -> None:
        """Ensure curses is initialized before operations."""
        if not self.is_initialized:
            raise RuntimeError("CursesAdapter not initialized. Call initialize() first.")