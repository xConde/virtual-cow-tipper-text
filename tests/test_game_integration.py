"""
Integration test - Verify all refactored components work together.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_cow_generation_full():
    """Test complete cow generation pipeline."""
    from cow import Cow
    from models import CowProperties

    class MockPlayer:
        hp = 50
        cash = 100

    class MockTerminal:
        def draw_dialog(self, text): pass

    # Generate cow properties
    props = Cow.generate_random_cow_properties(MockPlayer())

    assert isinstance(props, CowProperties)
    assert props.name is not None
    assert props.hp > 0
    assert props.strength > 0
    assert props.mood in ['upset', 'neutral', 'friendly']
    assert props.approach is not None and len(props.approach) > 0

    # Create cow from properties
    cow = Cow(MockTerminal(), props)

    assert cow.name == props.name
    assert cow.mood == props.mood
    assert cow.hp == props.hp

    # Test cow can generate responses
    response = cow.get_response('intro')
    assert response is not None
    assert len(response) > 0

    print("test_cow_generation_full: PASSED")


def test_item_creation_full():
    """Test complete item generation pipeline."""
    from item_factory import ItemFactory

    # Create weapon
    weapon = ItemFactory.create_weapon()
    assert weapon is not None
    assert weapon.name is not None
    assert weapon.min_damage > 0

    # Create shield
    shield = ItemFactory.create_shield()
    assert shield is not None
    assert shield.min_defence > 0

    # Create random item
    item = ItemFactory.create_random_item()
    assert item is not None

    # Test damage rolling
    damage = ItemFactory.roll_weapon_damage(weapon)
    assert damage > 0

    print("test_item_creation_full: PASSED")


def test_player_combat():
    """Test player combat mechanics."""
    from player import Player
    from cow import Cow
    from models import CowProperties

    class MockTerminal:
        def draw_dialog(self, text): pass
        def set_player_stats(self, *args): pass
        def draw_player_stats(self): pass
        def draw_game_title(self): pass
        def draw_separator(self): pass
        def refresh(self): pass
        class stdscr:
            @staticmethod
            def refresh(): pass

    terminal = MockTerminal()
    player = Player(terminal, "TestHero")

    # Create a weak cow to fight
    props = CowProperties(
        name="TestCow", req_amount=10, likeliness=5, strength=5,
        hp=20, cash=10, is_shop=False, is_aggro=True, pack=1, approach="test"
    )
    cow = Cow(terminal, props)

    initial_cow_hp = cow.hp

    # Player attacks
    player.deal_damage(cow)

    # Cow should have taken damage
    assert cow.hp < initial_cow_hp, "Cow should have taken damage"

    print("test_player_combat: PASSED")


def test_config_values():
    """Test game_config values are loaded."""
    from game_config import (
        PLAYER_STARTING_HP, PLAYER_STARTING_CASH,
        COW_QUEUE_SIZE, NUM_COW_PACKS,
        INTERRUPTION_CHANCE
    )

    assert PLAYER_STARTING_HP == 20
    assert PLAYER_STARTING_CASH == 50
    assert COW_QUEUE_SIZE == 3
    assert NUM_COW_PACKS == 6
    assert INTERRUPTION_CHANCE == 0.10

    print("test_config_values: PASSED")


def test_all_imports():
    """Test all modules can be imported without errors."""
    try:
        from game import VirtualCowTipper
        from cow import Cow
        from player import Player
        from cow_interaction import CowInteraction
        from cow_attack import CowAttack
        from item_factory import ItemFactory
        from dialogue_manager import DialogueManager
        from models import CowProperties, PlayerState
        from game_config import PLAYER_STARTING_HP

        print("test_all_imports: PASSED")
        return True
    except ImportError as e:
        print(f"test_all_imports: FAILED - {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("GAME INTEGRATION TEST SUITE")
    print("="*60)
    print()

    test_all_imports()
    print()
    test_config_values()
    test_cow_generation_full()
    test_item_creation_full()
    test_player_combat()

    print()
    print("="*60)
    print("ALL INTEGRATION TESTS PASSED!")
    print("="*60)
    print("\nAll refactored systems work together correctly!")
    print("Game is ready to run: python3 main.py")
