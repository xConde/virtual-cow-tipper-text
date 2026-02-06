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
from utils import safe_print
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

        # Apply career bonuses to player
        self.player.damage_bonus = bonuses['damage_bonus']
        self.player.dairy_heal_bonus = bonuses['dairy_heal_bonus']

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

        # FIX 4: Floor system tracking (MUST be initialized!)
        self.current_floor = 1
        self.encounters_this_floor = 0
        self.encounters_per_floor = 10

        # Load saved game if requested
        if load_save:
            self._load_saved_game()

    def _show_game_introduction(self, loaded_game: bool = False) -> None:
        """Show welcome message and game introduction."""
        self.game_terminal.clear_screen()
        self.game_terminal.stdscr.refresh()
        self.player.display_info()

        if loaded_game:
            inventory_count = len(self.player.inventory)

            intro_msg = (
                f"Welcome back, {self.player.name}!\n\n"
                f"Progress:\n"
                f"  Floor {self.current_floor} - Encounter #{self.encounters_this_floor + 1}\n"
                f"  Cows Defeated: {self.stats.cows_defeated}\n"
                f"  Inventory: {inventory_count}/8 items"
            )
        else:
            intro_msg = (
                f"The Cow Towers\n\n"
                f"{self.player.name}, you stand at the base.\n\n"
                f"Climb the tower. Survive the encounters.\n"
                f"Build your reputation.\n\n"
                f"HP: {self.player.hp}  |  Cash: ${self.player.cash}\n\n"
                f"Arrows or numbers to select. SPACE or ENTER to confirm."
            )

        self.game_terminal.draw_dialog(intro_msg)
        self._pause_with_prompt("[Press any key to begin...]")

        self.game_terminal.clear_screen()
        self.game_terminal.stdscr.refresh()

    def start(self) -> None:
        """Main game loop."""
        if not hasattr(self, 'showed_intro'):
            self._show_game_introduction()
            self.showed_intro = True

        while self.running:
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
        """Clean up current cow and increment encounter tracking."""
        self.game_terminal.set_cow_stats('')
        self.cow = None
        self.encounters_this_floor += 1

        if self.encounters_this_floor >= self.encounters_per_floor:
            self.advance_floor()

    def advance_floor(self):
        """Advance to the next floor and reset encounter counter."""
        self.current_floor += 1
        self.encounters_this_floor = 0

        floor_msg = f"=== FLOOR {self.current_floor} REACHED ===\n\nYou ascend to the next level!"
        self.game_terminal.draw_dialog(floor_msg)
        self._pause_with_prompt("[Press any key to continue...]")

    def update_cow_scores(self, defeated_cow: Cow, score: float):
        """Update pack reputation and queued cow likeliness based on interaction outcome."""
        self.cow_packs[defeated_cow.pack] += score
        for queued_cow in self.cows:
            queued_cow.likeliness += score
        self.destroy_cow()

    def player_turn(self):
        if not self.cow:
            self.spawn_cow()

            self.game_terminal.clear_screen()
            self.game_terminal.stdscr.refresh()
            self.player.display_info()

            encounter_num = self.encounters_this_floor + 1
            if self.cow.is_aggro:
                cow_type = "Aggressive Cow"
                behavior = "AGGRESSIVE"
                behavior_desc = f"{self.cow.name} looks hostile and ready to fight!"
            elif self.cow.is_shop:
                cow_type = "Shop Keeper"
                behavior = "SHOP KEEPER"
                behavior_desc = f"{self.cow.name} runs a shop here."
            else:
                cow_type = "Peaceful Cow"
                behavior = "NEUTRAL"
                behavior_desc = f"{self.cow.name} seems curious about you."

            if self.first_encounter:
                intro_msg = f"Floor {self.current_floor} - Encounter #1\n\n"
                intro_msg += f"{self.cow.approach}\n\n"

                if self.cow.is_aggro:
                    intro_msg += "The cow is hostile."
                elif self.cow.is_shop:
                    intro_msg += "The cow runs a shop."
                else:
                    intro_msg += "The cow seems amenable to a wager."

                intro_msg += "\n\nYour options will be presented below."

                self.first_encounter = False
            else:
                intro_msg = f"Floor {self.current_floor} - Encounter #{encounter_num}\n\n"
                intro_msg += f"{self.cow.approach}"
            if self.cow.is_aggro:
                cow_header = f"{self.cow.name} | HP {self.cow.hp} | STR {self.cow.strength} - HOSTILE"
            elif self.cow.is_shop:
                cow_header = f"{self.cow.name} | Shop ({self.cow.mood})"
            else:
                cow_header = f"{self.cow.name} | {self.cow.mood.title()}"
            self.game_terminal.set_cow_stats(cow_header)

            self.game_terminal.draw_dialog(intro_msg)
            self._pause_with_prompt("[Press any key to continue...]")

            # Easter egg: Lucky 777
            from easter_eggs import check_lucky_number
            lucky = check_lucky_number(self.player.hp, self.player.cash)
            if lucky and not getattr(self, '_lucky_777_used', False):
                self._lucky_777_used = True
                from easter_eggs import EasterEggRewards
                self.game_terminal.close_game_terminal()
                lucky_rewards = EasterEggRewards.lucky_777_activated(
                    "HP" if self.player.hp == 77 else "Cash"
                )
                # Apply immediate rewards
                from game_config import PLAYER_MAX_HP
                self.player.cash += lucky_rewards['cash_bonus']
                self.player.hp = min(self.player.hp + lucky_rewards['hp_bonus'], PLAYER_MAX_HP)
                self.stats.cash_earned += lucky_rewards['cash_bonus']
                input("\nPress Enter to continue...")
                self.game_terminal = GameTerminal()
                self.player.display_info()
                self.game_terminal.draw_dialog(intro_msg)
                self.game_terminal.stdscr.refresh()

        # Easter egg: Meta-dialogue (1% chance)
        from easter_eggs import get_meta_dialogue
        meta = get_meta_dialogue()
        if meta:
            self.game_terminal.draw_dialog(f"[The cow pauses and looks at you] \"{meta}\" [It continues as normal]")
            self._pause_with_prompt("[Press any key to continue...]")

        # Easter egg: Philosopher cow dialogue (0.5% chance on neutral encounters)
        if self.cow.mood == 'neutral':
            from easter_eggs import get_philosopher_cow_dialogue
            philosophy = get_philosopher_cow_dialogue()
            if philosophy:
                formatted = philosophy.replace('{player_name}', self.player.name)
                self.game_terminal.draw_dialog(f"{self.cow.name}: \"{formatted}\"")
                self._pause_with_prompt("[Press any key to continue...]")

        is_interrupted = self.get_interruption()
        if is_interrupted:
            CowInteraction(self, self.player, self.cow).interact()
            return

        actions = {
            "approach the cow": lambda: CowInteraction(self, self.player, self.cow).interact(),
            "rest": self._rest,
            "inventory": lambda: self.player.check_inventory(),
            "quit": self.quit_with_save,
        }

        menu_items = [f"{i+1}. {action}" for i, action in enumerate(actions.keys())]
        choice = self.game_terminal.get_menu_choice(menu_items)

        if choice in range(1, len(actions) + 1):
            action_name = list(actions.keys())[choice - 1]
            action_func = actions[action_name]

            try:
                action_func()
            except Exception as e:
                safe_print(f"Error executing action: {e}")
                import traceback
                traceback.print_exc()

    def _rest(self) -> None:
        """Rest to recover HP. Only skips cow if healing occurs."""
        from game_config import REST_HEAL_AMOUNT, PLAYER_MAX_HP

        if self.player.hp >= PLAYER_MAX_HP:
            saved_dialog = self.game_terminal.save_dialog_state()

            rest_msg = (
                f"Already at Full HP!\n\n"
                f"{self.player.name}, you're already at maximum health.\n\n"
                f"No need to rest right now.\n\n"
                f"The cow waits patiently..."
            )
            self.game_terminal.draw_dialog(rest_msg)
            self._pause_with_prompt("[Press any key to continue...]")

            self.game_terminal.restore_dialog_state(saved_dialog)
            return

        old_hp = self.player.hp
        self.player.hp = min(self.player.hp + REST_HEAL_AMOUNT, PLAYER_MAX_HP)
        healed = self.player.hp - old_hp

        rest_msg = (
            f"=== RESTING ===\n\n"
            f"{self.player.name} takes a moment to rest.\n"
            f"HP restored: +{healed}\n"
            f"Current HP: {self.player.hp}/{PLAYER_MAX_HP}\n\n"
            f"The cow wanders off while you rest..."
        )
        self.game_terminal.draw_dialog(rest_msg)
        self.destroy_cow()
        self._pause_with_prompt("[Press any key to continue...]")
    
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

            # Close curses before print-based screens
            self.game_terminal.close_game_terminal()

            if newly_unlocked:
                self._show_new_unlocks(newly_unlocked)

            should_restart = self.player.die(self.stats)
            if should_restart:
                self.game_terminal = GameTerminal()
                self._restart_game()
            else:
                self.running = False

    def check_victory_conditions(self) -> None:
        """Check if player has won the game."""
        from easter_eggs import check_achievement_42, EasterEggRewards

        # Easter egg: 42 cows achievement
        if check_achievement_42(self.stats.cows_defeated) and self.stats.cows_defeated not in getattr(self, '_achievements_shown', set()):
            if not hasattr(self, '_achievements_shown'):
                self._achievements_shown = set()
            self._achievements_shown.add(self.stats.cows_defeated)
            self.game_terminal.close_game_terminal()
            towel = EasterEggRewards.achievement_42()
            self.player.update_inventory(towel, "add")
            self.stats.legendary_items_found += 1
            input("\nPress Enter to continue...")
            self.game_terminal = GameTerminal()

        if self.stats.check_victory():
            # Update career stats with victory
            self.career_stats.add_run_stats(self.stats, victory=True)
            newly_unlocked = self.career_stats.check_unlocks()
            self.career_stats.save()

            # Close curses before print-based screens
            self.game_terminal.close_game_terminal()

            self._show_victory_screen()

            if newly_unlocked:
                self._show_new_unlocks(newly_unlocked)

            self.running = False

    def _show_new_unlocks(self, newly_unlocked: List[str]) -> None:
        """Show newly unlocked bonuses."""
        print("\n" + "="*60)
        print("NEW UNLOCKS ACHIEVED!")
        print("="*60)

        for unlock_id in newly_unlocked:
            info = Unlock.UNLOCK_DATA[unlock_id]
            print(f"\n[OK] {info['name']}")
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

    def _pause_with_prompt(self, prompt_text: str = "[Continue...]"):
        """
        Show a pause prompt and wait for keypress, with menu hidden.

        This is a helper method to maintain consistent pause behavior across game.py.
        It follows the same pattern as CowInteraction.pause_with_prompt().
        """
        # Clear menu area so it doesn't show during pause
        self.game_terminal.clear_area(self.game_terminal.MENU_Y_START, self.game_terminal.MENU_Y_END)

        # Clear prompt area first to remove any old text
        self.game_terminal.clear_area(self.game_terminal.PROMPT_INPUT_Y)

        # Show prompt
        prompt_y = self.game_terminal.PROMPT_INPUT_Y
        self.game_terminal.stdscr.addstr(prompt_y, 2, prompt_text)
        self.game_terminal.stdscr.refresh()
        self.game_terminal.stdscr.getch()

    def _restart_game(self) -> None:
        """Reset game state for new run, preserving career bonuses."""
        SaveManager.delete_save()

        # Re-load career stats (may have new unlocks from the run that just ended)
        self.career_stats = CareerStats.load()
        bonuses = self.career_stats.get_starting_bonuses()
        self.career_bonuses = bonuses

        self.player = Player(
            self.game_terminal,
            self.player.name,
            starting_hp=20 + bonuses['extra_hp'],
            starting_cash=50 + bonuses['extra_cash']
        )
        self.player.damage_bonus = bonuses['damage_bonus']
        self.player.dairy_heal_bonus = bonuses['dairy_heal_bonus']

        # Apply starting items from unlocks
        for item_id in bonuses['starting_items']:
            if item_id == 'cowbell':
                self.player.inventory.append(CowBell())
            elif item_id == 'basic_weapon':
                from item_factory import ItemFactory
                weapon = ItemFactory.create_weapon(less_likely=True)
                self.player.weapon = weapon

        self.cow = None
        self.cows = [self.generate_cow() for _ in range(COW_QUEUE_SIZE)]
        self.cow_packs = {pack: 0.0 for pack in range(1, NUM_COW_PACKS + 1)}
        self.stats = GameStats()
        self.current_floor = 1
        self.encounters_this_floor = 0

    def save_game(self) -> bool:
        """Save current game state."""
        return SaveManager.save_game(self.player, self.stats, self.cow_packs,
                                     self.current_floor, self.encounters_this_floor)

    def _load_saved_game(self) -> None:
        """Load game state from save file."""
        save_data = SaveManager.load_game()
        if not save_data:
            print("No save file found or load failed.")
            return

        SaveManager.restore_player(self.player, save_data)
        SaveManager.restore_stats(self.stats, save_data)

        self.cow_packs = save_data['cow_packs']
        self.current_floor = save_data.get('current_floor', 1)
        self.encounters_this_floor = save_data.get('encounters_this_floor', 0)

        self.showed_intro = True
        self._show_game_introduction(loaded_game=True)

    def quit_with_save(self) -> None:
        """Quit game with option to save."""
        saved_dialog = self.game_terminal.save_dialog_state()

        quit_msg = f"Quitting Game\n\nSave your progress?"
        self.game_terminal.draw_dialog(quit_msg)

        menu_items = ["1. Save and quit", "2. Quit without saving", "3. Cancel (back to game)"]
        choice = self.game_terminal.get_menu_choice(menu_items, "Select an option:")

        if choice == 1:
            if self.save_game():
                success_msg = "Progress Saved!\n\nYou can continue later.\n\nSee you next time!"
                self.game_terminal.draw_dialog(success_msg)
                self._pause_with_prompt("[Press any key to exit...]")
                self.game_terminal.close_game_terminal()
                self.running = False
            else:
                error_msg = "Save Failed!\n\nUnable to save progress.\n\nQuitting anyway..."
                self.game_terminal.draw_dialog(error_msg)
                self._pause_with_prompt("[Press any key to exit...]")
                self.game_terminal.close_game_terminal()
                self.running = False
        elif choice == 2:
            self.game_terminal.close_game_terminal()
            self.running = False
        else:
            self.game_terminal.restore_dialog_state(saved_dialog)
