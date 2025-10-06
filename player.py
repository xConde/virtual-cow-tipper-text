from typing import Optional, List
import random

from item import Weapon, Shield, Tool, CowBell, Bucket, roll_weapon_dmg, Item
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
            print(f"{item.name} is neither a weapon nor a shield and cannot be equipped.")

    def print_small_damage_context(self, cow_name, total_damage):
        context = random.choice(small_damage_contexts)
        context = context.format(player_name=self.name, cow_name=cow_name, total_damage=total_damage)
        print(context)

    def print_large_damage_context(self, cow_name, total_damage):
        context = random.choice(large_damage_contexts)
        context = context.format(player_name=self.name, cow_name=cow_name, total_damage=total_damage)
        print(context)

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
            print(f"{self.name} dealt {total_damage} damage to {cow.name}.")
        self.display_info()

    def update_cash(self, amount):
        self.cash += amount
        self.display_info()

    def die(self):
        print(f"{self.name} has died.")
        # Logic for handling player death, such as resetting stats, can be added here.

    def update_inventory(self, item: Item, action: str) -> None:
        """Add or remove item from inventory."""
        if action == "add" and len(self.inventory) < PLAYER_MAX_INVENTORY_SIZE:
            self.inventory.append(item)
            if isinstance(item, (Weapon, Shield)) and item.is_upgrade(self, item):
                self.equip(item)
        elif action == "remove" and item in self.inventory:
            self.inventory.remove(item)
        else:
            print(f"update_inventory failed to {action} {item.name}.")
    
    def check_inventory(self):
        items = ', '.join(item.name for item in self.inventory) if self.inventory else "empty"
        print(f"{self.name}'s inventory: {items}")

    def use_item(self, item):
        if item in self.inventory:
            if isinstance(item, Tool):
                item.action()
                self.remove_item_from_inventory(item)
            else:
                print(f"{self.name} cannot use {item.name}.")
        else:
            print(f"{self.name} does not have {item.name} in their inventory.")
