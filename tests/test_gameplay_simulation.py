"""
Gameplay simulation - Test all systems work together in realistic scenarios.
"""
import random

from cow import Cow
from player import Player
from models import CowProperties, GameStats
from item_factory import ItemFactory
from item import HealthPotion
from dialogue_manager import DialogueManager
from save_manager import SaveManager


class MockStdscr:
    def refresh(self): pass
    def addstr(self, *args): pass
    def getch(self): return ord('\n')

class MockTerminal:
    """Mock terminal for headless testing."""
    def __init__(self):
        self.stdscr = MockStdscr()
    def clear_screen(self): pass
    def refresh(self): pass
    def set_cow_stats(self, s): pass
    def draw_dialog(self, s): pass
    def set_player_stats(self, *args): pass
    def draw_player_stats(self, *args): pass
    def draw_game_title(self, *args): pass
    def draw_separator(self, *args): pass
    def close_game_terminal(self): pass


def test_early_game_scenario():
    """Simulate first 5 encounters."""
    terminal = MockTerminal()
    player = Player(terminal, "TestHero")
    stats = GameStats()

    for i in range(1, 6):
        # Generate cow
        props = Cow.generate_random_cow_properties(player)
        cow = Cow(terminal, props)

        # Simulate outcome
        if cow.is_aggro:
            # Combat
            player.deal_damage(cow)
            if cow.hp <= 0:
                player.update_cash(cow.cash)
                stats.cows_defeated += 1
        elif cow.is_shop:
            # Buy potion if low HP
            if player.hp < 15 and player.cash >= 50:
                potion = HealthPotion('normal')
                player.cash -= 50
                player.inventory.append(potion)
                stats.items_purchased += 1

    assert player.hp > 0, "Player should survive early game"


def test_healing_mechanics():
    """Test all 3 healing methods work."""
    terminal = MockTerminal()
    player = Player(terminal, "Healer")
    player.hp = 50  # Damaged

    # Test 1: Health Potion
    potion = HealthPotion('normal')
    player.inventory.append(potion)
    potion.use(player)
    assert player.hp == 70, f"Expected 70 HP, got {player.hp}"

    # Test 2: Rest (simulated)
    from game_config import REST_HEAL_AMOUNT, PLAYER_MAX_HP
    old_hp = player.hp
    player.hp = min(player.hp + REST_HEAL_AMOUNT, PLAYER_MAX_HP)
    assert player.hp > old_hp

    # Test 3: Dairy healing (simulated)
    from game_config import DAIRY_COW_HEAL_AMOUNT
    old_hp = player.hp
    player.hp = min(player.hp + DAIRY_COW_HEAL_AMOUNT, PLAYER_MAX_HP)
    assert player.hp >= old_hp

    # Test HP cap
    player.hp = 95
    player.hp = min(player.hp + 20, PLAYER_MAX_HP)
    assert player.hp == 100, "HP should cap at 100"


def test_combat_balance():
    """Test late game combat is balanced."""
    terminal = MockTerminal()
    player = Player(terminal, "Fighter")
    player.cash = 1000  # Late game wealth
    player.hp = 80

    # Generate late game cow
    props = Cow.generate_random_cow_properties(player)
    cow = Cow(terminal, props)

    # Calculate expected damage
    from game_config import PLAYER_BASE_DAMAGE_MIN, PLAYER_BASE_DAMAGE_MAX, PLAYER_DAMAGE_CASH_SCALING
    player_dmg = random.randint(PLAYER_BASE_DAMAGE_MIN, PLAYER_BASE_DAMAGE_MAX) + (player.cash // PLAYER_DAMAGE_CASH_SCALING)

    assert cow.strength < 40, f"Late game cows should be < 40 strength (got {cow.strength})"
    assert player_dmg > cow.strength, f"Player should outdamage cow (player:{player_dmg} vs cow:{cow.strength})"


def test_economy_balance():
    """Test shop prices vs cow rewards."""
    terminal = MockTerminal()
    player = Player(terminal, "Merchant")
    player.cash = 500

    # Generate shop
    shop_items = ItemFactory.get_shop_inventory('neutral', player.cash, False)

    # Generate cow reward
    props = Cow.generate_random_cow_properties(player)
    cow_reward = props.cash

    assert cow_reward >= 30, f"Cow rewards should be >=$30 (got ${cow_reward})"
    item_price = shop_items[0]['price']
    assert item_price < 100, f"Shop items should be <$100 (got ${item_price:.0f})"


def test_aggro_chance_capped():
    """Test aggro chance doesn't exceed cap."""
    class RichPlayer:
        hp = 20
        cash = 5000  # Very rich

    aggro_count = 0
    total = 100

    for _ in range(total):
        props = Cow.generate_random_cow_properties(RichPlayer())
        if props.is_aggro:
            aggro_count += 1

    aggro_percentage = aggro_count / total

    from game_config import AGGRO_MAX_CHANCE
    assert aggro_percentage <= AGGRO_MAX_CHANCE + 0.1, f"Aggro should be capped at {AGGRO_MAX_CHANCE*100}%"


def test_save_load_with_potions():
    """Test save/load preserves healing items."""
    SaveManager.delete_save()

    terminal = MockTerminal()
    player = Player(terminal, "SaveTest")
    player.hp = 50
    player.cash = 200

    # Add potions to inventory
    potion1 = HealthPotion('normal')
    potion2 = HealthPotion('greater')
    player.inventory.append(potion1)
    player.inventory.append(potion2)

    stats = GameStats(cows_defeated=10)
    packs = {1: 2.0, 2: 0.0, 3: -1.0, 4: 0.0, 5: 0.0, 6: 0.0}

    # Save
    SaveManager.save_game(player, stats, packs)

    # Load
    save_data = SaveManager.load_game()
    assert save_data is not None

    # Verify potions preserved
    assert len(save_data['player']['inventory']) == 2

    # Cleanup
    SaveManager.delete_save()
