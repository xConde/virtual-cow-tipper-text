from typing import Optional, List
import random

from cow import Cow
from player import Player
from item import Item, CowBell
from cow_interaction import CowInteraction
from terminal.game_terminal import GameTerminal
from dialogue_manager import DialogueManager
from models import GameStats
from save_manager import SaveManager
from career_stats import CareerStats, Unlock
from game_config import (
    COW_QUEUE_SIZE,
    NUM_COW_PACKS,
    INTERRUPTION_CHANCE,
)

class VirtualCowTipper:
    def __init__(self, player_name: str, show_tutorial: bool = True, load_save: bool = False):
        self.game_terminal = GameTerminal()
        self.career_stats = CareerStats.load()  # Load career progression

        # Apply career bonuses to starting stats
        bonuses = self.career_stats.get_starting_bonuses()

        self.player = Player(
            self.game_terminal,
            player_name,
            starting_hp=20 + bonuses['extra_hp'],
            starting_cash=50 + bonuses['extra_cash']
        )

        # Apply starting items from unlocks
        for item_id in bonuses['starting_items']:
            if item_id == 'cowbell':
                self.player.inventory.append(CowBell())
                print(f"[UNLOCK BONUS] {player_name} starts with a Cow Bell!")
            elif item_id == 'basic_weapon':
                from item_factory import ItemFactory
                weapon = ItemFactory.create_weapon(less_likely=True)  # Common weapon
                self.player.weapon = weapon
                print(f"[UNLOCK BONUS] {player_name} starts with {weapon.name}!")

        self.cow: Optional[Cow] = None
        self.cows = [self.generate_cow() for _ in range(COW_QUEUE_SIZE)]
        self.cow_packs = {pack: 0.0 for pack in range(1, NUM_COW_PACKS + 1)}
        self.stats = GameStats()
        self.running = True
        self.first_encounter = show_tutorial
        self.tutorial_shown = not show_tutorial
        self.career_bonuses = bonuses  # Store for use throughout game

        # Load saved game if requested
        if load_save:
            self._load_saved_game()

    def start(self) -> None:
        """Main game loop."""
        while self.running:
            self.game_terminal.clear_screen()
            self.game_terminal.refresh()
            self.player.display_info()
            self.player_turn()
            self.check_end_conditions()
            self.check_victory_conditions()

    def generate_cow(self) -> Cow:
        """Generate a new random cow scaled to player progression."""
        properties = Cow.generate_random_cow_properties(self.player)
        return Cow(self.game_terminal, properties)

    def spawn_cow(self):
        if not self.cow:
            cow = self.cows.pop(0)
            pack_score = self.cow_packs[cow.pack]
            cow.likeliness += pack_score
            self.cow = cow
            self.cows.append(self.generate_cow())

    def destroy_cow(self):
        self.game_terminal.set_cow_stats('')
        self.cow = None

    def update_cow_scores(self, defeated_cow: Cow, score: float):
        """Update pack reputation and queued cow likeliness based on interaction outcome."""
        self.cow_packs[defeated_cow.pack] += score
        for queued_cow in self.cows:
            queued_cow.likeliness += score
        self.destroy_cow()

    def player_turn(self):
        if not self.cow:
            self.spawn_cow()

            # Show tutorial tip before first encounter
            if self.first_encounter:
                from tutorial import show_first_encounter_tip
                self.game_terminal.close_game_terminal()
                show_first_encounter_tip()
                self.game_terminal = GameTerminal()  # Reinitialize
                self.first_encounter = False

        self.cow.get_approach()

        is_interrupted = self.get_interruption()
        if is_interrupted:
            CowInteraction(self, self.player, self.cow).interact()
            return

        actions = {
            "approach the cow": lambda: CowInteraction(self, self.player, self.cow).interact(),
            "rest": self._rest,
            "check inventory": lambda: self.player.check_inventory(),
            "use an item from inventory": self.player.use_item,
            "save and quit": self.quit_with_save,
        }

    def _rest(self) -> None:
        """Rest to recover HP (skip cow encounter)."""
        from game_config import REST_HEAL_AMOUNT, PLAYER_MAX_HP

        old_hp = self.player.hp
        self.player.hp = min(self.player.hp + REST_HEAL_AMOUNT, PLAYER_MAX_HP)
        healed = self.player.hp - old_hp

        print(f"\n{self.player.name} rests and recovers {healed} HP.")
        print(f"Current HP: {self.player.hp}/{PLAYER_MAX_HP}")
        print("The cow wanders off while you rest...")

        # Skip this cow, generate new one
        self.destroy_cow()
        input("\nPress Enter to continue...")
        while True:
            menu_items = [f"{i+1}. {action.capitalize()}" for i, action in enumerate(actions.keys())]
            choice = self.game_terminal.get_menu_choice(menu_items)
            if choice in range(1, len(actions.keys())+1):
                action_name = list(actions.keys())[int(choice) - 1]
                try:
                    actions[action_name](self.cow)
                except TypeError:
                    actions[action_name]()
                return
    
    def get_interruption(self) -> Optional[str]:
        """Check for random interruption event (10% chance)."""
        if random.random() < INTERRUPTION_CHANCE:
            message = DialogueManager.get_interruption()
            self.game_terminal.draw_dialog(message)
            return message
        return None

    def check_end_conditions(self) -> None:
        """Check if game is over and handle restart."""
        if self.player.hp <= 0 or self.player.cash <= 0:
            # Update career stats
            self.career_stats.add_run_stats(self.stats, victory=False)
            newly_unlocked = self.career_stats.check_unlocks()
            self.career_stats.save()

            # Show unlocks if any
            if newly_unlocked:
                self._show_new_unlocks(newly_unlocked)

            should_restart = self.player.die(self.stats)
            if should_restart:
                self._restart_game()
            else:
                self.game_terminal.close_game_terminal()
                self.running = False

    def check_victory_conditions(self) -> None:
        """Check if player has won the game."""
        if self.stats.check_victory():
            # Update career stats with victory
            self.career_stats.add_run_stats(self.stats, victory=True)
            newly_unlocked = self.career_stats.check_unlocks()
            self.career_stats.save()

            self._show_victory_screen()

            # Show unlocks after victory
            if newly_unlocked:
                self._show_new_unlocks(newly_unlocked)

            self.game_terminal.close_game_terminal()
            self.running = False

    def _show_new_unlocks(self, newly_unlocked: List[str]) -> None:
        """Show newly unlocked bonuses."""
        print("\n" + "="*60)
        print("NEW UNLOCKS ACHIEVED!")
        print("="*60)

        for unlock_id in newly_unlocked:
            info = Unlock.UNLOCK_DATA[unlock_id]
            print(f"\n✓ {info['name']}")
            print(f"  {info['description']}")
            print(f"  Bonus: {info['bonus']}")

        print(f"\n{len(newly_unlocked)} new unlock(s) will apply to future runs!")
        input("\nPress Enter to continue...")

    def _show_victory_screen(self) -> None:
        """Display victory screen with stats."""
        print(f"\n{'='*60}")
        print("VICTORY! You've Mastered the Art of Cow Tipping!")
        print(f"{'='*60}")
        print(f"\nCongratulations, {self.player.name}!")
        self._show_stats()
        print(f"\n{'='*60}")
        input("\nPress Enter to return to main menu...")

    def _show_stats(self) -> None:
        """Show game statistics."""
        print(f"\nGame Statistics:")
        print(f"  Cows Defeated: {self.stats.cows_defeated}")
        print(f"  Cows Fled From: {self.stats.cows_fled_from}")
        print(f"  Total Cash Earned: ${self.stats.cash_earned}")
        print(f"  Total Cash Spent: ${self.stats.cash_spent}")
        print(f"  Dairy Cows Milked: {self.stats.dairy_cows_milked}")
        print(f"  Shops Visited: {self.stats.shops_visited}")
        print(f"  Mini-Games Won: {self.stats.mini_games_won}")
        print(f"  Legendary Items Found: {self.stats.legendary_items_found}")

    def _restart_game(self) -> None:
        """Reset game state for new run."""
        # Delete old save before restarting
        SaveManager.delete_save()

        self.player = Player(self.game_terminal, self.player.name)
        self.cow = None
        self.cows = [self.generate_cow() for _ in range(COW_QUEUE_SIZE)]
        self.cow_packs = {pack: 0.0 for pack in range(1, NUM_COW_PACKS + 1)}
        self.stats = GameStats()  # Reset stats

    def save_game(self) -> bool:
        """Save current game state."""
        return SaveManager.save_game(self.player, self.stats, self.cow_packs)

    def _load_saved_game(self) -> None:
        """Load game state from save file."""
        save_data = SaveManager.load_game()
        if not save_data:
            print("No save file found or load failed.")
            return

        # Restore player
        SaveManager.restore_player(self.player, save_data)

        # Restore stats
        SaveManager.restore_stats(self.stats, save_data)

        # Restore pack scores
        self.cow_packs = save_data['cow_packs']

        print(f"\nGame loaded from {save_data['timestamp']}")
        print(f"Welcome back, {self.player.name}!")
        input("\nPress Enter to continue...")

    def quit_with_save(self) -> None:
        """Quit game with option to save."""
        print("\n" + "="*60)
        print("Quitting game...")
        save_choice = input("Save your progress? (y/n): ").strip().lower()

        if save_choice == 'y':
            if self.save_game():
                print("Progress saved! You can continue later.")
            else:
                print("Save failed.")

        self.game_terminal.close_game_terminal()
        self.running = False
