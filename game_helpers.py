"""
Game Helpers - Shared utility functions for Virtual Cow Tipper

This module contains helper functions and classes that are used across
multiple parts of the game to reduce code duplication and improve maintainability.
"""
from typing import Optional, List, Any, Dict


class UIHelpers:
    """Terminal UI helper functions for consistent user interaction."""

    @staticmethod
    def show_message_with_pause(game_terminal, message: str, prompt: str = "[Continue...]",
                                clear_menu: bool = True):
        """
        Show a message with automatic pause and cleanup.

        This is the recommended way to show any message that requires user acknowledgment.
        It handles:
        - Clearing the menu area (if needed)
        - Drawing the message
        - Showing a prompt
        - Waiting for user input

        Args:
            game_terminal: The GameTerminal instance
            message: The message to display in the dialogue area
            prompt: The prompt text to show (default: "[Continue...]")
            clear_menu: Whether to hide the menu during the pause (default: True)
        """
        if clear_menu:
            game_terminal.clear_area(game_terminal.MENU_Y_START, game_terminal.MENU_Y_END)

        game_terminal.draw_dialog(message)

        # Clear prompt area first to remove any old text
        game_terminal.clear_area(game_terminal.PROMPT_INPUT_Y)

        # Show prompt
        prompt_y = game_terminal.PROMPT_INPUT_Y
        game_terminal.stdscr.addstr(prompt_y, 2, prompt)
        game_terminal.stdscr.refresh()
        game_terminal.stdscr.getch()

    @staticmethod
    def pause_with_prompt(game_terminal, prompt_text: str = "[Continue...]"):
        """
        Show a pause prompt and wait for keypress, with menu hidden.

        Lightweight version of show_message_with_pause() for when you've already
        drawn the dialogue and just need to pause.

        Args:
            game_terminal: The GameTerminal instance
            prompt_text: The prompt to display (default: "[Continue...]")
        """
        # Clear menu area so it doesn't show during pause
        game_terminal.clear_area(game_terminal.MENU_Y_START, game_terminal.MENU_Y_END)

        # Clear prompt area first to remove any old text
        game_terminal.clear_area(game_terminal.PROMPT_INPUT_Y)

        # Show prompt
        prompt_y = game_terminal.PROMPT_INPUT_Y
        game_terminal.stdscr.addstr(prompt_y, 2, prompt_text)
        game_terminal.stdscr.refresh()
        game_terminal.stdscr.getch()


class InventoryHelpers:
    """Inventory management utilities."""

    @staticmethod
    def find_item_by_type(inventory: List[Any], item_class: type) -> Optional[Any]:
        """
        Find the first item of a given type in the inventory.

        Args:
            inventory: List of items to search
            item_class: The class type to search for (e.g., Bucket, CowBell)

        Returns:
            The first item of the specified type, or None if not found
        """
        for item in inventory:
            if isinstance(item, item_class):
                return item
        return None

    @staticmethod
    def get_sellable_items(inventory: List[Any]) -> List[Any]:
        """
        Get all items from inventory that can be sold (have stats).

        Args:
            inventory: List of items to filter

        Returns:
            List of sellable items (weapons, shields, etc.)
        """
        return [item for item in inventory if hasattr(item, 'stats')]

    @staticmethod
    def get_equipment_items(inventory: List[Any]) -> Dict[str, List[Any]]:
        """
        Categorize inventory items by type.

        Returns:
            Dict with keys: 'weapons', 'shields', 'consumables', 'tools'
        """
        from item import Weapon, Shield, Potion, Tool

        return {
            'weapons': [i for i in inventory if isinstance(i, Weapon)],
            'shields': [i for i in inventory if isinstance(i, Shield)],
            'consumables': [i for i in inventory if isinstance(i, Potion)],
            'tools': [i for i in inventory if isinstance(i, Tool)]
        }


class PricingHelpers:
    """Shop pricing and economy calculations."""

    @staticmethod
    def calculate_sell_price(item, cow_mood: str, base_multiplier: float = 2.0) -> int:
        """
        Calculate the sell price for an item based on shop mood.

        Args:
            item: The item being sold
            cow_mood: The shop keeper's mood ('friendly', 'neutral', 'upset')
            base_multiplier: Base multiplier for calculating item value (default: 2.0)

        Returns:
            The sell price in cash
        """
        from item_factory import ItemFactory
        from game_config import (
            SELL_PRICE_VALUE_MULTIPLIER,
            SELL_PRICE_FRIENDLY,
            SELL_PRICE_NEUTRAL,
            SELL_PRICE_UPSET,
            SELL_PRICE_MINIMUM
        )

        # Estimate item value based on median stat
        median_stat = ItemFactory.calculate_item_median_stat(item)
        base_value = int(median_stat * SELL_PRICE_VALUE_MULTIPLIER)

        # Mood affects sell price (friendly pays more)
        sell_percentages = {
            'friendly': SELL_PRICE_FRIENDLY,
            'neutral': SELL_PRICE_NEUTRAL,
            'upset': SELL_PRICE_UPSET
        }
        sell_percentage = sell_percentages.get(cow_mood, SELL_PRICE_NEUTRAL)

        return max(SELL_PRICE_MINIMUM, int(base_value * sell_percentage))


class CombatMessageFormatter:
    """Standardized combat message formatting for consistent UX."""

    @staticmethod
    def format_player_attack(player_name: str, cow_name: str, cow_hp: int) -> str:
        """
        Format message for player attack action.

        Args:
            player_name: The player's name
            cow_name: The cow's name
            cow_hp: Remaining HP after attack

        Returns:
            Formatted attack message
        """
        if cow_hp <= 0:
            return f"{player_name} attacks {cow_name}!\n\n{cow_name} is defeated!"
        return f"{player_name} attacks {cow_name}!\n\n{cow_name}: {cow_hp} HP remaining"

    @staticmethod
    def format_victory(cow_name: str, cash_reward: int, item_drop: Optional[str] = None) -> str:
        """
        Format victory message after defeating a cow.

        Args:
            cow_name: The defeated cow's name
            cash_reward: Cash reward amount
            item_drop: Optional item drop name

        Returns:
            Formatted victory message
        """
        msg = f"=== VICTORY ===\nYou defeat {cow_name}!\n\nRewards:\n  Cash: +${cash_reward}"
        if item_drop:
            msg += f"\n  Item Drop: {item_drop}!"
        return msg

    @staticmethod
    def format_flee(cow_name: str) -> str:
        """Format message for fleeing combat."""
        return f"Fled!\n\nYou escape from {cow_name}."

    @staticmethod
    def create_hp_bar(current_hp: int, max_hp: int, label: str, bar_width: int = 20) -> str:
        """
        Create a visual HP bar for combat display.

        Args:
            current_hp: Current HP value
            max_hp: Maximum HP value
            label: Label for the HP bar
            bar_width: Width of the bar in characters (default: 20)

        Returns:
            Formatted HP bar string
        """
        filled = int((current_hp / max_hp) * bar_width) if max_hp > 0 else 0
        empty = bar_width - filled

        hp_bar = '[' + ('=' * filled) + (' ' * empty) + ']'
        return f"{label}: {hp_bar} {current_hp}/{max_hp} HP"


class TransactionFormatter:
    """Format shop transaction messages consistently."""

    @staticmethod
    def format_transaction(action: str, item_name: str, amount: int,
                          new_balance: int, transaction_count: int,
                          total_amount: int) -> str:
        """
        Format a shop transaction message.

        Args:
            action: "Purchased" or "Sold"
            item_name: Name of the item
            amount: Transaction amount (price paid or received)
            new_balance: Player's cash balance after transaction
            transaction_count: Number of items in this category during visit
            total_amount: Total cash spent/earned during visit

        Returns:
            Formatted transaction message
        """
        action_verb = "Paid" if action == "Purchased" else "Received"
        total_verb = "spent" if action == "Purchased" else "earned"

        return (
            f"{action}: {item_name}\n"
            f"{action_verb}: ${amount} | Remaining: ${new_balance}\n\n"
            f"Visit Total: {transaction_count} items | ${total_amount} {total_verb}"
        )

    @staticmethod
    def format_shop_summary(cow_name: str, purchases: List[tuple], sales: List[tuple],
                           starting_cash: int, ending_cash: int) -> str:
        """
        Format a complete shop visit summary.

        Args:
            cow_name: Shop keeper's name
            purchases: List of (item_name, price) tuples
            sales: List of (item_name, price) tuples
            starting_cash: Cash at start of visit
            ending_cash: Cash at end of visit

        Returns:
            Formatted summary message
        """
        if not purchases and not sales:
            return f"Leaving {cow_name}'s Shop\n\nYou browsed but didn't transact."

        msg = f"Leaving {cow_name}'s Shop\n\n"

        if purchases:
            msg += f"Purchased: {len(purchases)} items\n"
            for item_name, price in purchases:
                msg += f"  • {item_name} (${price})\n"

        if sales:
            msg += f"\nSold: {len(sales)} items\n"
            for item_name, price in sales:
                msg += f"  • {item_name} (${price})\n"

        # Net change
        total_spent = sum(price for _, price in purchases)
        total_earned = sum(price for _, price in sales)
        net_change = total_earned - total_spent

        msg += f"\nCash: ${starting_cash} → ${ending_cash}"
        if net_change < 0:
            msg += f" (spent ${abs(net_change)})"
        elif net_change > 0:
            msg += f" (profit ${net_change})"

        return msg


class ValidationHelpers:
    """Input validation utilities."""

    @staticmethod
    def validate_menu_choice(choice: int, min_option: int, max_option: int) -> bool:
        """
        Validate that a menu choice is within valid range.

        Args:
            choice: The selected option number
            min_option: Minimum valid option (usually 1)
            max_option: Maximum valid option

        Returns:
            True if choice is valid, False otherwise
        """
        return min_option <= choice <= max_option

    @staticmethod
    def safe_int_input(prompt: str, default: int = 0, min_val: int = None,
                      max_val: int = None) -> int:
        """
        Safely get integer input with validation.

        Args:
            prompt: The input prompt to display
            default: Default value if input is invalid
            min_val: Optional minimum allowed value
            max_val: Optional maximum allowed value

        Returns:
            Valid integer input or default value
        """
        try:
            value = int(input(prompt).strip())
            if min_val is not None and value < min_val:
                return default
            if max_val is not None and value > max_val:
                return default
            return value
        except (ValueError, EOFError):
            return default
