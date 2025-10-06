import random


class Item:
    def __init__(self, name, item_type):
        self.name = name
        self.item_type = item_type

    def display_name(self):
        if hasattr(self, 'rarity'):
            return f"{self.name.title()} ({self.rarity})"
        else:
            return self.name


class Potion(Item):
    def __init__(self, name, stat, boost_amount, duration=None):
        super().__init__(name, 'potion')
        self.stat = stat
        self.boost_amount = boost_amount
        self.duration = duration
        self.type = 'potion'

class Weapon(Item):
    def __init__(self, name, min_damage, max_damage, rarity, scale):
        super().__init__(name, 'weapon')
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.rarity = rarity
        self.scale = scale
        self.type = 'weapon'

    def stats(self):
        return f"{self.name} (L: {self.min_damage}, H: {self.max_damage}, Rarity: {self.rarity})"

    def is_upgrade(self, player, item) -> bool:
        """Check if this weapon is better than player's current weapon."""
        if not player.weapon:
            return True
        from item_factory import ItemFactory
        return ItemFactory.calculate_item_median_stat(item) > ItemFactory.calculate_item_median_stat(player.weapon)


class Shield(Item):
    def __init__(self, name, min_defence, max_defence, rarity, scale):
        super().__init__(name, 'shield')
        self.min_defence = min_defence
        self.max_defence = max_defence
        self.rarity = rarity
        self.scale = scale
        self.type = 'shield'

    def stats(self):
        return f"{self.name} (L: {self.min_defence}, H: {self.max_defence}, Rarity: {self.rarity})"

    def is_upgrade(self, player, item) -> bool:
        """Check if this shield is better than player's current shield."""
        if not player.shield:
            return True
        from item_factory import ItemFactory
        return ItemFactory.calculate_item_median_stat(item) > ItemFactory.calculate_item_median_stat(player.shield)


class Tool(Item):
    def __init__(self, name, action):
        super().__init__(name, 'tool')
        self.action = action
        self.type = 'utility'


class CowBell(Tool):
    def __init__(self):
        super().__init__("Cow Bell", None)

    def get_dairy_bonus(self):
        return 15


class Bucket(Tool):
    def __init__(self):
        super().__init__("Bucket", None)

    def use(self):
        return LiquidGold()


class Object(Item):
    def __init__(self, name, description):
        super().__init__(name, 'object')
        self.description = description
        self.type = 'product'


class LiquidGold(Object):
    def __init__(self):
        super().__init__("Liquid Gold", "A valuable substance that can be sold at the shop.")

    def get_value(self, player):
        weapon = player.weapon
        if weapon:
            weapon_dps = (weapon.min_damage + weapon.max_damage) / 2
        else:
            weapon_dps = 0
        return 150 + 5 * weapon_dps + 10 * (player.cash // 50)


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
    'lengendairy': {
        'prefix': ['Mythic', 'Astral', 'Ethereal'],
        'suffix': ['of the Ancients', 'of Eons']
    }
}


def get_modified_name(base_name, rarity, item_type):
    prefix_or_suffix = random.choice(['prefix', 'suffix'])
    adjective = random.choice(RARITY_ADJECTIVES[rarity][prefix_or_suffix])
    return f'{adjective} {base_name}'.strip() if prefix_or_suffix == 'prefix' else f'{base_name} {adjective}'.strip()


def build_item(item_type: str, less_likely: bool = False):
    if item_type not in ['weapon', 'shield', 'tool', 'object']:
        raise ValueError('Invalid item type.')

    item_list = WEAPON_TYPES if item_type == 'weapon' else SHIELD_TYPES
    item_weights = [35, 28, 24, 15, 12, 9, 6, 4, 2, 1] if not less_likely else [
        40, 30, 20, 10, 5, 3, 2, 1, 1, 1]
    item_index = random.choices(range(len(item_list)), weights=item_weights)[0]
    base_item = item_list[item_index]

    weights = [60, 35, 10, 4, 1] if not less_likely else [72, 32, 3, 2, 1]
    scale = random.choices([1, 2, 3, 4, 5], weights=weights)[0]
    rarity = list(RARITY_ADJECTIVES.keys())[scale - 1]

    stat_key = 'min_damage' if item_type == 'weapon' else 'min_defence'
    min_stat = base_item[stat_key]
    max_stat = min(base_item['max_' + stat_key[4:]], min_stat)

    item_obj = {'name': base_item['name'], str(stat_key): min_stat, str('max_' + stat_key[4:]): max_stat, 'rarity': rarity, 'scale': scale}
    item = Weapon(**item_obj) if item_type == 'weapon' else Shield(**item_obj)
    item.name = get_modified_name(item.name, rarity, item_type)

    return item


# Legacy exports for backwards compatibility
# These redirect to ItemFactory - will be removed in Phase 3
from item_factory import ItemFactory

def find_median_stat(item):
    """DEPRECATED: Use ItemFactory.calculate_item_median_stat()"""
    return ItemFactory.calculate_item_median_stat(item)

def roll_weapon_dmg(weapon) -> int:
    """DEPRECATED: Use ItemFactory.roll_weapon_damage()"""
    return ItemFactory.roll_weapon_damage(weapon)

def random_item_roll(less_likely):
    """DEPRECATED: Use ItemFactory.create_random_item()"""
    return ItemFactory.create_random_item(less_likely)

def get_shop_items(cow_mood: str, player_cash: float, isLucky: bool):
    """DEPRECATED: Use ItemFactory.get_shop_inventory()"""
    return ItemFactory.get_shop_inventory(cow_mood, player_cash, isLucky)

def random_tool_roll():
    """DEPRECATED: Use ItemFactory._create_random_tool()"""
    return ItemFactory._create_random_tool()

def random_object_roll():
    """DEPRECATED: Use ItemFactory._create_random_object()"""
    return ItemFactory._create_random_object()

# Remove build_item - no longer needed
