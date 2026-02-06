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

    def use(self, player):
        """
        Use potion to restore HP.

        Returns:
            True if potion was used (HP not full), False if HP already at max
        """
        from game_config import PLAYER_MAX_HP

        if self.stat == 'hp':
            if player.hp >= PLAYER_MAX_HP:
                return False

            old_hp = player.hp
            player.hp = min(player.hp + self.boost_amount, PLAYER_MAX_HP)
            return True
        return False


class HealthPotion(Potion):
    def __init__(self, strength: str = 'minor'):
        amounts = {'minor': 10, 'normal': 20, 'greater': 40}
        names = {'minor': 'Minor Health Potion', 'normal': 'Health Potion', 'greater': 'Greater Health Potion'}
        super().__init__(names[strength], 'hp', amounts[strength])
        self.strength = strength

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



# Legacy function exports - forwarding to ItemFactory
# These remain for backward compatibility with existing callers

def roll_weapon_dmg(weapon):
    from item_factory import ItemFactory
    return ItemFactory.roll_weapon_damage(weapon)

def get_shop_items(cow_mood, player_cash, isLucky, shop_discount=0.0):
    from item_factory import ItemFactory
    return ItemFactory.get_shop_inventory(cow_mood, player_cash, isLucky, shop_discount)
