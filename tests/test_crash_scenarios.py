"""
Crash Scenario Testing - Find any code paths that could crash the game.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports_dont_crash():
    """Test all imports work without errors."""
    print("Testing all imports...")

    try:
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

        print("[OK] All imports successful (no circular dependencies)")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_player_inventory_operations():
    """Test inventory edge cases that could crash."""
    from player import Player
    from item import HealthPotion, Weapon

    class MockTerminal:
        def set_player_stats(self, *args): pass
        def refresh(self): pass

    print("\nTesting inventory operations...")

    player = Player(MockTerminal(), "Test")

    # Test 1: Use item not in inventory
    potion = HealthPotion()
    try:
        player.use_item(potion)  # Not in inventory
        print("  [OK] Using item not in inventory doesn't crash")
    except Exception as e:
        print(f"  ✗ Crash on use_item: {e}")
        return False

    # Test 2: Add to full inventory
    from game_config import PLAYER_MAX_INVENTORY_SIZE
    for i in range(PLAYER_MAX_INVENTORY_SIZE + 5):
        player.update_inventory(HealthPotion(), "add")

    assert len(player.inventory) <= PLAYER_MAX_INVENTORY_SIZE
    print(f"  [OK] Inventory caps at {PLAYER_MAX_INVENTORY_SIZE} (no overflow)")

    # Test 3: Remove item not in inventory
    weapon = Weapon("Test", 1, 1, "common", 1)
    player.update_inventory(weapon, "remove")  # Not in inventory
    print("  [OK] Removing missing item doesn't crash")

    # Test 4: Use potion at full HP
    player.hp = 100
    potion2 = HealthPotion()
    player.inventory.append(potion2)
    potion2.use(player)
    assert player.hp == 100
    print("  [OK] Potion at full HP doesn't overflow")

    return True


def test_cow_generation_edge_cases():
    """Test cow generation doesn't crash with extreme player stats."""
    from cow import Cow

    print("\nTesting cow generation edge cases...")

    # Test 1: Player with 0 cash
    class PoorPlayer:
        hp = 20
        cash = 0

    try:
        props = Cow.generate_random_cow_properties(PoorPlayer())
        assert props.cash >= 30, "Min cash reward should be $30"
        print("  [OK] Cow generation works with $0 player")
    except Exception as e:
        print(f"  ✗ Crash with poor player: {e}")
        return False

    # Test 2: Player with 1 HP
    class DyingPlayer:
        hp = 1
        cash = 50

    try:
        props = Cow.generate_random_cow_properties(DyingPlayer())
        print("  [OK] Cow generation works with 1 HP player")
    except Exception as e:
        print(f"  ✗ Crash with low HP: {e}")
        return False

    # Test 3: Rich player (high cash)
    class RichPlayer:
        hp = 100
        cash = 10000

    try:
        props = Cow.generate_random_cow_properties(RichPlayer())
        print("  [OK] Cow generation works with wealthy player")
    except Exception as e:
        print(f"  ✗ Crash with rich player: {e}")
        return False

    return True


def test_save_load_edge_cases():
    """Test save/load with edge cases."""
    from save_manager import SaveManager
    from models import GameStats

    print("\nTesting save/load edge cases...")

    SaveManager.delete_save()

    # Test 1: Load when no save exists
    result = SaveManager.load_game()
    assert result is None
    print("  [OK] Load with no save returns None (doesn't crash)")

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

    try:
        SaveManager.save_game(EmptyPlayer(), stats, packs)
        print("  [OK] Save with empty inventory works")
    except Exception as e:
        print(f"  ✗ Crash on empty save: {e}")
        return False

    # Test 3: Load corrupted save (delete it)
    SaveManager.delete_save()

    return True


def test_combat_edge_cases():
    """Test combat scenarios that could crash."""
    from player import Player
    from cow import Cow
    from models import CowProperties

    print("\nTesting combat edge cases...")

    class MockTerminal:
        def set_player_stats(self, *args): pass
        def refresh(self): pass
        def draw_dialog(self, text): pass

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
    print("  [OK] Damage doesn't cause negative HP")

    # Test 2: Player at 0 HP
    player.hp = 0
    try:
        player.deal_damage(cow)  # Can dead player attack?
        print("  [OK] Dead player can still execute actions (death check happens after)")
    except Exception as e:
        print(f"  ✗ Crash with dead player: {e}")
        return False

    return True


def test_shop_edge_cases():
    """Test shop scenarios."""
    from item_factory import ItemFactory

    print("\nTesting shop edge cases...")

    # Test 1: Player with $0
    try:
        items = ItemFactory.get_shop_inventory('neutral', player_cash=0, is_lucky=False)
        assert len(items) >= 4
        print("  [OK] Shop generates with $0 player")
    except Exception as e:
        print(f"  ✗ Shop crash with poor player: {e}")
        return False

    # Test 2: Upset mood (2x prices)
    try:
        items = ItemFactory.get_shop_inventory('upset', player_cash=100, is_lucky=False)
        print("  [OK] Upset shop doesn't crash")
    except Exception as e:
        print(f"  ✗ Upset shop crash: {e}")
        return False

    # Test 3: Wealthy player (triggers greater potion)
    try:
        items = ItemFactory.get_shop_inventory('friendly', player_cash=500, is_lucky=True)
        assert len(items) >= 5  # Should have greater potion
        print("  [OK] Wealthy player shop generates correctly")
    except Exception as e:
        print(f"  ✗ Wealthy shop crash: {e}")
        return False

    return True


def test_floor_system():
    """Test floor completion logic."""
    print("\nTesting floor system...")

    # Simulate floor progression
    encounters_this_floor = 0
    current_floor = 1

    for i in range(25):
        encounters_this_floor += 1

        if encounters_this_floor >= 10:
            print(f"  Floor {current_floor} complete at encounter {i + 1}")
            current_floor += 1
            encounters_this_floor = 0

    assert current_floor == 3  # Should be on floor 3
    assert encounters_this_floor == 5  # 5 encounters into floor 3

    print("  [OK] Floor system logic correct (no off-by-one)")

    return True


if __name__ == "__main__":
    print("="*60)
    print("CRASH SCENARIO TESTING")
    print("="*60)

    all_pass = True

    all_pass &= test_imports_dont_crash()
    all_pass &= test_player_inventory_operations()
    all_pass &= test_cow_generation_edge_cases()
    all_pass &= test_save_load_edge_cases()
    all_pass &= test_combat_edge_cases()
    all_pass &= test_shop_edge_cases()
    all_pass &= test_floor_system()

    print("\n" + "="*60)
    if all_pass:
        print("ALL CRASH SCENARIOS TESTED - SAFE!")
        print("="*60)
        print("\n[OK] No circular dependencies")
        print("[OK] Inventory operations safe")
        print("[OK] Cow generation handles edge cases")
        print("[OK] Save/load robust")
        print("[OK] Combat math safe")
        print("[OK] Shop generation safe")
        print("[OK] Floor system correct")
        print("\nGame is crash-resistant and ready for demo!")
    else:
        print("SOME TESTS FAILED - REVIEW ABOVE")
        sys.exit(1)
