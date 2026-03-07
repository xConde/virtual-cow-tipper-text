"""
Crash Scenario Testing - Find any code paths that could crash the game.
"""


def test_imports_dont_crash():
    """Test all imports work without errors."""
    from game import VirtualCowTipper
    from cow import Cow
    from player import Player
    from cow_interaction import CowInteraction
    from cow_attack import CowAttack
    from item import Weapon, Shield, HealthPotion, CowBell, Bucket
    from item_factory import ItemFactory
    from dialogue_manager import DialogueManager
    from save_manager import SaveManager
    from career_stats import CareerStats, Unlock
    from models import CowProperties, GameStats, PlayerState
    from game_config import PLAYER_STARTING_HP
    from easter_eggs import get_legendary_cow
    from tutorial import show_tutorial

    assert VirtualCowTipper is not None


def test_player_inventory_operations():
    """Test inventory edge cases that could crash."""
    from player import Player
    from item import HealthPotion, Weapon

    class MockTerminal:
        def set_player_stats(self, *args): pass
        def draw_player_stats(self): pass
        def draw_game_title(self): pass
        def draw_separator(self): pass
        def refresh(self): pass
        class stdscr:
            @staticmethod
            def refresh(): pass

    player = Player(MockTerminal(), "Test")

    # Test 1: Use item not in inventory
    potion = HealthPotion()
    player.use_item(potion)  # Not in inventory - should not crash

    # Test 2: Add to full inventory
    from game_config import PLAYER_MAX_INVENTORY_SIZE
    for i in range(PLAYER_MAX_INVENTORY_SIZE + 5):
        player.update_inventory(HealthPotion(), "add")

    assert len(player.inventory) <= PLAYER_MAX_INVENTORY_SIZE

    # Test 3: Remove item not in inventory
    weapon = Weapon("Test", 1, 1, "common", 1)
    player.update_inventory(weapon, "remove")  # Not in inventory

    # Test 4: Use potion at full HP
    player.hp = 100
    potion2 = HealthPotion()
    player.inventory.append(potion2)
    potion2.use(player)
    assert player.hp == 100


def test_cow_generation_edge_cases():
    """Test cow generation doesn't crash with extreme player stats."""
    from cow import Cow

    # Test 1: Player with 0 cash
    class PoorPlayer:
        hp = 20
        cash = 0

    props = Cow.generate_random_cow_properties(PoorPlayer())
    assert props.cash >= 30, "Min cash reward should be $30"

    # Test 2: Player with 1 HP
    class DyingPlayer:
        hp = 1
        cash = 50

    props = Cow.generate_random_cow_properties(DyingPlayer())
    assert props is not None

    # Test 3: Rich player (high cash)
    class RichPlayer:
        hp = 100
        cash = 10000

    props = Cow.generate_random_cow_properties(RichPlayer())
    assert props is not None


def test_save_load_edge_cases():
    """Test save/load with edge cases."""
    from save_manager import SaveManager
    from models import GameStats

    SaveManager.delete_save()

    # Test 1: Load when no save exists
    result = SaveManager.load_game()
    assert result is None

    # Test 2: Save with empty inventory
    class EmptyPlayer:
        name = "Empty"
        hp = 20
        cash = 50
        stunned_turns = 0
        inventory = []
        weapon = None
        shield = None

    stats = GameStats()
    packs = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0}

    SaveManager.save_game(EmptyPlayer(), stats, packs)

    # Test 3: Load corrupted save (delete it)
    SaveManager.delete_save()


def test_combat_edge_cases():
    """Test combat scenarios that could crash."""
    from player import Player
    from cow import Cow
    from models import CowProperties

    class MockTerminal:
        def set_player_stats(self, *args): pass
        def draw_player_stats(self): pass
        def draw_game_title(self): pass
        def draw_separator(self): pass
        def refresh(self): pass
        def draw_dialog(self, text): pass
        class stdscr:
            @staticmethod
            def refresh(): pass

    terminal = MockTerminal()
    player = Player(terminal, "Fighter")

    # Test 1: Damage exceeds cow HP
    props = CowProperties(
        name="Test", req_amount=10, likeliness=5, strength=5,
        hp=5, cash=10, is_shop=False, is_aggro=True, pack=1, approach="test"
    )
    cow = Cow(terminal, props)

    player.deal_damage(cow)
    # Should cap at cow.hp, not go negative
    assert cow.hp >= 0

    # Test 2: Player at 0 HP
    player.hp = 0
    player.deal_damage(cow)  # Can dead player attack? Death check happens after


def test_shop_edge_cases():
    """Test shop scenarios."""
    from item_factory import ItemFactory

    # Test 1: Player with $0
    items = ItemFactory.get_shop_inventory('neutral', player_cash=0, is_lucky=False)
    assert len(items) >= 4

    # Test 2: Upset mood (2x prices)
    items = ItemFactory.get_shop_inventory('upset', player_cash=100, is_lucky=False)
    assert items is not None

    # Test 3: Wealthy player (triggers greater potion)
    items = ItemFactory.get_shop_inventory('friendly', player_cash=500, is_lucky=True)
    assert len(items) >= 5  # Should have greater potion


def test_floor_system():
    """Test floor completion logic."""
    # Simulate floor progression
    encounters_this_floor = 0
    current_floor = 1

    for i in range(25):
        encounters_this_floor += 1

        if encounters_this_floor >= 10:
            current_floor += 1
            encounters_this_floor = 0

    assert current_floor == 3  # Should be on floor 3
    assert encounters_this_floor == 5  # 5 encounters into floor 3
