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


@dataclass
class GameStateManager:
    """Manages game state for Textual UI integration."""
    player_name: str = "Player"
    player_hp: int = 20
    player_max_hp: int = 20
    player_cash: int = 50
    current_floor: int = 1
    current_cow: Optional[Dict[str, Any]] = None
    inventory: List[Dict[str, Any]] = None
    equipped_weapon: Optional[Dict[str, Any]] = None
    equipped_shield: Optional[Dict[str, Any]] = None
    in_combat: bool = False
    game_running: bool = True

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []


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
                self.state.player_cash = player_data.get('cash', 50)
                self.state.current_floor = save_data.get('floor', 1)

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
        await self.ui.push_screen("game")

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
        """Spawn a new cow."""
        cow_types = ["Normal", "Aggressive", "Defensive", "Lucky", "Boss"]
        cow_type = random.choice(cow_types)

        hp = random.randint(5, 15) * self.state.current_floor
        damage = random.randint(2, 5) * self.state.current_floor

        self.state.current_cow = {
            'name': f"{cow_type} Cow",
            'type': cow_type,
            'hp': hp,
            'max_hp': hp,
            'damage': damage,
            'mood': random.choice(['Calm', 'Angry', 'Confused', 'Happy'])
        }

        # Send event
        await self.bridge.send_event(
            GameEvent(type=EventType.COW_SPAWNED, data={'cow': self.state.current_cow})
        )

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
                # Player attacks
                damage = random.randint(3, 8)
                if self.state.equipped_weapon:
                    damage += self.state.equipped_weapon.get('damage', 0)

                cow['hp'] -= damage
                combat_log.append(f"You deal {damage} damage to the {cow['name']}!")

                if cow['hp'] <= 0:
                    # Cow defeated
                    await self.cow_defeated()
                    break

                # Cow attacks back
                cow_damage = random.randint(1, cow['damage'])
                if self.state.equipped_shield:
                    cow_damage = max(1, cow_damage - self.state.equipped_shield.get('defense', 0))

                self.state.player_hp -= cow_damage
                combat_log.append(f"The {cow['name']} deals {cow_damage} damage to you!")

            elif action.label == "Defend":
                # Reduced damage
                cow_damage = max(1, random.randint(1, cow['damage']) // 2)
                self.state.player_hp -= cow_damage
                combat_log.append(f"You defend! The {cow['name']} deals {cow_damage} damage.")

            elif action.label == "Use Item":
                # Use item (simplified)
                if self.state.inventory:
                    await self.ui.show_notification(
                        "You use a health potion and restore 10 HP!",
                        notification_type="success"
                    )
                    self.state.player_hp = min(
                        self.state.player_hp + 10,
                        self.state.player_max_hp
                    )
                else:
                    await self.ui.show_notification(
                        "No items to use!",
                        notification_type="warning"
                    )

            elif action.label == "Run":
                if random.random() > 0.5:
                    await self.ui.show_notification(
                        "You escaped!",
                        notification_type="success"
                    )
                    self.state.current_cow = None
                    break
                else:
                    cow_damage = random.randint(1, cow['damage'])
                    self.state.player_hp -= cow_damage
                    combat_log.append(f"Failed to escape! The {cow['name']} deals {cow_damage} damage!")

            # Update UI
            await self.update_ui_stats()

        self.state.in_combat = False

        # Send combat end event
        await self.bridge.send_event(
            GameEvent(type=EventType.COMBAT_ENDED)
        )

    async def cow_defeated(self) -> None:
        """Handle cow defeat."""
        if not self.state.current_cow:
            return

        cow = self.state.current_cow

        # Calculate rewards
        cash_reward = random.randint(10, 30) * self.state.current_floor
        self.state.player_cash += cash_reward

        # Random item drop
        item_drop = None
        if random.random() > 0.5:
            items = [
                {'name': 'Health Potion', 'type': 'consumable'},
                {'name': 'Rusty Sword', 'type': 'weapon', 'damage': 3},
                {'name': 'Wooden Shield', 'type': 'shield', 'defense': 2}
            ]
            item_drop = random.choice(items)
            self.state.inventory.append(item_drop)

        # Show rewards
        reward_text = f"Victory! You defeated the {cow['name']}!\n"
        reward_text += f"Gained {cash_reward} coins."
        if item_drop:
            reward_text += f"\nFound: {item_drop['name']}"

        await self.ui.show_notification(reward_text, notification_type="success")

        # Clear cow
        self.state.current_cow = None

        # Send event
        await self.bridge.send_event(
            GameEvent(type=EventType.COW_DEFEATED, data={'cow': cow})
        )

        # Check for floor advancement
        if random.random() > 0.7:  # 30% chance to advance floor
            self.state.current_floor += 1
            await self.ui.show_notification(
                f"Advanced to floor {self.state.current_floor}!",
                notification_type="success"
            )
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

        await self.ui.show_inventory(self.state.inventory, equipped)

    async def visit_shop(self) -> None:
        """Visit the shop."""
        shop_items = [
            {'name': 'Health Potion', 'price': 10, 'type': 'consumable'},
            {'name': 'Iron Sword', 'price': 50, 'type': 'weapon', 'damage': 5},
            {'name': 'Iron Shield', 'price': 40, 'type': 'shield', 'defense': 3},
            {'name': 'Cow Bell', 'price': 25, 'type': 'special'}
        ]

        result = await self.ui.show_shop(
            shop_items,
            self.state.player_cash,
            self.state.inventory
        )

        if result and result['action'] == 'buy':
            item = result['item']
            price = result['price']

            if self.state.player_cash >= price:
                self.state.player_cash -= price
                self.state.inventory.append(item)

                await self.ui.show_notification(
                    f"Purchased {item['name']} for {price} coins!",
                    notification_type="success"
                )

                # Auto-equip if weapon/shield
                if item['type'] == 'weapon':
                    self.state.equipped_weapon = item
                elif item['type'] == 'shield':
                    self.state.equipped_shield = item

                await self.update_ui_stats()

    async def save_and_quit(self) -> None:
        """Save the game and quit."""
        try:
            from save_manager import SaveManager

            save_data = {
                'player': {
                    'name': self.state.player_name,
                    'hp': self.state.player_hp,
                    'cash': self.state.player_cash
                },
                'floor': self.state.current_floor,
                'inventory': self.state.inventory
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
        """Handle game over."""
        await self.ui.push_screen('game_over', {
            'message': f"{self.state.player_name} has been defeated!",
            'score': self.state.player_cash
        })

        await self.bridge.send_event(
            GameEvent(type=EventType.GAME_OVER)
        )

        self.state.game_running = False

    async def victory(self) -> None:
        """Handle victory."""
        await self.ui.push_screen('victory', {
            'message': f"Congratulations, {self.state.player_name}! You conquered all floors!",
            'score': self.state.player_cash
        })

        await self.bridge.send_event(
            GameEvent(type=EventType.GAME_WON)
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