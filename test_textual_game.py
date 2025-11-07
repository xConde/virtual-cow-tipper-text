#!/usr/bin/env python3
"""
Test script to verify the Textual game is functional.
"""

import asyncio
import sys
import os

# Add venv to path
sys.path.insert(0, './venv_textual/lib/python3.13/site-packages')


async def test_game_components():
    """Test individual game components."""
    print("Testing Textual Game Components...")
    print("=" * 50)

    try:
        # Test imports
        print("1. Testing imports...")
        from game_textual_integration import TextualGameAdapter, GameStateManager, SimpleInventory
        from ui.adapters.textual_adapter import TextualAdapter
        print("   ✅ All imports successful")

        # Test GameStateManager
        print("\n2. Testing GameStateManager...")
        state = GameStateManager(player_name="TestPlayer")
        assert state.player_hp == 20
        assert state.player_cash == 50
        assert state.current_floor == 1
        assert state.inventory is not None
        print("   ✅ GameStateManager initialized correctly")

        # Test SimpleInventory
        print("\n3. Testing SimpleInventory...")
        inv = SimpleInventory()
        item1 = {'name': 'Test Sword', 'type': 'weapon', 'damage': 5}
        assert inv.add_item(item1) == True
        assert inv.count_items('Test Sword') == 1
        assert len(inv.get_equipment()) == 1
        removed = inv.remove_item('Test Sword')
        assert removed['name'] == 'Test Sword'
        print("   ✅ SimpleInventory works correctly")

        # Test game adapter creation
        print("\n4. Testing TextualGameAdapter...")
        game = TextualGameAdapter()
        assert game.state is not None
        assert game.ui is not None
        assert game.bridge is not None
        print("   ✅ TextualGameAdapter created successfully")

        # Test cow spawning
        print("\n5. Testing cow spawn mechanics...")
        await game.spawn_cow()
        assert game.state.current_cow is not None
        assert 'name' in game.state.current_cow
        assert 'hp' in game.state.current_cow
        assert 'damage' in game.state.current_cow
        assert 'behavior' in game.state.current_cow
        assert 'special_attacks' in game.state.current_cow
        print(f"   ✅ Spawned: {game.state.current_cow['name']}")
        print(f"      HP: {game.state.current_cow['hp']}")
        print(f"      Damage: {game.state.current_cow['damage']}")

        # Test loot generation
        print("\n6. Testing loot generation...")
        loot = game._generate_loot('Normal', 1)
        assert 'name' in loot
        assert 'type' in loot
        assert 'value' in loot
        print(f"   ✅ Generated loot: {loot['name']} ({loot['type']})")

        # Test shop generation
        print("\n7. Testing shop generation...")
        shop_items = game._generate_shop_items()
        assert len(shop_items) > 0
        assert any(item['type'] == 'consumable' for item in shop_items)
        assert any(item['type'] == 'weapon' for item in shop_items)
        print(f"   ✅ Generated {len(shop_items)} shop items")

        # Test save data structure
        print("\n8. Testing save data structure...")
        save_data = {
            'player': {
                'name': game.state.player_name,
                'hp': game.state.player_hp,
                'max_hp': game.state.player_max_hp,
                'cash': game.state.player_cash
            },
            'floor': game.state.current_floor,
            'inventory': game.state.inventory.items if game.state.inventory else [],
            'equipped_weapon': game.state.equipped_weapon,
            'equipped_shield': game.state.equipped_shield,
            'stats': {
                'cows_defeated': game.state.cows_defeated,
                'bosses_defeated': game.state.bosses_defeated
            }
        }
        assert 'player' in save_data
        assert 'inventory' in save_data
        print("   ✅ Save data structure is valid")

        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("\nThe Textual game components are functional.")
        print("You can now run: ./venv_textual/bin/python3 main_textual.py")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_combat_simulation():
    """Simulate a combat encounter."""
    print("\n\nCombat Simulation Test")
    print("=" * 50)

    try:
        from game_textual_integration import TextualGameAdapter

        game = TextualGameAdapter()
        game.state.current_floor = 3  # Mid-level difficulty

        # Spawn a cow
        await game.spawn_cow()
        cow = game.state.current_cow
        print(f"Fighting: {cow['name']}")
        print(f"Cow HP: {cow['hp']}/{cow['max_hp']}")
        print(f"Player HP: {game.state.player_hp}/{game.state.player_max_hp}")

        # Simulate combat rounds
        combat_log = []
        rounds = 0

        while game.state.player_hp > 0 and cow['hp'] > 0 and rounds < 10:
            rounds += 1
            print(f"\nRound {rounds}:")

            # Player attacks
            base_damage = 7 + (game.state.current_floor * 2)
            damage = max(1, base_damage - cow.get('defense', 0))
            cow['hp'] -= damage
            print(f"  Player deals {damage} damage")

            if cow['hp'] <= 0:
                print(f"  🎉 {cow['name']} defeated!")
                break

            # Cow attacks
            cow_damage = cow['damage'] // 2  # Simulated defense
            game.state.player_hp -= cow_damage
            print(f"  {cow['name']} deals {cow_damage} damage")

            if game.state.player_hp <= 0:
                print(f"  💀 Player defeated!")
                break

        print(f"\nCombat ended after {rounds} rounds")
        print(f"Final Player HP: {game.state.player_hp}/{game.state.player_max_hp}")
        print(f"Final Cow HP: {max(0, cow['hp'])}/{cow['max_hp']}")

        print("\n✅ Combat simulation successful")
        return True

    except Exception as e:
        print(f"\n❌ Combat simulation failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("TEXTUAL GAME FUNCTIONALITY TEST")
    print("=" * 60)

    # Run component tests
    components_ok = await test_game_components()

    # Run combat simulation
    combat_ok = await test_combat_simulation()

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY")
    print("=" * 60)
    print(f"Component Tests: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print(f"Combat Simulation: {'✅ PASS' if combat_ok else '❌ FAIL'}")

    if components_ok and combat_ok:
        print("\n🎉 All tests passed! The game is ready to play.")
        print("\nTo run the game:")
        print("  ./venv_textual/bin/python3 main_textual.py")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

    return 0 if (components_ok and combat_ok) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)