import random

from assets.context import cow_sayings, cow_names, approaches
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
        likeliness = Cow.set_random_likeliness()
        max_strength = max(
            int(player.hp * COW_MAX_STRENGTH_MULTIPLIER),
            int(player.cash // COW_MAX_STRENGTH_FROM_CASH)
        )
        strength = random.randint(3, max_strength) if 3 < max_strength else 3
        hp = max(10, strength * random.randint(1, 2) * (2 if likeliness < LIKELINESS_BASE else 1)) + random.randint(1, 3) * int(player.cash % 20)
        is_aggro = random.randint(0, 99) < (AGGRO_BASE_CHANCE * 100 + int(player.cash / 20))
        is_shop = random.randint(0, 99) < (SHOP_CHANCE * 100) if not is_aggro else False

        return CowProperties(
            name=random.choice(cow_names),
            req_amount=(random.randint(3, 12) + 5 * player.cash % 25),
            likeliness=likeliness,
            strength=strength,
            hp=hp,
            cash=random.choices([random.randint(strength, hp), random.randint(strength, hp) * 2], weights=[0.40, 0.60])[0],
            is_shop=is_shop,
            is_aggro=is_aggro,
            pack=random.randint(1, NUM_COW_PACKS),
            approach=random.choice(approaches)
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

    def tip(self, amount):
        response = 'graceful' if amount >= self.req_amount else 'counter'
        self.likeliness += (amount >= self.req_amount)
        return self.get_response(response)

    def get_response(self, response_type):
        return random.choice(cow_sayings[self.mood][response_type])

    def get_approach(self):
        print(f'\n{self.approach}')
        self.game_terminal.draw_dialog(self.approach)
        self.game_terminal.refresh()

    def print_response(self, cow_name, response_type, gap=True):
        print(f"{cow_name}: {self.get_response(response_type)}" + ('\n' if gap else ''))
        self.game_terminal.draw_dialog(self.get_response(response_type))
        
    def get_combat_stats(self):
        hp_str = f"{self.hp}/{self.max_hp}" if self.hp != self.max_hp else f"{self.hp}"
        return f"{self.name} | {self.strength} STR | {hp_str} HP"

    def get_mood_status(self):
        return f"{self.name} | {self.mood}."
        