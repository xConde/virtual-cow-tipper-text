from typing import Optional, List
import random

from item import Weapon, Shield, Tool, CowBell, Bucket, Potion, roll_weapon_dmg, Item
from assets.context import small_damage_contexts, large_damage_contexts
from utils import safe_print
from game_config import (
    PLAYER_STARTING_HP,
    PLAYER_STARTING_CASH,
    PLAYER_MAX_INVENTORY_SIZE,
    PLAYER_BASE_DAMAGE_MIN,
    PLAYER_BASE_DAMAGE_MAX,
    PLAYER_DAMAGE_CASH_SCALING,
    SMALL_DAMAGE_THRESHOLD,
    LARGE_DAMAGE_THRESHOLD,
    SMALL_DAMAGE_CONTEXT_CHANCE,
)

class Player:
    def __init__(self, game_terminal, name: str,
                 starting_hp: int = PLAYER_STARTING_HP,
                 starting_cash: int = PLAYER_STARTING_CASH):
        self.game_terminal = game_terminal
        self.name = name
        self.hp = starting_hp
        self.cash = starting_cash
        self.inventory: List[Item] = []
        self.weapon: Optional[Weapon] = None
        self.shield: Optional[Shield] = None
        self.stunned_turns = 0  # For stun effect implementation

    def display_info(self, combat=True):
        player_stats = f"{self.name} | HP: {self.hp} | Cash: ${self.cash}"
        weapon = self.weapon.display_name() if self.weapon else "Weapon: None"
        shield = self.shield.display_name() if self.shield else "Shield: None"
        self.game_terminal.set_player_stats(player_stats, weapon, shield)
        # DON'T call game_terminal.refresh() - it clears dialogue area!
        # Just update stats in header without clearing
        self.game_terminal.draw_player_stats()
        self.game_terminal.draw_game_title()
        self.game_terminal.draw_separator()
        self.game_terminal.stdscr.refresh()

    def equip(self, item):
        """Equip a weapon or shield and update display."""
        if isinstance(item, Weapon):
            self.weapon = item
            self.display_info()
        elif isinstance(item, Shield):
            self.shield = item
            self.display_info()
        else:
            safe_print(f"{item.name} is neither a weapon nor a shield and cannot be equipped.")

    def get_damage_context(self, cow_name, total_damage, cow_hp_before_damage) -> Optional[str]:
        """
        Get optional flavor text for damage context.

        Returns:
            Flavor text string if context should be shown, None otherwise
        """
        print_small_hit_context = total_damage <= cow_hp_before_damage * SMALL_DAMAGE_THRESHOLD and random.random() <= SMALL_DAMAGE_CONTEXT_CHANCE
        print_large_hit_context = total_damage >= cow_hp_before_damage * LARGE_DAMAGE_THRESHOLD

        if print_small_hit_context:
            context = random.choice(small_damage_contexts)
            return context.format(player_name=self.name, cow_name=cow_name, total_damage=total_damage)
        elif print_large_hit_context:
            context = random.choice(large_damage_contexts)
            return context.format(player_name=self.name, cow_name=cow_name, total_damage=total_damage)

        return None

    def deal_damage(self, cow) -> tuple[int, Optional[str]]:
        """
        Calculate and apply damage to cow.

        Returns:
            Tuple of (damage_dealt, optional_flavor_text)
        """
        base_damage = random.randint(PLAYER_BASE_DAMAGE_MIN, PLAYER_BASE_DAMAGE_MAX) + (self.cash // PLAYER_DAMAGE_CASH_SCALING)
        weapon_damage = roll_weapon_dmg(self.weapon)
        career_bonus = getattr(self, 'damage_bonus', 0)
        total_damage = base_damage + weapon_damage + career_bonus
        total_damage = min(total_damage, cow.hp)

        cow_hp_before = cow.hp
        flavor_text = self.get_damage_context(cow.name, total_damage, cow_hp_before)

        cow.hp -= total_damage
        self.display_info()

        return (total_damage, flavor_text)

    def _show_item_actions(self, item):
        """Show available actions for a selected item."""
        if isinstance(item, Weapon):
            details = f"Weapon Details\n\n{item.stats()}\n\nEquip this weapon?"
            actions = ["Equip", "Back to inventory"]
        elif isinstance(item, Shield):
            details = f"Shield Details\n\n{item.stats()}\n\nEquip this shield?"
            actions = ["Equip", "Back to inventory"]
        elif isinstance(item, Potion):
            details = f"Potion Details\n\n{item.name}\nHeals: {item.boost_amount} HP\n\nUse this potion?"
            actions = ["Use potion", "Back to inventory"]
        elif isinstance(item, Tool):
            details = f"Tool Details\n\n{item.name}\n\n{item.description if hasattr(item, 'description') else 'Special item'}"
            actions = ["Back to inventory"]  # Tools can't be used in combat
        else:
            details = f"Item Details\n\n{item.name}"
            actions = ["Back to inventory"]

        self.game_terminal.draw_dialog(details)

        menu_items = [f"{i+1}. {action}" for i, action in enumerate(actions)]
        choice = self.game_terminal.get_menu_choice(menu_items, "What would you like to do?")

        if choice == 1 and len(actions) > 1:
            if isinstance(item, (Weapon, Shield)):
                old_item = self.weapon if isinstance(item, Weapon) else self.shield
                self.equip(item)

                equip_msg = f"Equipped: {item.name}!"
                if old_item:
                    equip_msg += f"\n\nPrevious: {old_item.name} (still in inventory)"

                self.game_terminal.draw_dialog(equip_msg)
                self._pause_for_inventory()
            elif isinstance(item, Potion):
                if item.use(self):
                    self.inventory.remove(item)
                    use_msg = f"Used {item.name}!\n\nHP restored: +{item.boost_amount}\nCurrent HP: {self.hp}"
                    self.game_terminal.draw_dialog(use_msg)
                    self._pause_for_inventory()
                else:
                    error_msg = f"Cannot use {item.name}\n\nHP is already full!"
                    self.game_terminal.draw_dialog(error_msg)
                    self._pause_for_inventory()

    def _pause_for_inventory(self):
        """Helper to pause after showing inventory (menu hidden)."""
        self.game_terminal.clear_area(self.game_terminal.MENU_Y_START, self.game_terminal.MENU_Y_END)
        self.game_terminal.clear_area(self.game_terminal.PROMPT_INPUT_Y)

        prompt_y = self.game_terminal.PROMPT_INPUT_Y
        self.game_terminal.stdscr.addstr(prompt_y, 2, "[Press any key to close...]")
        self.game_terminal.stdscr.refresh()
        self.game_terminal.stdscr.getch()

    def update_cash(self, amount):
        self.cash += amount
        self.display_info()

    def die(self, game_stats=None) -> bool:
        """Handle player death - returns True if player wants to restart."""
        safe_print(f"\n{'='*60}")
        safe_print(f"GAME OVER - {self.name} has fallen!")
        safe_print(f"{'='*60}")

        # Show game stats if available
        if game_stats:
            safe_print(f"\nYour Journey:")
            safe_print(f"  Cows Defeated: {game_stats.cows_defeated}")
            safe_print(f"  Cows Fled From: {game_stats.cows_fled_from}")
            safe_print(f"  Cash Earned: ${game_stats.cash_earned}")
            safe_print(f"  Cash Spent: ${game_stats.cash_spent}")
            safe_print(f"  Items Purchased: {game_stats.items_purchased}")
            safe_print(f"  Items Sold: {game_stats.items_sold}")
            safe_print(f"  Dairy Cows Milked: {game_stats.dairy_cows_milked}")
            safe_print(f"  Mini-Games Won: {game_stats.mini_games_won}")
            safe_print(f"  Legendary Items Found: {game_stats.legendary_items_found}")

        safe_print(f"\nFinal Stats:")
        safe_print(f"  HP: {self.hp}")
        safe_print(f"  Cash: ${self.cash}")
        safe_print(f"  Items: {len(self.inventory)}")

        safe_print(f"\n{'='*60}")
        safe_print(f"\nWould you like to:")
        safe_print("1. Restart")
        safe_print("2. Return to Main Menu")

        choice = input("Choice (1 or 2): ").strip()
        return choice == "1"

    def update_inventory(self, item: Item, action: str) -> None:
        """Add or remove item from inventory."""
        if action == "add" and len(self.inventory) < PLAYER_MAX_INVENTORY_SIZE:
            self.inventory.append(item)
            if isinstance(item, (Weapon, Shield)) and item.is_upgrade(self, item):
                self.equip(item)
        elif action == "remove" and item in self.inventory:
            self.inventory.remove(item)
        else:
            safe_print(f"update_inventory failed to {action} {item.name}.")
    
    def check_inventory(self):
        """Display inventory with interactive item selection. Preserves and restores previous screen state."""
        saved_dialog = self.game_terminal.save_dialog_state()

        if not self.inventory:
            inventory_msg = f"{self.name}'s Inventory\n\nInventory is empty!"
            self.game_terminal.draw_dialog(inventory_msg)
            self._pause_for_inventory()
            self.game_terminal.restore_dialog_state(saved_dialog)
            return

        inventory_msg = f"{self.name}'s Inventory\n\n"

        if self.weapon:
            inventory_msg += f"Equipped Weapon: {self.weapon.name}\n"
        if self.shield:
            inventory_msg += f"Equipped Shield: {self.shield.name}\n"

        inventory_msg += f"\nItems ({len(self.inventory)}/{PLAYER_MAX_INVENTORY_SIZE}):"

        self.game_terminal.draw_dialog(inventory_msg)

        menu_items = []
        for i, item in enumerate(self.inventory):
            if isinstance(item, (Weapon, Shield)):
                menu_items.append(f"{i+1}. {item.stats()}")
            else:
                menu_items.append(f"{i+1}. {item.name}")
        menu_items.append(f"{len(self.inventory)+1}. Close inventory")

        choice = self.game_terminal.get_menu_choice(menu_items, "Select item to view/use:")

        if choice <= len(self.inventory):
            selected_item = self.inventory[choice - 1]
            self._show_item_actions(selected_item)

        self.game_terminal.restore_dialog_state(saved_dialog)

    def use_item(self, item=None):
        """Use an item from inventory."""
        if item is None:
            # Show inventory to select item
            if not self.inventory:
                safe_print("Inventory is empty!")
                return

            safe_print("\nSelect item to use:")
            for i, inv_item in enumerate(self.inventory):
                safe_print(f"{i+1}. {inv_item.name}")
            safe_print(f"{len(self.inventory)+1}. Cancel")

            try:
                choice = int(input("Choice: ").strip())
                if choice <= len(self.inventory):
                    item = self.inventory[choice - 1]
                else:
                    return
            except (ValueError, IndexError):
                safe_print("Invalid choice.")
                return

        if item in self.inventory:
            if isinstance(item, Potion):
                # Use potion
                if item.use(self):
                    self.inventory.remove(item)
                    self.display_info()
            elif isinstance(item, Tool):
                # Tools might have actions
                if hasattr(item, 'action') and item.action:
                    item.action()
                self.inventory.remove(item)
            else:
                safe_print(f"{self.name} cannot use {item.name}.")
        else:
            safe_print(f"{self.name} does not have {item.name} in their inventory.")
