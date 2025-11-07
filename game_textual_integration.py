"""
Integration module to connect the existing game logic with the Textual UI.
Provides wrapper classes and async conversion for game components.
"""

import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import random

from ui.adapters.textual_adapter import TextualAdapter
from ui.game_ui_bridge import GameUIBridge, EventType, GameEvent


class SimpleInventory:
    """Simple inventory system for items and equipment."""
    def __init__(self):
        self.items = []
        self.max_size = 20

    def add_item(self, item: Dict[str, Any]) -> bool:
        """Add an item to inventory if there's space."""
        if len(self.items) >= self.max_size:
            return False
        self.items.append(item)
        return True

    def remove_item(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Remove and return an item from inventory."""
        for i, item in enumerate(self.items):
            if item['name'] == item_name:
                return self.items.pop(i)
        return None

    def count_items(self, item_name: str) -> int:
        """Count how many of a specific item we have."""
        return sum(1 for item in self.items if item['name'] == item_name)

    def get_consumables(self) -> List[Dict[str, Any]]:
        """Get all consumable items."""
        return [item for item in self.items if item.get('type') == 'consumable']

    def get_equipment(self) -> List[Dict[str, Any]]:
        """Get all equipment items."""
        return [item for item in self.items if item.get('type') in ['weapon', 'shield']]


# Cow behavior definitions for variety and strategy
COW_BEHAVIORS = {
    'Normal': {
        'hp_mult': 1.0,
        'damage_mult': 1.0,
        'loot_mult': 1.0,
        'hit_chance': 0.8,
        'escape_difficulty': 0.5,
        'special_chance': 0.1
    },
    'Aggressive': {
        'hp_mult': 0.8,
        'damage_mult': 1.5,
        'loot_mult': 1.2,
        'hit_chance': 0.9,
        'escape_difficulty': 0.7,
        'special_chance': 0.3
    },
    'Defensive': {
        'hp_mult': 1.5,
        'damage_mult': 0.7,
        'loot_mult': 0.8,
        'hit_chance': 0.7,
        'escape_difficulty': 0.3,
        'special_chance': 0.1
    },
    'Lucky': {
        'hp_mult': 0.9,
        'damage_mult': 0.9,
        'loot_mult': 2.0,
        'hit_chance': 0.75,
        'escape_difficulty': 0.4,
        'special_chance': 0.2
    },
    'Boss': {
        'hp_mult': 3.0,
        'damage_mult': 2.0,
        'loot_mult': 5.0,
        'hit_chance': 0.95,
        'escape_difficulty': 0.9,
        'special_chance': 0.5
    }
}


@dataclass
class GameStateManager:
    """Manages game state for Textual UI integration."""
    player_name: str = "Player"
    player_hp: int = 20
    player_max_hp: int = 20
    player_cash: int = 50
    current_floor: int = 1
    current_cow: Optional[Dict[str, Any]] = None
    inventory: SimpleInventory = None
    equipped_weapon: Optional[Dict[str, Any]] = None
    equipped_shield: Optional[Dict[str, Any]] = None
    in_combat: bool = False
    game_running: bool = True
    cows_defeated: int = 0
    bosses_defeated: int = 0
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    perfect_floors: int = 0
    floor_damage_taken: int = 0
    encounters_this_floor: int = 0

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = SimpleInventory()
            # Start with 2 health potions
            self.inventory.add_item({'name': 'Health Potion', 'type': 'consumable', 'heal': 15})
            self.inventory.add_item({'name': 'Health Potion', 'type': 'consumable', 'heal': 15})


class TextualGameAdapter:
    """
    Adapter to connect game logic with Textual UI.
    Converts synchronous game logic to async UI operations.
    """

    def __init__(self):
        """Initialize the game adapter."""
        self.ui = TextualAdapter()
        self.bridge = GameUIBridge(self.ui)
        self.state = GameStateManager()
        self.running = False

    async def start(self) -> None:
        """Start the game with Textual UI."""
        try:
            # Start the bridge and UI
            await self.bridge.start()
            self.running = True

            # Show main menu
            await self.main_menu()

        except Exception as e:
            await self.ui.show_error(f"Game error: {e}", fatal=False)
            raise

        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop the game and cleanup."""
        self.running = False
        await self.bridge.stop()

    async def main_menu(self) -> None:
        """Display main menu and handle selections."""
        while self.running:
            choice = await self.ui.show_menu(
                [
                    "New Game",
                    "Continue",
                    "Career Progress",
                    "How to Play",
                    "Quit"
                ],
                title="VIRTUAL COW TIPPER - TEXTUAL EDITION"
            )

            if not choice or choice.label == "Quit":
                break

            elif choice.label == "New Game":
                await self.start_new_game()

            elif choice.label == "Continue":
                await self.continue_game()

            elif choice.label == "Career Progress":
                await self.show_career()

            elif choice.label == "How to Play":
                await self.show_help()

    async def start_new_game(self) -> None:
        """Start a new game."""
        # Get player name
        name = await self.ui.get_input(
            "Enter your name",
            default="Adventurer"
        )
        self.state.player_name = name

        # Ask about tutorial
        tutorial = await self.ui.show_menu(
            ["Yes, show tutorial", "No, skip tutorial"],
            title="First time playing?"
        )

        if tutorial and tutorial.label.startswith("Yes"):
            await self.show_tutorial()

        # Initialize game state
        self.state = GameStateManager(player_name=name)

        # Start game loop
        await self.game_loop()

    async def continue_game(self) -> None:
        """Load and continue a saved game."""
        # Check for save file
        try:
            from save_manager import SaveManager
            save_data = SaveManager.load_game()

            if save_data:
                # Load player data
                player_data = save_data.get('player', {})
                self.state.player_name = player_data.get('name', 'Player')
                self.state.player_hp = player_data.get('hp', 20)
                self.state.player_max_hp = player_data.get('max_hp', 20)
                self.state.player_cash = player_data.get('cash', 50)
                self.state.current_floor = save_data.get('floor', 1)

                # Load inventory
                saved_items = save_data.get('inventory', [])
                self.state.inventory = SimpleInventory()
                for item in saved_items:
                    self.state.inventory.add_item(item)

                # Load equipment
                self.state.equipped_weapon = save_data.get('equipped_weapon')
                self.state.equipped_shield = save_data.get('equipped_shield')

                # Load stats
                stats = save_data.get('stats', {})
                self.state.cows_defeated = stats.get('cows_defeated', 0)
                self.state.bosses_defeated = stats.get('bosses_defeated', 0)
                self.state.total_damage_dealt = stats.get('total_damage_dealt', 0)
                self.state.total_damage_taken = stats.get('total_damage_taken', 0)
                self.state.perfect_floors = stats.get('perfect_floors', 0)
                self.state.encounters_this_floor = stats.get('encounters_this_floor', 0)

                await self.ui.show_notification(
                    f"Game loaded! Welcome back, {self.state.player_name}!",
                    notification_type="success"
                )

                # Start game loop
                await self.game_loop()

            else:
                await self.ui.show_error("No save file found!", fatal=False)

        except Exception as e:
            await self.ui.show_error(f"Failed to load game: {e}", fatal=False)

    async def game_loop(self) -> None:
        """Main game loop."""
        # Don't push game screen - we use dialogue screens for interaction
        # The game screen has TODOs and isn't connected to actual logic

        # Update initial stats
        await self.update_ui_stats()

        # Game running
        self.state.game_running = True

        while self.state.game_running and self.state.player_hp > 0:
            # Spawn a cow if none present
            if not self.state.current_cow:
                await self.spawn_cow()

            # Show cow encounter options
            action = await self.ui.show_menu(
                [
                    "Approach the cow",
                    "Rest (+5 HP)",
                    "Check inventory",
                    "Visit shop",
                    "Save and quit"
                ],
                title=f"A {self.state.current_cow['type']} cow appears!"
            )

            if not action:
                continue

            # Handle action
            if action.label.startswith("Approach"):
                await self.cow_encounter()

            elif action.label.startswith("Rest"):
                await self.rest()

            elif action.label.startswith("Check inventory"):
                await self.show_inventory()

            elif action.label.startswith("Visit shop"):
                await self.visit_shop()

            elif action.label.startswith("Save"):
                await self.save_and_quit()
                break

            # Check game over conditions
            if self.state.player_hp <= 0:
                await self.game_over()
                break

            # Check victory (e.g., floor 10)
            if self.state.current_floor >= 10:
                await self.victory()
                break

    async def spawn_cow(self) -> None:
        """Spawn a new cow with scaling difficulty and behavior variety."""
        # Weighted selection based on floor
        if self.state.current_floor < 3:
            weights = [60, 20, 15, 5, 0]  # No bosses early
        elif self.state.current_floor < 7:
            weights = [40, 25, 20, 10, 5]  # Rare bosses
        else:
            weights = [30, 25, 20, 15, 10]  # More bosses late game

        cow_types = ["Normal", "Aggressive", "Defensive", "Lucky", "Boss"]
        cow_type = random.choices(cow_types, weights=weights)[0]

        # Get behavior modifiers
        behavior = COW_BEHAVIORS[cow_type]

        # Scale base stats with floor
        base_hp = 10 + (self.state.current_floor * 5)
        base_damage = 3 + (self.state.current_floor * 2)

        # Apply behavior multipliers
        hp = int(base_hp * behavior['hp_mult'])
        damage = int(base_damage * behavior['damage_mult'])

        # Generate special attacks based on type
        special_attacks = self._generate_special_attacks(cow_type)

        self.state.current_cow = {
            'name': f"{cow_type} Cow",
            'type': cow_type,
            'hp': hp,
            'max_hp': hp,
            'damage': damage,
            'mood': random.choice(['Calm', 'Angry', 'Confused', 'Happy']),
            'behavior': behavior,
            'special_attacks': special_attacks,
            'defense': max(0, self.state.current_floor - 1),  # Cows get tougher
            'enraged': False  # Becomes true at low HP
        }

        # Send event
        await self.bridge.send_event(
            GameEvent(type=EventType.COW_SPAWNED, data={'cow': self.state.current_cow})
        )

    def _generate_special_attacks(self, cow_type: str) -> List[Dict[str, Any]]:
        """Generate special attacks based on cow type."""
        attacks = {
            'Normal': [
                {'name': 'Headbutt', 'damage_mult': 1.0, 'message': 'charges forward!'},
                {'name': 'Kick', 'damage_mult': 0.8, 'message': 'kicks wildly!'}
            ],
            'Aggressive': [
                {'name': 'Rampage', 'damage_mult': 1.5, 'message': 'goes on a rampage!'},
                {'name': 'Gore', 'damage_mult': 1.3, 'message': 'attempts to gore you!'},
                {'name': 'Trample', 'damage_mult': 1.2, 'message': 'tries to trample you!'}
            ],
            'Defensive': [
                {'name': 'Block', 'damage_mult': 0.5, 'message': 'blocks and counters!'},
                {'name': 'Fortify', 'damage_mult': 0.3, 'message': 'fortifies its position!'}
            ],
            'Lucky': [
                {'name': 'Lucky Strike', 'damage_mult': 2.0, 'message': 'lands a lucky hit!'},
                {'name': 'Dodge', 'damage_mult': 0.0, 'message': 'dodges gracefully!'}
            ],
            'Boss': [
                {'name': 'Earthquake Stomp', 'damage_mult': 2.0, 'message': 'shakes the ground!'},
                {'name': 'Mighty Roar', 'damage_mult': 1.5, 'message': 'roars intimidatingly!'},
                {'name': 'Charge', 'damage_mult': 1.8, 'message': 'charges with full force!'}
            ]
        }
        return attacks.get(cow_type, attacks['Normal'])

    async def cow_encounter(self) -> None:
        """Handle cow encounter."""
        if not self.state.current_cow:
            return

        # Show dialogue
        cow_name = self.state.current_cow['name']
        mood = self.state.current_cow['mood']

        dialogue_text = f"The {cow_name} looks {mood.lower()}. What will you do?"

        choice = await self.ui.show_dialogue(
            cow_name,
            dialogue_text,
            ["Tip the cow", "Try to pet it", "Back away slowly"]
        )

        if choice == 0:  # Tip the cow
            await self.combat()

        elif choice == 1:  # Pet it
            if mood == "Happy":
                await self.ui.show_notification(
                    "The cow enjoys the petting! It gives you 10 coins.",
                    notification_type="success"
                )
                self.state.player_cash += 10
                self.state.current_cow = None
            else:
                await self.ui.show_notification(
                    "The cow doesn't like that! Combat begins!",
                    notification_type="warning"
                )
                await self.combat()

        else:  # Back away
            await self.ui.show_notification(
                "You back away. The cow wanders off.",
                notification_type="info"
            )
            self.state.current_cow = None

        await self.update_ui_stats()

    async def combat(self) -> None:
        """Handle combat with current cow."""
        if not self.state.current_cow:
            return

        self.state.in_combat = True
        cow = self.state.current_cow
        combat_log = []

        # Send combat start event
        await self.bridge.send_event(
            GameEvent(type=EventType.COMBAT_STARTED, data={'cow': cow})
        )

        while self.state.player_hp > 0 and cow['hp'] > 0:
            # Show combat state
            await self.ui.show_combat(
                (self.state.player_hp, self.state.player_max_hp),
                (cow['hp'], cow['max_hp']),
                combat_log
            )

            # Player action
            action = await self.ui.show_menu(
                ["Attack", "Defend", "Use Item", "Run"],
                title="Combat Actions"
            )

            if not action:
                continue

            if action.label == "Attack":
                # Calculate hit chance
                player_hit_chance = 0.85  # Base hit chance
                if self.state.equipped_weapon and 'accuracy' in self.state.equipped_weapon:
                    player_hit_chance += self.state.equipped_weapon['accuracy']

                if random.random() < player_hit_chance:
                    # Calculate damage with scaling
                    base_damage = random.randint(5, 10) + (self.state.current_floor * 2)

                    # Add weapon damage
                    if self.state.equipped_weapon:
                        base_damage += self.state.equipped_weapon.get('damage', 0)

                    # Apply cow defense
                    damage = max(1, base_damage - cow.get('defense', 0))

                    # Check for critical hit
                    crit_chance = 0.1  # 10% base crit chance
                    if random.random() < crit_chance:
                        damage = int(damage * 2)
                        combat_log.append(f"⚡ CRITICAL HIT! You deal {damage} damage!")
                    else:
                        combat_log.append(f"You deal {damage} damage to the {cow['name']}!")

                    cow['hp'] -= damage
                    self.state.total_damage_dealt += damage

                    # Check for cow enrage at low HP
                    if cow['hp'] < cow['max_hp'] * 0.3 and not cow.get('enraged'):
                        cow['enraged'] = True
                        combat_log.append(f"💢 The {cow['name']} becomes enraged!")
                else:
                    combat_log.append("Your attack misses!")

                if cow['hp'] <= 0:
                    # Cow defeated
                    await self.cow_defeated()
                    break

                # Cow retaliation with special attacks
                await self._cow_attack(cow, combat_log)

            elif action.label == "Defend":
                # Defensive stance reduces damage significantly
                await self._cow_attack(cow, combat_log, defending=True)

            elif action.label == "Use Item":
                # Show consumable items
                consumables = self.state.inventory.get_consumables()
                if consumables:
                    # For now, auto-use health potion if available
                    potion = None
                    for item in consumables:
                        if 'Health Potion' in item['name']:
                            potion = item
                            break

                    if potion:
                        # Use the potion
                        heal_amount = potion.get('heal', 15)
                        old_hp = self.state.player_hp
                        self.state.player_hp = min(
                            self.state.player_hp + heal_amount,
                            self.state.player_max_hp
                        )
                        actual_heal = self.state.player_hp - old_hp

                        # Remove from inventory
                        self.state.inventory.remove_item(potion['name'])

                        combat_log.append(f"💚 Used {potion['name']}! Restored {actual_heal} HP!")
                        await self.ui.show_notification(
                            f"Restored {actual_heal} HP!",
                            notification_type="success"
                        )
                    else:
                        combat_log.append("No health potions available!")
                        await self.ui.show_notification(
                            "No health potions!",
                            notification_type="warning"
                        )
                else:
                    combat_log.append("No items to use!")
                    await self.ui.show_notification(
                        "No items to use!",
                        notification_type="warning"
                    )

            elif action.label == "Run":
                # Use cow's escape difficulty
                escape_difficulty = cow.get('behavior', {}).get('escape_difficulty', 0.5)
                if random.random() > escape_difficulty:
                    await self.ui.show_notification(
                        "You escaped successfully!",
                        notification_type="success"
                    )
                    self.state.current_cow = None
                    break
                else:
                    combat_log.append(f"Failed to escape from the {cow['name']}!")
                    await self._cow_attack(cow, combat_log, fleeing=True)

            # Update UI
            await self.update_ui_stats()

        self.state.in_combat = False

        # Send combat end event
        await self.bridge.send_event(
            GameEvent(type=EventType.COMBAT_ENDED)
        )

    async def _cow_attack(self, cow: Dict[str, Any], combat_log: List[str],
                          defending: bool = False, fleeing: bool = False) -> None:
        """Handle cow attack with special moves and modifiers."""
        # Check if cow hits
        cow_hit_chance = cow.get('behavior', {}).get('hit_chance', 0.8)
        if cow.get('enraged'):
            cow_hit_chance = min(0.95, cow_hit_chance + 0.15)  # Enraged cows hit more

        if random.random() > cow_hit_chance:
            combat_log.append(f"The {cow['name']} misses its attack!")
            return

        # Choose attack type
        use_special = random.random() < cow.get('behavior', {}).get('special_chance', 0.1)
        if use_special and cow.get('special_attacks'):
            # Use special attack
            attack = random.choice(cow['special_attacks'])
            base_damage = cow['damage']
            damage = int(base_damage * attack['damage_mult'])

            if cow.get('enraged'):
                damage = int(damage * 1.3)  # Enraged bonus

            message = f"The {cow['name']} {attack['message']}"
        else:
            # Normal attack
            damage = random.randint(
                max(1, cow['damage'] - 2),
                cow['damage'] + 2
            )
            if cow.get('enraged'):
                damage = int(damage * 1.3)
            message = f"The {cow['name']} attacks!"

        # Apply modifiers
        if defending:
            damage = max(1, damage // 3)  # Heavy reduction when defending
            message += " (Blocked!)"
        elif fleeing:
            damage = int(damage * 1.5)  # Extra damage when fleeing
            message += " (Attacks your back!)"

        # Apply shield defense
        if self.state.equipped_shield:
            shield_def = self.state.equipped_shield.get('defense', 0)
            damage = max(1, damage - shield_def)

        # Apply damage
        self.state.player_hp -= damage
        self.state.total_damage_taken += damage
        self.state.floor_damage_taken += damage

        combat_log.append(f"{message} Deals {damage} damage!")

        # Check for stun or other effects
        if use_special and attack.get('name') == 'Earthquake Stomp':
            combat_log.append("You're stunned by the impact!")

    async def cow_defeated(self) -> None:
        """Handle cow defeat with scaled rewards."""
        if not self.state.current_cow:
            return

        cow = self.state.current_cow
        self.state.cows_defeated += 1
        self.state.encounters_this_floor += 1

        # Track boss defeats
        if cow['type'] == 'Boss':
            self.state.bosses_defeated += 1

        # Calculate cash rewards with loot multiplier
        base_cash = random.randint(10, 20) + (self.state.current_floor * 5)
        loot_mult = cow.get('behavior', {}).get('loot_mult', 1.0)
        cash_reward = int(base_cash * loot_mult)
        self.state.player_cash += cash_reward

        # Generate loot drops
        items_found = []

        # Calculate drop chance based on cow type and floor
        drop_chance = 0.3 + (self.state.current_floor * 0.05)  # Higher floors = better drops
        if cow['type'] == 'Boss':
            drop_chance = 1.0  # Bosses always drop something
        elif cow['type'] == 'Lucky':
            drop_chance = 0.8  # Lucky cows drop more

        if random.random() < drop_chance:
            item = self._generate_loot(cow['type'], self.state.current_floor)
            if self.state.inventory.add_item(item):
                items_found.append(item['name'])
            else:
                # Inventory full, convert to cash
                cash_reward += item.get('value', 10)
                items_found.append(f"Inventory full! Sold {item['name']} for {item.get('value', 10)} coins")

        # Chance for bonus potion
        if random.random() < 0.2:
            potion = {'name': 'Health Potion', 'type': 'consumable', 'heal': 15 + self.state.current_floor}
            if self.state.inventory.add_item(potion):
                items_found.append('Health Potion')

        # Show rewards
        reward_text = f"Victory! You defeated the {cow['name']}!\n"
        reward_text += f"💰 Gained {cash_reward} coins"
        if items_found:
            reward_text += f"\n📦 Found: {', '.join(items_found)}"

        await self.ui.show_notification(reward_text, notification_type="success")

        # Clear cow
        self.state.current_cow = None

        # Send event
        await self.bridge.send_event(
            GameEvent(type=EventType.COW_DEFEATED, data={'cow': cow})
        )

        # Check for floor advancement
        if self.state.encounters_this_floor >= 3:  # Advance after 3 encounters
            await self.advance_floor()

    def _generate_loot(self, cow_type: str, floor: int) -> Dict[str, Any]:
        """Generate loot based on cow type and floor."""
        # Define loot tables
        if floor <= 3:
            # Early game items
            weapons = [
                {'name': 'Rusty Sword', 'damage': 3, 'value': 20},
                {'name': 'Wooden Club', 'damage': 2, 'value': 15},
                {'name': 'Sharp Stick', 'damage': 4, 'value': 25}
            ]
            shields = [
                {'name': 'Wooden Shield', 'defense': 2, 'value': 20},
                {'name': 'Pot Lid', 'defense': 1, 'value': 10}
            ]
        elif floor <= 7:
            # Mid game items
            weapons = [
                {'name': 'Iron Sword', 'damage': 6, 'value': 50},
                {'name': 'Battle Axe', 'damage': 8, 'value': 70},
                {'name': 'Mace', 'damage': 7, 'value': 60}
            ]
            shields = [
                {'name': 'Iron Shield', 'defense': 4, 'value': 50},
                {'name': 'Round Shield', 'defense': 3, 'value': 40}
            ]
        else:
            # Late game items
            weapons = [
                {'name': 'Steel Sword', 'damage': 10, 'value': 100},
                {'name': 'War Hammer', 'damage': 12, 'value': 120},
                {'name': 'Enchanted Blade', 'damage': 15, 'value': 200}
            ]
            shields = [
                {'name': 'Steel Shield', 'defense': 6, 'value': 100},
                {'name': 'Tower Shield', 'defense': 8, 'value': 150}
            ]

        # Boss drops are always good
        if cow_type == 'Boss':
            if random.random() < 0.7:
                item = random.choice(weapons)
                item['type'] = 'weapon'
            else:
                item = random.choice(shields)
                item['type'] = 'shield'
            # Boss items get bonus stats
            if 'damage' in item:
                item['damage'] = int(item['damage'] * 1.2)
            if 'defense' in item:
                item['defense'] = int(item['defense'] * 1.2)
            item['name'] = f"Superior {item['name']}"
            item['value'] = int(item['value'] * 1.5)
        else:
            # Regular drops
            if random.random() < 0.6:
                item = random.choice(weapons)
                item['type'] = 'weapon'
            else:
                item = random.choice(shields)
                item['type'] = 'shield'

        return item

    async def advance_floor(self) -> None:
        """Advance to the next floor with bonuses."""
        self.state.current_floor += 1
        self.state.encounters_this_floor = 0

        # Check for perfect floor (no damage taken)
        if self.state.floor_damage_taken == 0:
            self.state.perfect_floors += 1
            bonus_cash = 50 * self.state.current_floor
            self.state.player_cash += bonus_cash
            await self.ui.show_notification(
                f"🌟 Perfect Floor! No damage taken! Bonus: {bonus_cash} coins!",
                notification_type="success"
            )

        # Reset floor damage tracking
        self.state.floor_damage_taken = 0

        # Heal player slightly
        heal_amount = min(5, self.state.player_max_hp - self.state.player_hp)
        self.state.player_hp += heal_amount

        await self.ui.show_notification(
            f"📈 Advanced to Floor {self.state.current_floor}! Healed {heal_amount} HP",
            notification_type="success"
        )

        # Every 3 floors, offer a shop
        if self.state.current_floor % 3 == 0:
            await self.ui.show_notification(
                "🏪 A traveling merchant appears!",
                notification_type="info"
            )
            await self.visit_shop()

        await self.bridge.send_event(
            GameEvent(type=EventType.FLOOR_CHANGED, data={'floor': self.state.current_floor})
        )

    async def rest(self) -> None:
        """Rest to restore HP."""
        old_hp = self.state.player_hp
        self.state.player_hp = min(
            self.state.player_hp + 5,
            self.state.player_max_hp
        )
        healed = self.state.player_hp - old_hp

        await self.ui.show_notification(
            f"You rest and recover {healed} HP.",
            notification_type="success"
        )

        # Cow wanders off
        if self.state.current_cow:
            self.state.current_cow = None
            await self.ui.show_notification(
                "The cow wanders away while you rest.",
                notification_type="info"
            )

        await self.update_ui_stats()

    async def show_inventory(self) -> None:
        """Show inventory screen."""
        equipped = {
            'weapon': self.state.equipped_weapon,
            'shield': self.state.equipped_shield
        }

        # Convert inventory items for display
        inventory_data = self.state.inventory.items if self.state.inventory else []

        await self.ui.show_inventory(inventory_data, equipped)

    async def visit_shop(self) -> None:
        """Visit the shop with scaled items."""
        # Generate shop items based on floor
        shop_items = self._generate_shop_items()

        # Show items in a menu
        item_descriptions = []
        for item in shop_items:
            desc = f"{item['name']} - {item['price']} coins"
            if item['type'] == 'weapon':
                desc += f" (Damage: +{item['damage']})"
            elif item['type'] == 'shield':
                desc += f" (Defense: +{item['defense']})"
            elif item['type'] == 'consumable':
                desc += f" (Heals: {item.get('heal', '?')} HP)"
            item_descriptions.append(desc)

        item_descriptions.append("Leave shop")

        while True:
            choice = await self.ui.show_menu(
                item_descriptions,
                title=f"🏪 Shop (You have {self.state.player_cash} coins)"
            )

            if not choice or choice.label == "Leave shop":
                break

            # Find selected item
            selected_index = item_descriptions.index(choice.label)
            if selected_index < len(shop_items):
                item = shop_items[selected_index]

                if self.state.player_cash >= item['price']:
                    # Check inventory space
                    if not self.state.inventory.add_item(item):
                        await self.ui.show_notification(
                            "Inventory full! Can't buy item.",
                            notification_type="warning"
                        )
                        continue

                    self.state.player_cash -= item['price']

                    await self.ui.show_notification(
                        f"✅ Purchased {item['name']} for {item['price']} coins!",
                        notification_type="success"
                    )

                    # Ask to equip if weapon/shield
                    if item['type'] in ['weapon', 'shield']:
                        equip_choice = await self.ui.show_menu(
                            ["Yes", "No"],
                            title=f"Equip {item['name']} now?"
                        )
                        if equip_choice and equip_choice.label == "Yes":
                            if item['type'] == 'weapon':
                                self.state.equipped_weapon = item
                                await self.ui.show_notification(
                                    f"⚔️ Equipped {item['name']}!",
                                    notification_type="success"
                                )
                            elif item['type'] == 'shield':
                                self.state.equipped_shield = item
                                await self.ui.show_notification(
                                    f"🛡️ Equipped {item['name']}!",
                                    notification_type="success"
                                )
                else:
                    await self.ui.show_notification(
                        f"Not enough coins! Need {item['price']}, have {self.state.player_cash}",
                        notification_type="warning"
                    )

        await self.update_ui_stats()

    def _generate_shop_items(self) -> List[Dict[str, Any]]:
        """Generate shop items based on current floor."""
        items = []

        # Always have health potions
        potion_price = 10 + (self.state.current_floor * 2)
        items.append({
            'name': 'Health Potion',
            'type': 'consumable',
            'heal': 15 + self.state.current_floor,
            'price': potion_price,
            'value': potion_price
        })

        # Add mega potion on higher floors
        if self.state.current_floor >= 5:
            items.append({
                'name': 'Mega Potion',
                'type': 'consumable',
                'heal': 30 + (self.state.current_floor * 2),
                'price': potion_price * 3,
                'value': potion_price * 3
            })

        # Generate weapons based on floor
        if self.state.current_floor <= 3:
            weapons = [
                {'name': 'Iron Sword', 'damage': 5, 'price': 50},
                {'name': 'Battle Axe', 'damage': 6, 'price': 60}
            ]
        elif self.state.current_floor <= 7:
            weapons = [
                {'name': 'Steel Sword', 'damage': 8, 'price': 100},
                {'name': 'War Hammer', 'damage': 10, 'price': 120}
            ]
        else:
            weapons = [
                {'name': 'Mystic Blade', 'damage': 12, 'price': 200},
                {'name': 'Dragon Slayer', 'damage': 15, 'price': 300}
            ]

        for weapon in weapons:
            weapon['type'] = 'weapon'
            weapon['value'] = weapon['price'] // 2
            items.append(weapon)

        # Generate shields
        if self.state.current_floor <= 3:
            shields = [
                {'name': 'Iron Shield', 'defense': 3, 'price': 40}
            ]
        elif self.state.current_floor <= 7:
            shields = [
                {'name': 'Steel Shield', 'defense': 5, 'price': 80}
            ]
        else:
            shields = [
                {'name': 'Dragon Scale Shield', 'defense': 8, 'price': 150}
            ]

        for shield in shields:
            shield['type'] = 'shield'
            shield['value'] = shield['price'] // 2
            items.append(shield)

        # Special items on higher floors
        if self.state.current_floor >= 4:
            items.append({
                'name': 'Lucky Charm',
                'type': 'consumable',
                'price': 100,
                'value': 50,
                'effect': 'double_loot'
            })

        return items

    async def save_and_quit(self) -> None:
        """Save the game and quit."""
        try:
            from save_manager import SaveManager

            save_data = {
                'player': {
                    'name': self.state.player_name,
                    'hp': self.state.player_hp,
                    'max_hp': self.state.player_max_hp,
                    'cash': self.state.player_cash
                },
                'floor': self.state.current_floor,
                'inventory': self.state.inventory.items if self.state.inventory else [],
                'equipped_weapon': self.state.equipped_weapon,
                'equipped_shield': self.state.equipped_shield,
                'stats': {
                    'cows_defeated': self.state.cows_defeated,
                    'bosses_defeated': self.state.bosses_defeated,
                    'total_damage_dealt': self.state.total_damage_dealt,
                    'total_damage_taken': self.state.total_damage_taken,
                    'perfect_floors': self.state.perfect_floors,
                    'encounters_this_floor': self.state.encounters_this_floor
                }
            }

            SaveManager.save_game(save_data)

            await self.ui.show_notification(
                "Game saved successfully!",
                notification_type="success"
            )

        except Exception as e:
            await self.ui.show_error(f"Failed to save: {e}", fatal=False)

        self.state.game_running = False

    async def game_over(self) -> None:
        """Handle game over with detailed stats."""
        # Calculate final score
        final_score = (
            self.state.player_cash +
            (self.state.cows_defeated * 10) +
            (self.state.current_floor * 50) +
            (self.state.perfect_floors * 100)
        )

        # Save to career stats
        await self._update_career_stats(final_score, won=False)

        # Create detailed message
        message = f"""
💀 {self.state.player_name} has been defeated on Floor {self.state.current_floor}!

📊 Final Statistics:
• Cows Defeated: {self.state.cows_defeated}
• Bosses Defeated: {self.state.bosses_defeated}
• Floors Cleared: {self.state.current_floor - 1}
• Perfect Floors: {self.state.perfect_floors}
• Total Damage Dealt: {self.state.total_damage_dealt}
• Total Damage Taken: {self.state.total_damage_taken}
• Cash Collected: ${self.state.player_cash}

🏆 Final Score: {final_score}
"""

        await self.ui.push_screen('game_over', {
            'message': message,
            'score': final_score
        })

        await self.bridge.send_event(
            GameEvent(type=EventType.GAME_OVER, data={'score': final_score})
        )

        self.state.game_running = False

    async def victory(self) -> None:
        """Handle victory with detailed stats."""
        # Calculate victory bonus
        victory_bonus = 1000
        if self.state.current_floor >= 15:
            victory_bonus = 2000  # Extra for going beyond floor 10

        final_score = (
            self.state.player_cash +
            (self.state.cows_defeated * 10) +
            (self.state.current_floor * 50) +
            (self.state.perfect_floors * 100) +
            victory_bonus
        )

        # Save to career stats
        await self._update_career_stats(final_score, won=True)

        # Check for special victories
        victory_type = "Victory"
        if self.state.bosses_defeated >= 5:
            victory_type = "Boss Slayer Victory"
        elif self.state.perfect_floors >= 5:
            victory_type = "Flawless Victory"
        elif self.state.current_floor >= 15:
            victory_type = "Legendary Victory"

        message = f"""
🎉 {victory_type}!
{self.state.player_name} has conquered the cow fields!

📊 Final Statistics:
• Cows Defeated: {self.state.cows_defeated}
• Bosses Defeated: {self.state.bosses_defeated}
• Final Floor: {self.state.current_floor}
• Perfect Floors: {self.state.perfect_floors}
• Total Damage Dealt: {self.state.total_damage_dealt}
• Total Damage Taken: {self.state.total_damage_taken}
• Cash Collected: ${self.state.player_cash}
• Victory Bonus: {victory_bonus}

🏆 Final Score: {final_score}

{'⭐ New High Score!' if await self._is_high_score(final_score) else ''}
"""

        await self.ui.push_screen('victory', {
            'message': message,
            'score': final_score
        })

        await self.bridge.send_event(
            GameEvent(type=EventType.GAME_WON, data={'score': final_score, 'type': victory_type})
        )

        self.state.game_running = False

    async def show_career(self) -> None:
        """Show career progress."""
        try:
            from career_stats import CareerStats
            career = CareerStats.load()

            stats_text = f"""
=== CAREER PROGRESS ===

Total Runs: {career.total_runs}
Best Score: {career.best_score}
Total Cows Defeated: {career.total_cows_defeated}
Total Cash Earned: ${career.total_cash_earned}
Highest Floor: {career.highest_floor}

Unlocks: {len(career.unlocks)} achievements
"""
            await self.ui.show_text(stats_text)

        except Exception as e:
            await self.ui.show_error(f"Failed to load career stats: {e}", fatal=False)

    async def show_help(self) -> None:
        """Show help/tutorial."""
        help_text = """
=== HOW TO PLAY VIRTUAL COW TIPPER ===

OBJECTIVE:
Navigate through floors of aggressive cows, collecting loot and growing stronger!

GAMEPLAY:
1. Each floor has cows to encounter
2. Choose to approach, rest, or check inventory
3. Combat: Attack, defend, use items, or flee
4. Defeated cows drop cash and items
5. Visit shops to buy better equipment
6. Reach higher floors for greater challenges

TIPS:
- Rest when low on HP
- Save your game frequently
- Equip weapons and shields for combat
- Some cows have special moods

Good luck, cow tipper!
"""
        await self.ui.show_text(help_text)

    async def show_tutorial(self) -> None:
        """Show tutorial for new players."""
        await self.ui.show_text(
            """
Welcome to Virtual Cow Tipper!

You're about to embark on a journey through floors
filled with increasingly aggressive cows.

Your goal: Tip cows, collect loot, and survive!

Each cow has different moods and behaviors.
Some might be friendly, others... not so much.

Let's begin your adventure!
""",
            style="info"
        )

    async def update_ui_stats(self) -> None:
        """Update UI with current stats."""
        player_stats = {
            'hp': self.state.player_hp,
            'max_hp': self.state.player_max_hp,
            'cash': self.state.player_cash,
            'floor': self.state.current_floor,
            'weapon': self.state.equipped_weapon['name'] if self.state.equipped_weapon else None,
            'shield': self.state.equipped_shield['name'] if self.state.equipped_shield else None
        }

        cow_stats = None
        if self.state.current_cow:
            cow_stats = {
                'name': self.state.current_cow['name'],
                'hp': (self.state.current_cow['hp'], self.state.current_cow['max_hp']),
                'type': self.state.current_cow['type'],
                'mood': self.state.current_cow['mood']
            }

        await self.ui.update_stats(player_stats, cow_stats)

    async def _update_career_stats(self, score: int, won: bool) -> None:
        """Update career statistics after game end."""
        try:
            from career_stats import CareerStats
            career = CareerStats.load()

            # Update stats
            career.total_runs += 1
            if won:
                career.total_wins += 1
            career.total_cows_defeated += self.state.cows_defeated
            career.total_cash_earned += self.state.player_cash

            if score > career.best_score:
                career.best_score = score

            if self.state.current_floor > career.highest_floor:
                career.highest_floor = self.state.current_floor

            # Check for new unlocks
            if self.state.bosses_defeated >= 10 and 'boss_slayer' not in career.unlocks:
                career.unlocks.append('boss_slayer')
                await self.ui.show_notification(
                    "🏅 Achievement Unlocked: Boss Slayer!",
                    notification_type="success"
                )

            if self.state.perfect_floors >= 3 and 'untouchable' not in career.unlocks:
                career.unlocks.append('untouchable')
                await self.ui.show_notification(
                    "🏅 Achievement Unlocked: Untouchable!",
                    notification_type="success"
                )

            if self.state.current_floor >= 15 and 'floor_master' not in career.unlocks:
                career.unlocks.append('floor_master')
                await self.ui.show_notification(
                    "🏅 Achievement Unlocked: Floor Master!",
                    notification_type="success"
                )

            career.save()
        except Exception as e:
            # Don't fail the game over this
            print(f"Failed to update career stats: {e}")

    async def _is_high_score(self, score: int) -> bool:
        """Check if this is a new high score."""
        try:
            from career_stats import CareerStats
            career = CareerStats.load()
            return score > career.best_score
        except:
            return True  # First game is always a high score


async def main():
    """Main entry point for Textual game."""
    game = TextualGameAdapter()

    try:
        await game.start()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())