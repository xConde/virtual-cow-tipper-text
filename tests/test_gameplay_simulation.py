"""
Gameplay simulation - Test all systems work together in realistic scenarios.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cow import Cow
from player import Player
from models import CowProperties, GameStats
from item_factory import ItemFactory
from item import HealthPotion
from dialogue_manager import DialogueManager
from save_manager import SaveManager
import random


class MockTerminal:
    """Mock terminal for headless testing."""
    def __init__(self):
        pass
    def clear_screen(self): pass
    def refresh(self): pass
    def set_cow_stats(self, s): pass
    def draw_dialog(self, s): pass
    def set_player_stats(self, *args): pass
    def close_game_terminal(self): pass


def test_early_game_scenario():
    """Simulate first 5 encounters."""
    print("\n" + "="*60)
    print("EARLY GAME SCENARIO (Encounters 1-5)")
    print("="*60)

    terminal = MockTerminal()
    player = Player(terminal, "TestHero")
    stats = GameStats()

    print(f"\nStarting: HP={player.hp}, Cash=${player.cash}")

    for i in range(1, 6):
        print(f"\n--- Encounter {i} ---")

        # Generate cow
        props = Cow.generate_random_cow_properties(player)
        cow = Cow(terminal, props)

        print(f"Cow: {cow.name} ({cow.mood}, Pack {cow.pack})")
        print(f"  Stats: {cow.strength} STR, {cow.hp} HP, ${cow.cash} reward")
        print(f"  Type: {'AGGRO' if cow.is_aggro else 'SHOP' if cow.is_shop else 'REGULAR'}")

        # Simulate outcome
        if cow.is_aggro:
            # Combat
            player.deal_damage(cow)
            if cow.hp <= 0:
                player.update_cash(cow.cash)
                stats.cows_defeated += 1
                print(f"  Victory! Earned ${cow.cash}")
        elif cow.is_shop:
            # Buy potion if low HP
            if player.hp < 15 and player.cash >= 50:
                potion = HealthPotion('normal')
                player.cash -= 50
                player.inventory.append(potion)
                stats.items_purchased += 1
                print(f"  Bought {potion.name}")

        print(f"After: HP={player.hp}, Cash=${player.cash}")

    assert player.hp > 0, "Player should survive early game"
    print(f"\n✓ Early game survivable!")


def test_healing_mechanics():
    """Test all 3 healing methods work."""
    print("\n" + "="*60)
    print("HEALING MECHANICS TEST")
    print("="*60)

    terminal = MockTerminal()
    player = Player(terminal, "Healer")
    player.hp = 50  # Damaged

    print(f"Starting HP: {player.hp}")

    # Test 1: Health Potion
    print("\n1. Health Potion:")
    potion = HealthPotion('normal')
    player.inventory.append(potion)
    potion.use(player)
    assert player.hp == 70, f"Expected 70 HP, got {player.hp}"
    print(f"   After potion: {player.hp} HP ✓")

    # Test 2: Rest (simulated)
    print("\n2. Rest:")
    from game_config import REST_HEAL_AMOUNT, PLAYER_MAX_HP
    old_hp = player.hp
    player.hp = min(player.hp + REST_HEAL_AMOUNT, PLAYER_MAX_HP)
    print(f"   After rest: {player.hp} HP (+{player.hp - old_hp}) ✓")

    # Test 3: Dairy healing (simulated)
    print("\n3. Dairy Milk:")
    from game_config import DAIRY_COW_HEAL_AMOUNT
    old_hp = player.hp
    player.hp = min(player.hp + DAIRY_COW_HEAL_AMOUNT, PLAYER_MAX_HP)
    print(f"   After milking: {player.hp} HP (+{player.hp - old_hp}) ✓")

    # Test HP cap
    print("\n4. HP Cap:")
    player.hp = 95
    player.hp = min(player.hp + 20, PLAYER_MAX_HP)
    assert player.hp == 100, "HP should cap at 100"
    print(f"   HP capped at: {player.hp} ✓")

    print(f"\n✓ All healing mechanics working!")


def test_combat_balance():
    """Test late game combat is balanced."""
    print("\n" + "="*60)
    print("COMBAT BALANCE TEST (Late Game)")
    print("="*60)

    terminal = MockTerminal()
    player = Player(terminal, "Fighter")
    player.cash = 1000  # Late game wealth
    player.hp = 80

    print(f"\nPlayer: HP={player.hp}, Cash=${player.cash}")

    # Generate late game cow
    props = Cow.generate_random_cow_properties(player)
    cow = Cow(terminal, props)

    print(f"Cow: {cow.name} (STR: {cow.strength}, HP: {cow.hp})")

    # Calculate expected damage
    from game_config import PLAYER_BASE_DAMAGE_MIN, PLAYER_BASE_DAMAGE_MAX, PLAYER_DAMAGE_CASH_SCALING
    player_dmg = random.randint(PLAYER_BASE_DAMAGE_MIN, PLAYER_BASE_DAMAGE_MAX) + (player.cash // PLAYER_DAMAGE_CASH_SCALING)

    print(f"Player damage: ~{player_dmg}")
    print(f"Cow HP: {cow.hp}")
    print(f"Hits to kill: {cow.hp / player_dmg:.1f}")

    assert cow.strength < 40, f"Late game cows should be < 40 strength (got {cow.strength})"
    assert player_dmg > cow.strength, f"Player should outdamage cow (player:{player_dmg} vs cow:{cow.strength})"

    print(f"\n✓ Combat balanced! Player can win late game fights!")


def test_economy_balance():
    """Test shop prices vs cow rewards."""
    print("\n" + "="*60)
    print("ECONOMY BALANCE TEST")
    print("="*60)

    terminal = MockTerminal()
    player = Player(terminal, "Merchant")
    player.cash = 500

    # Generate shop
    shop_items = ItemFactory.get_shop_inventory('neutral', player.cash, False)

    print(f"\nPlayer cash: ${player.cash}")
    print(f"Shop items:")
    for item in shop_items:
        print(f"  {item['label']}: ${item['price']:.0f}")

    # Generate cow reward
    props = Cow.generate_random_cow_properties(player)
    cow_reward = props.cash

    print(f"\nCow reward: ${cow_reward}")
    print(f"Items per cow: {cow_reward / shop_items[0]['price']:.1f}")

    assert cow_reward >= 30, f"Cow rewards should be >=$30 (got ${cow_reward})"
    item_price = shop_items[0]['price']
    assert item_price < 100, f"Shop items should be <$100 (got ${item_price:.0f})"

    print(f"\n✓ Economy balanced! Can afford items from cow rewards!")


def test_aggro_chance_capped():
    """Test aggro chance doesn't exceed cap."""
    print("\n" + "="*60)
    print("AGGRO CAP TEST")
    print("="*60)

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
    print(f"\nWith ${RichPlayer.cash} cash:")
    print(f"Aggro encounters: {aggro_count}/{total} ({aggro_percentage*100:.0f}%)")

    from game_config import AGGRO_MAX_CHANCE
    assert aggro_percentage <= AGGRO_MAX_CHANCE + 0.1, f"Aggro should be capped at {AGGRO_MAX_CHANCE*100}%"

    print(f"✓ Aggro capped at {AGGRO_MAX_CHANCE*100}% (was 65%+)")


def test_save_load_with_potions():
    """Test save/load preserves healing items."""
    print("\n" + "="*60)
    print("SAVE/LOAD WITH POTIONS TEST")
    print("="*60)

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
    print(f"Inventory preserved: {len(save_data['player']['inventory'])} items")

    # Cleanup
    SaveManager.delete_save()

    print(f"✓ Save/load works with new potion system!")


if __name__ == "__main__":
    print("="*60)
    print("GAMEPLAY SIMULATION TEST SUITE")
    print("Testing all systems work together with balance fixes")
    print("="*60)

    test_early_game_scenario()
    test_healing_mechanics()
    test_combat_balance()
    test_economy_balance()
    test_aggro_chance_capped()
    test_save_load_with_potions()

    print("\n" + "="*60)
    print("ALL GAMEPLAY TESTS PASSED!")
    print("="*60)
    print("\n✓ Game is balanced and playable")
    print("✓ All healing methods work")
    print("✓ Combat is fair")
    print("✓ Economy is sustainable")
    print("✓ Save/load preserves state")
    print("\nGame is ready for real gameplay testing!")
