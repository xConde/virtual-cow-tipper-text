"""
Data models using dataclasses for clean, typed data structures.
"""
from dataclasses import dataclass
from typing import Literal

CowMood = Literal['upset', 'neutral', 'friendly']


@dataclass
class CowProperties:
    """Properties for generating a new cow."""
    name: str
    req_amount: int
    likeliness: int
    strength: int
    hp: int
    cash: int
    is_shop: bool
    is_aggro: bool
    pack: int
    approach: str

    @property
    def mood(self) -> CowMood:
        """Calculate mood based on likeliness."""
        from game_config import LIKELINESS_UPSET_THRESHOLD, LIKELINESS_FRIENDLY_THRESHOLD
        if self.likeliness <= LIKELINESS_UPSET_THRESHOLD:
            return 'upset'
        elif self.likeliness >= LIKELINESS_FRIENDLY_THRESHOLD:
            return 'friendly'
        else:
            return 'neutral'


@dataclass
class PlayerState:
    """Player state for save/load functionality."""
    name: str
    hp: int
    cash: int
    inventory_items: list
    weapon_name: str | None = None
    shield_name: str | None = None
    pack_scores: dict = None


@dataclass
class GameStats:
    """Track player statistics throughout the game."""
    cows_defeated: int = 0
    cows_fled_from: int = 0
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    cash_earned: int = 0
    cash_spent: int = 0
    items_purchased: int = 0
    items_sold: int = 0
    mini_games_won: int = 0
    mini_games_lost: int = 0
    legendary_items_found: int = 0
    dairy_cows_milked: int = 0
    shops_visited: int = 0

    def check_victory(self) -> bool:
        """Check if player has achieved victory."""
        from game_config import VICTORY_COWS_DEFEATED, VICTORY_CASH_EARNED, VICTORY_LEGENDARY_ITEMS

        return (self.cows_defeated >= VICTORY_COWS_DEFEATED or
                self.cash_earned >= VICTORY_CASH_EARNED or
                self.legendary_items_found >= VICTORY_LEGENDARY_ITEMS)


@dataclass
class ItemStats:
    """Base stats for weapons and shields."""
    name: str
    min_value: int
    max_value: int
    rarity: str
    scale: int

    def get_scaled_min(self) -> int:
        """Calculate actual min stat with rarity scaling."""
        from game_config import RARITY_MIN_STAT_MULTIPLIER
        return self.min_value + int(self.min_value * self.scale * RARITY_MIN_STAT_MULTIPLIER)

    def get_scaled_max(self) -> int:
        """Calculate actual max stat with rarity scaling."""
        from game_config import RARITY_MAX_STAT_MULTIPLIER
        return self.max_value + int(self.max_value * self.scale * RARITY_MAX_STAT_MULTIPLIER)
