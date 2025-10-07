from typing import Optional, List
import random

from item import Weapon, Shield, Tool, CowBell, Bucket, Potion, roll_weapon_dmg, Item
from assets.context import small_damage_contexts, large_damage_contexts
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
        self.game_terminal.refresh()

    def equip(self, item):
        if isinstance(item, Weapon):
            self.weapon = item
        elif isinstance(item, Shield):
            self.shield = item
        else:
            safe_print(f"{item.name} is neither a weapon nor a shield and cannot be equipped.")

    def print_small_damage_context(self, cow_name, total_damage):
        from utils import safe_print
        context = random.choice(small_damage_contexts)
        context = context.format(player_name=self.name, cow_name=cow_name, total_damage=total_damage)
        safe_print(context)

    def print_large_damage_context(self, cow_name, total_damage):
        from utils import safe_print
        context = random.choice(large_damage_contexts)
        context = context.format(player_name=self.name, cow_name=cow_name, total_damage=total_damage)
        safe_print(context)

    def deal_damage(self, cow) -> None:
        """Calculate and apply damage to cow with contextual flavor text."""
        base_damage = random.randint(PLAYER_BASE_DAMAGE_MIN, PLAYER_BASE_DAMAGE_MAX) + (self.cash // PLAYER_DAMAGE_CASH_SCALING)
        weapon_damage = roll_weapon_dmg(self.weapon)
        total_damage = base_damage + weapon_damage
        total_damage = min(total_damage, cow.hp)
        cow.hp -= total_damage

        print_small_hit_context = total_damage <= cow.hp * SMALL_DAMAGE_THRESHOLD and random.random() <= SMALL_DAMAGE_CONTEXT_CHANCE
        print_large_hit_context = total_damage >= cow.hp * LARGE_DAMAGE_THRESHOLD

        if print_small_hit_context:
            self.print_small_damage_context(cow.name, total_damage)
        elif print_large_hit_context:
            self.print_large_damage_context(cow.name, total_damage)
        else:
            from utils import safe_print
            safe_print(f"{self.name} dealt {total_damage} damage to {cow.name}.")
        self.display_info()

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
        items = ', '.join(item.name for item in self.inventory) if self.inventory else "empty"
        safe_print(f"{self.name}'s inventory: {items}")

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
