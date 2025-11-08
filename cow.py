from typing import Dict
import random

from dialogue_manager import DialogueManager
from game_config import (
    LIKELINESS_BASE,
    LIKELINESS_UPSET_THRESHOLD,
    LIKELINESS_FRIENDLY_THRESHOLD,
    LIKELINESS_MOOD_OFFSETS,
    LIKELINESS_MOOD_WEIGHTS,
    COW_MAX_STRENGTH_MULTIPLIER,
    COW_MAX_STRENGTH_FROM_CASH,
    AGGRO_BASE_CHANCE,
    SHOP_CHANCE,
    NUM_COW_PACKS,
)
from models import CowProperties, CowMood

class Cow:
    """Represents a cow in the game with stats, behavior, and dialogue."""

    def __init__(self, game_terminal, properties: CowProperties):
        """Initialize cow from CowProperties dataclass."""
        self.game_terminal = game_terminal
        self.name = properties.name
        self.req_amount = properties.req_amount
        self.likeliness = properties.likeliness
        self.strength = properties.strength
        self.hp = properties.hp
        self.max_hp = properties.hp
        self.cash = properties.cash
        self.is_shop = properties.is_shop
        self.is_aggro = properties.is_aggro
        self.pack = properties.pack
        self.approach = properties.approach
        self.mood: CowMood = self.set_mood(self.likeliness)

    @staticmethod
    def generate_random_cow_properties(player) -> CowProperties:
        """Generate random cow properties scaled to player progression."""
        from easter_eggs import get_legendary_cow

        # Check for legendary cow Easter egg (0.1% chance)
        legendary = get_legendary_cow()
        if legendary:
            cow_name, legendary_data = legendary
            return Cow._create_legendary_cow(player, cow_name, legendary_data)

        likeliness = Cow.set_random_likeliness()
        max_strength = max(
            int(player.hp * COW_MAX_STRENGTH_MULTIPLIER),
            int(player.cash // COW_MAX_STRENGTH_FROM_CASH)
        )
        from game_config import (
            COW_MIN_HP, COW_HP_STRENGTH_MULTIPLIER_LOW, COW_HP_STRENGTH_MULTIPLIER_HIGH,
            COW_HP_LIKELINESS_MULTIPLIER, COW_HP_CASH_BONUS_MIN, COW_HP_CASH_BONUS_MAX,
            COW_HP_CASH_MODULO, COW_TIP_REQUIREMENT_MIN, COW_TIP_REQUIREMENT_MAX,
            COW_TIP_CASH_SCALING
        )
        strength = random.randint(3, max_strength) if 3 < max_strength else 3
        hp_multiplier = COW_HP_LIKELINESS_MULTIPLIER if likeliness < LIKELINESS_BASE else 1
        hp = max(COW_MIN_HP, strength * random.randint(COW_HP_STRENGTH_MULTIPLIER_LOW, COW_HP_STRENGTH_MULTIPLIER_HIGH) * hp_multiplier)
        hp += random.randint(COW_HP_CASH_BONUS_MIN, COW_HP_CASH_BONUS_MAX) * int(player.cash % COW_HP_CASH_MODULO)
        from game_config import AGGRO_MAX_CHANCE
        # Cap aggro chance to prevent late-game combat overload
        aggro_chance = min(AGGRO_BASE_CHANCE + (player.cash / 2000), AGGRO_MAX_CHANCE)
        is_aggro = random.random() < aggro_chance
        is_shop = random.random() < SHOP_CHANCE if not is_aggro else False

        # ECONOMY FIX: Increase cash rewards to match shop prices
        base_cash = random.randint(strength, hp)
        cash_multiplier = 2.0 + (player.cash / 500)  # Better scaling
        cash_reward = max(30, int(base_cash * cash_multiplier))  # Minimum $30 reward

        return CowProperties(
            name=DialogueManager.get_cow_name(),
            req_amount=(random.randint(COW_TIP_REQUIREMENT_MIN, COW_TIP_REQUIREMENT_MAX) + (player.cash // COW_TIP_CASH_SCALING)),
            likeliness=likeliness,
            strength=strength,
            hp=hp,
            cash=cash_reward,
            is_shop=is_shop,
            is_aggro=is_aggro,
            pack=random.randint(1, NUM_COW_PACKS),
            approach=DialogueManager.get_approach()
        )

    @staticmethod
    def set_random_likeliness() -> int:
        """Generate random cow likeliness with weighted offsets."""
        mood_offsets = random.choices(LIKELINESS_MOOD_OFFSETS, weights=LIKELINESS_MOOD_WEIGHTS)[0]
        return LIKELINESS_BASE + mood_offsets

    def set_mood(self, likeliness: int) -> CowMood:
        """Determine cow mood based on likeliness value."""
        if likeliness <= LIKELINESS_UPSET_THRESHOLD:
            return 'upset'
        elif likeliness >= LIKELINESS_FRIENDLY_THRESHOLD:
            return 'friendly'
        else:
            return 'neutral'

    def tip(self, amount: int) -> str:
        """Handle tipping and return cow's response."""
        response_type = 'graceful' if amount >= self.req_amount else 'counter'
        self.likeliness += (amount >= self.req_amount)
        return self.get_response(response_type)

    def get_response(self, response_type: str) -> str:
        """Get dialogue response from DialogueManager."""
        return DialogueManager.get_cow_saying(self.mood, response_type)

    def get_approach(self):
        """Display cow's approach (already shown via draw_dialog)."""
        # Don't use print() - it bypasses terminal margins!
        self.game_terminal.draw_dialog(self.approach)
        # draw_dialog already called stdscr.refresh(), don't call game_terminal.refresh()!

    def print_response(self, cow_name, response_type, gap=True):
        """Print cow response - only use draw_dialog to avoid duplication."""
        response = self.get_response(response_type)
        # Only use draw_dialog (handles margins via curses)
        # Don't print() - that would duplicate the text
        self.game_terminal.draw_dialog(f"{cow_name}: {response}")
        
    def get_combat_stats(self):
        hp_str = f"{self.hp}/{self.max_hp}" if self.hp != self.max_hp else f"{self.hp}"
        return f"{self.name} | {self.strength} STR | {hp_str} HP"

    def get_mood_status(self):
        return f"{self.name} | {self.mood}."

    @staticmethod
    def _create_legendary_cow(player, cow_name: str, legendary_data: Dict) -> CowProperties:
        """Create a legendary named cow with special properties."""
        from easter_eggs import EasterEggRewards

        EasterEggRewards.legendary_cow_found(cow_name)

        # Use legendary approach
        approach = legendary_data['approach']
        mood = legendary_data.get('mood_override', 'friendly')
        strength = legendary_data.get('strength_override', 10)
        hp = strength * 5
        cash = int(30 * legendary_data.get('cash_multiplier', 2.0))

        # Map mood to likeliness
        mood_to_likeliness = {'upset': 3, 'neutral': 5, 'friendly': 8}
        likeliness = mood_to_likeliness.get(mood, 5)

        return CowProperties(
            name=cow_name,
            req_amount=10,
            likeliness=likeliness,
            strength=strength,
            hp=hp,
            cash=cash,
            is_shop=legendary_data.get('is_shop', False),
            is_aggro=legendary_data.get('is_aggro', False),
            pack=random.randint(1, 6),
            approach=approach
        )
        