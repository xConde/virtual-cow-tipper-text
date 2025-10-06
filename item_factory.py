"""
Item generation factory - encapsulates all item creation logic.
Replaces global functions from item.py
"""
from typing import Literal, List, Dict
import random

from item import Weapon, Shield, CowBell, Bucket, LiquidGold, Item
from game_config import (
    ITEM_TYPE_WEIGHTS_NORMAL,
    ITEM_TYPE_WEIGHTS_LUCKY,
    ITEM_TIER_WEIGHTS_NORMAL,
    ITEM_TIER_WEIGHTS_LUCKY,
    RARITY_WEIGHTS_NORMAL,
    RARITY_WEIGHTS_LUCKY,
    SHOP_RANDOM_ITEM_MULTIPLIER,
    SHOP_WEAPON_MULTIPLIER,
    SHOP_SHIELD_MULTIPLIER,
    SHOP_PRICE_BASE_MIN,
    SHOP_PRICE_BASE_MAX,
    SHOP_PRICE_CASH_SCALING,
    SHOP_PRICE_UPSET_MULTIPLIER,
)

# Item data (moved from item.py for clarity)
WEAPON_TYPES = [
    {'name': 'dagger', 'min_damage': 1, 'max_damage': 4},
    {'name': 'club', 'min_damage': 2, 'max_damage': 6},
    {'name': 'short bow', 'min_damage': 3, 'max_damage': 8},
    {'name': 'mace', 'min_damage': 4, 'max_damage': 10},
    {'name': 'longbow', 'min_damage': 5, 'max_damage': 12},
    {'name': 'battleaxe', 'min_damage': 6, 'max_damage': 14},
    {'name': 'flail', 'min_damage': 7, 'max_damage': 16},
    {'name': 'halberd', 'min_damage': 8, 'max_damage': 18},
    {'name': 'greatsword', 'min_damage': 9, 'max_damage': 20},
    {'name': 'godsword', 'min_damage': 10, 'max_damage': 22}
]

SHIELD_TYPES = [
    {'name': 'buckler', 'min_defence': 1, 'max_defence': 4},
    {'name': 'targe', 'min_defence': 2, 'max_defence': 6},
    {'name': 'round shield', 'min_defence': 3, 'max_defence': 8},
    {'name': 'heater shield', 'min_defence': 4, 'max_defence': 10},
    {'name': 'kite shield', 'min_defence': 5, 'max_defence': 12},
    {'name': 'tower shield', 'min_defence': 6, 'max_defence': 14},
    {'name': 'pavise', 'min_defence': 7, 'max_defence': 16},
    {'name': 'spiked shield', 'min_defence': 8, 'max_defence': 18},
    {'name': 'barrier shield', 'min_defence': 9, 'max_defence': 20},
    {'name': 'aegis', 'min_defence': 10, 'max_defence': 22}
]

RARITY_ADJECTIVES = {
    'common': {
        'prefix': ['Plain', 'Simple', 'Basic'],
        'suffix': ['']
    },
    'uncommon': {
        'prefix': ['Sturdy', 'Polished', 'Reinforced'],
        'suffix': ['of Quality', 'of Precision']
    },
    'magic': {
        'prefix': ['Enchanted', 'Mystic', 'Arcane'],
        'suffix': ['of Power', 'of Sorcery']
    },
    'rare': {
        'prefix': ['Ancient', 'Exquisite', 'Ethereal'],
        'suffix': ['of Legends', 'of the Ancients']
    },
    'legendairy': {  # Your brilliant pun!
        'prefix': ['Mythic', 'Astral', 'Ethereal'],
        'suffix': ['of the Ancients', 'of Eons']
    }
}

RARITY_NAMES = list(RARITY_ADJECTIVES.keys())


class ItemFactory:
    """Factory for creating randomized items with proper rarity scaling."""

    @staticmethod
    def create_weapon(less_likely: bool = False) -> Weapon:
        """Generate a random weapon with scaled stats."""
        return ItemFactory._create_equipment('weapon', less_likely)

    @staticmethod
    def create_shield(less_likely: bool = False) -> Shield:
        """Generate a random shield with scaled stats."""
        return ItemFactory._create_equipment('shield', less_likely)

    @staticmethod
    def create_random_item(less_likely: bool = False) -> Item:
        """Generate a random item of any type."""
        weights = ITEM_TYPE_WEIGHTS_LUCKY if less_likely else ITEM_TYPE_WEIGHTS_NORMAL
        item_type = random.choices(['weapon', 'shield', 'tool', 'object'], weights=weights)[0]

        if item_type == 'weapon':
            return ItemFactory.create_weapon(less_likely)
        elif item_type == 'shield':
            return ItemFactory.create_shield(less_likely)
        elif item_type == 'tool':
            return ItemFactory._create_random_tool()
        else:
            return ItemFactory._create_random_object()

    @staticmethod
    def get_shop_inventory(cow_mood: str, player_cash: float, is_lucky: bool) -> List[Dict]:
        """Generate shop inventory with pricing based on cow mood and player wealth."""
        base_price = random.randint(SHOP_PRICE_BASE_MIN, SHOP_PRICE_BASE_MAX) + 3 * int(player_cash // SHOP_PRICE_CASH_SCALING)
        price_multiplier = SHOP_PRICE_UPSET_MULTIPLIER if cow_mood == 'upset' else 1.0
        less_likely = not (is_lucky and cow_mood != 'neutral')

        items = [
            {
                "label": "random item",
                "item": ItemFactory.create_random_item(less_likely),
                "price": base_price * SHOP_RANDOM_ITEM_MULTIPLIER * price_multiplier
            },
            {
                "label": "random weapon",
                "item": ItemFactory.create_weapon(less_likely=False),
                "price": base_price * SHOP_WEAPON_MULTIPLIER * price_multiplier
            },
            {
                "label": "random shield",
                "item": ItemFactory.create_shield(less_likely=False),
                "price": base_price * SHOP_SHIELD_MULTIPLIER * price_multiplier
            },
        ]

        return items

    @staticmethod
    def _create_equipment(item_type: Literal['weapon', 'shield'], less_likely: bool) -> Weapon | Shield:
        """Internal: Create weapon or shield with rarity."""
        item_list = WEAPON_TYPES if item_type == 'weapon' else SHIELD_TYPES
        tier_weights = ITEM_TIER_WEIGHTS_LUCKY if less_likely else ITEM_TIER_WEIGHTS_NORMAL

        # Select base item tier
        item_index = random.choices(range(len(item_list)), weights=tier_weights)[0]
        base_item = item_list[item_index]

        # Roll rarity
        rarity_weights = RARITY_WEIGHTS_LUCKY if less_likely else RARITY_WEIGHTS_NORMAL
        scale = random.choices([1, 2, 3, 4, 5], weights=rarity_weights)[0]
        rarity = RARITY_NAMES[scale - 1]

        # Calculate stats
        stat_key = 'min_damage' if item_type == 'weapon' else 'min_defence'
        min_stat = base_item[stat_key]
        max_stat = base_item['max_' + stat_key[4:]]

        # Apply rarity-based name modification
        modified_name = ItemFactory._get_modified_name(base_item['name'], rarity)

        # Create item
        if item_type == 'weapon':
            return Weapon(modified_name, min_stat, max_stat, rarity, scale)
        else:
            return Shield(modified_name, min_stat, max_stat, rarity, scale)

    @staticmethod
    def _get_modified_name(base_name: str, rarity: str) -> str:
        """Add rarity prefix or suffix to item name."""
        prefix_or_suffix = random.choice(['prefix', 'suffix'])
        adjective = random.choice(RARITY_ADJECTIVES[rarity][prefix_or_suffix])

        if prefix_or_suffix == 'prefix':
            return f'{adjective} {base_name}'.strip()
        else:
            return f'{base_name} {adjective}'.strip()

    @staticmethod
    def _create_random_tool() -> CowBell | Bucket:
        """Create a random tool."""
        tools = [CowBell(), Bucket()]
        return random.choice(tools)

    @staticmethod
    def _create_random_object() -> LiquidGold:
        """Create a random object."""
        # Currently only LiquidGold exists
        return LiquidGold()

    @staticmethod
    def calculate_item_median_stat(item: Weapon | Shield) -> float:
        """Calculate median stat value for upgrade comparison."""
        if item.type == 'weapon':
            min_stat, max_stat = item.min_damage, item.max_damage
        elif item.type == 'shield':
            min_stat, max_stat = item.min_defence, item.max_defence
        else:
            raise ValueError(f'Invalid item type for median stat: {item.type}')

        from game_config import RARITY_MIN_STAT_MULTIPLIER, RARITY_MAX_STAT_MULTIPLIER
        min_scaled = min_stat + int(min_stat * item.scale * RARITY_MIN_STAT_MULTIPLIER)
        max_scaled = max_stat + int(max_stat * item.scale * RARITY_MAX_STAT_MULTIPLIER)
        median = (min_scaled + max_scaled) // 2
        return median / 3

    @staticmethod
    def roll_weapon_damage(weapon: Weapon | None) -> int:
        """Roll random damage for a weapon based on its stats and rarity."""
        if not weapon:
            return 0

        from game_config import RARITY_MIN_STAT_MULTIPLIER, RARITY_MAX_STAT_MULTIPLIER
        min_damage = weapon.min_damage + int(weapon.min_damage * weapon.scale * RARITY_MIN_STAT_MULTIPLIER)
        max_damage = weapon.max_damage + int(weapon.max_damage * weapon.scale * RARITY_MAX_STAT_MULTIPLIER)
        return random.randint(min_damage, max_damage)
