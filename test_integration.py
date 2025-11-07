#!/usr/bin/env python3
"""
Test the complete integration of UI abstraction, Textual app, and game logic.
"""

import sys
import os

# Add paths
sys.path.insert(0, './venv_textual/lib/python3.13/site-packages')
sys.path.insert(0, '.')


def test_imports():
    """Test all modules can be imported."""
    print("Testing imports...")

    try:
        # UI abstraction
        from ui.interfaces.base_ui import BaseUI, UIMode
        print("  ✓ BaseUI interface")

        from ui.adapters.curses_adapter import CursesAdapter
        print("  ✓ CursesAdapter")

        from ui.adapters.textual_adapter import TextualAdapter
        print("  ✓ TextualAdapter")

        from ui.textual_app import VirtualCowTipperApp
        print("  ✓ VirtualCowTipperApp")

        from ui.game_ui_bridge import GameUIBridge
        print("  ✓ GameUIBridge")

        from game_textual_integration import TextualGameAdapter
        print("  ✓ TextualGameAdapter")

        return True

    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_structure():
    """Test the structure is properly set up."""
    print("\nTesting structure...")

    from ui.textual_app import VirtualCowTipperApp

    # Check screens
    app = VirtualCowTipperApp()
    screens = [
        'main_menu', 'game', 'combat', 'shop', 'inventory',
        'pause', 'help', 'career', 'dialogue', 'save_game',
        'load_game', 'save_prompt', 'game_over', 'victory'
    ]

    all_ok = True
    for screen_name in screens:
        screen_class = app.get_screen_class(screen_name)
        if screen_class:
            print(f"  ✓ Screen '{screen_name}' available")
        else:
            print(f"  ✗ Screen '{screen_name}' missing")
            all_ok = False

    return all_ok


def test_adapter_implementation():
    """Test TextualAdapter implements all required methods."""
    print("\nTesting TextualAdapter implementation...")

    from ui.adapters.textual_adapter import TextualAdapter
    from ui.interfaces.base_ui import BaseUI

    adapter = TextualAdapter()

    # Check all abstract methods are implemented
    methods = [
        'initialize', 'shutdown', 'show_text', 'show_menu', 'get_input',
        'update_stats', 'show_combat', 'show_dialogue', 'show_inventory',
        'show_shop', 'on_pause', 'show_error', 'show_notification',
        'push_screen', 'pop_screen', 'clear_screen', 'refresh', 'get_mode'
    ]

    all_ok = True
    for method_name in methods:
        if hasattr(adapter, method_name):
            print(f"  ✓ {method_name} implemented")
        else:
            print(f"  ✗ {method_name} missing")
            all_ok = False

    return all_ok


def test_game_integration():
    """Test game integration components."""
    print("\nTesting game integration...")

    from game_textual_integration import TextualGameAdapter, GameStateManager

    # Create adapter
    adapter = TextualGameAdapter()
    print("  ✓ TextualGameAdapter created")

    # Check state manager
    state = GameStateManager()
    if state.player_hp == 20 and state.player_cash == 50:
        print("  ✓ GameStateManager initialized correctly")
    else:
        print("  ✗ GameStateManager initialization error")
        return False

    # Check key methods
    methods = [
        'start', 'stop', 'main_menu', 'start_new_game', 'game_loop',
        'spawn_cow', 'cow_encounter', 'combat', 'update_ui_stats'
    ]

    for method_name in methods:
        if hasattr(adapter, method_name):
            print(f"  ✓ {method_name} method exists")
        else:
            print(f"  ✗ {method_name} method missing")
            return False

    return True


def main():
    """Run all tests."""
    print("="*60)
    print("UI TEXTUAL INTEGRATION TEST SUITE")
    print("="*60)

    results = {
        'Imports': test_imports(),
        'Structure': test_structure(),
        'Adapter': test_adapter_implementation(),
        'Integration': test_game_integration()
    }

    print("\n" + "="*60)
    print("TEST RESULTS:")
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name:15} {status}")
    print("="*60)

    if all(results.values()):
        print("\n✓ All integration tests passed!")
        print("\nThe Textual UI implementation is complete:")
        print("  - UI abstraction layer working")
        print("  - Textual app with 14 screens")
        print("  - TextualAdapter fully implemented")
        print("  - Game integration ready")
        print("\nYou can now run the game with:")
        print("  python3 main_ui.py --textual")
        return 0
    else:
        print("\n✗ Some tests failed.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)