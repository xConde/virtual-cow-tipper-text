"""
Test save/load system.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from save_manager import SaveManager
from models import GameStats


def test_save_file_creation():
    """Test that save directory and file can be created."""
    # Clean up any existing save
    SaveManager.delete_save()

    assert not SaveManager.save_exists(), "Save should not exist initially"

    # Create mock player
    class MockPlayer:
        name = "TestHero"
        hp = 50
        cash = 200
        stunned_turns = 0
        inventory = []
        weapon = None
        shield = None

    stats = GameStats(
        cows_defeated=10,
        cash_earned=500,
        legendary_items_found=1
    )

    cow_packs = {1: 2.0, 2: -1.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0}

    # Save game
    success = SaveManager.save_game(MockPlayer(), stats, cow_packs)
    assert success, "Save should succeed"
    assert SaveManager.save_exists(), "Save file should exist after save"

    print("test_save_file_creation: PASSED")


def test_save_load_roundtrip():
    """Test that saved data can be loaded back correctly."""
    SaveManager.delete_save()

    # Create mock data
    class MockPlayer:
        name = "LoadTest"
        hp = 75
        cash = 350
        stunned_turns = 2
        inventory = []
        weapon = None
        shield = None

    stats = GameStats(
        cows_defeated=25,
        cash_earned=1000,
        shops_visited=5
    )

    cow_packs = {1: 5.0, 2: -3.0, 3: 1.0, 4: 0.0, 5: 2.0, 6: -1.0}

    # Save
    SaveManager.save_game(MockPlayer(), stats, cow_packs)

    # Load
    loaded = SaveManager.load_game()

    assert loaded is not None, "Load should succeed"
    assert loaded['player']['name'] == "LoadTest"
    assert loaded['player']['hp'] == 75
    assert loaded['player']['cash'] == 350
    assert loaded['stats']['cows_defeated'] == 25
    assert loaded['stats']['cash_earned'] == 1000
    assert loaded['cow_packs'][1] == 5.0
    assert loaded['cow_packs'][2] == -3.0

    print("test_save_load_roundtrip: PASSED")


def test_delete_save():
    """Test save file deletion."""
    # Ensure save exists
    if not SaveManager.save_exists():
        class MockPlayer:
            name, hp, cash, stunned_turns = "Test", 20, 50, 0
            inventory, weapon, shield = [], None, None
        SaveManager.save_game(MockPlayer(), GameStats(), {1: 0.0})

    assert SaveManager.save_exists(), "Save should exist before delete"

    # Delete
    success = SaveManager.delete_save()
    assert success, "Delete should succeed"
    assert not SaveManager.save_exists(), "Save should not exist after delete"

    print("test_delete_save: PASSED")


def test_load_nonexistent_save():
    """Test loading when no save exists."""
    SaveManager.delete_save()

    loaded = SaveManager.load_game()
    assert loaded is None, "Load should return None when no save exists"

    print("test_load_nonexistent_save: PASSED")


if __name__ == "__main__":
    print("="*60)
    print("SAVE/LOAD SYSTEM TESTS")
    print("="*60)
    print()

    test_save_file_creation()
    test_save_load_roundtrip()
    test_delete_save()
    test_load_nonexistent_save()

    # Cleanup
    SaveManager.delete_save()

    print()
    print("="*60)
    print("ALL SAVE/LOAD TESTS PASSED!")
    print("="*60)
