from typing import Optional
import random

from cow import Cow
from player import Player
from item import Item
from assets.context import interruptions
from cow_interaction import CowInteraction
from terminal.game_terminal import GameTerminal
from game_config import (
    COW_QUEUE_SIZE,
    NUM_COW_PACKS,
    INTERRUPTION_CHANCE,
)

class VirtualCowTipper:
    def __init__(self, player_name: str):
        self.game_terminal = GameTerminal()
        self.player = Player(self.game_terminal, player_name)
        self.cow: Optional[Cow] = None
        self.cows = [self.generate_cow() for _ in range(COW_QUEUE_SIZE)]
        self.cow_packs = {pack: 0.0 for pack in range(1, NUM_COW_PACKS + 1)}
        self.running = True

    def start(self) -> None:
        """Main game loop."""
        while self.running:
            self.game_terminal.clear_screen()
            self.game_terminal.refresh()
            self.player.display_info()
            self.player_turn()
            self.check_end_conditions()

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
        self.cow.get_approach()

        is_interrupted = self.get_interruption()
        if is_interrupted:
            CowInteraction(self, self.player, self.cow).interact()
            return

        actions = {
            "approach the cow": lambda: CowInteraction(self, self.player, self.cow).interact(),
            "check inventory": lambda: self.player.check_inventory(),
            "use an item from inventory": self.player.use_item,
            "quit game": lambda: setattr(self, "running", False),
        }
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
            message = random.choice(interruptions)
            self.game_terminal.draw_dialog(message)
            return message
        return None

    def check_end_conditions(self) -> None:
        """Check if game is over and handle restart."""
        if self.player.hp <= 0 or self.player.cash <= 0:
            should_restart = self.player.die()
            if should_restart:
                self._restart_game()
            else:
                self.game_terminal.close_game_terminal()
                self.running = False

    def _restart_game(self) -> None:
        """Reset game state for new run."""
        self.player = Player(self.game_terminal, self.player.name)
        self.cow = None
        self.cows = [self.generate_cow() for _ in range(COW_QUEUE_SIZE)]
        self.cow_packs = {pack: 0.0 for pack in range(1, NUM_COW_PACKS + 1)}
