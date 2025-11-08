#!/usr/bin/env python3
"""
Verify the UI abstraction layer structure is correctly implemented.
Non-interactive test that doesn't require terminal capabilities.
"""

import sys
import inspect

# Add current directory to path
sys.path.insert(0, '.')


def verify_base_ui_interface():
    """Verify BaseUI interface is properly defined."""
    from ui.interfaces.base_ui import BaseUI, UIMode, MenuChoice

    print("Checking BaseUI interface...")

    # Check abstract methods
    required_methods = [
        'initialize', 'shutdown',
        'show_text', 'show_menu', 'get_input',
        'update_stats', 'show_combat', 'show_dialogue',
        'show_inventory', 'show_shop',
        'on_pause', 'show_error', 'show_notification',
        'push_screen', 'pop_screen', 'clear_screen', 'refresh',
        'get_mode'
    ]

    for method_name in required_methods:
        if hasattr(BaseUI, method_name):
            method = getattr(BaseUI, method_name)
            if inspect.isabstract(method) or callable(method):
                print(f"  ✓ {method_name} defined")
            else:
                print(f"  ✗ {method_name} not properly defined")
                return False
        else:
            print(f"  ✗ {method_name} missing")
            return False

    print("  ✓ All required methods present")

    # Check UIMode enum
    if hasattr(UIMode, 'CURSES') and hasattr(UIMode, 'TEXTUAL'):
        print("  ✓ UIMode enum properly defined")
    else:
        print("  ✗ UIMode enum incomplete")
        return False

    # Check MenuChoice dataclass
    try:
        choice = MenuChoice(index=0, label="Test", value="test")
        print("  ✓ MenuChoice dataclass works")
    except:
        print("  ✗ MenuChoice dataclass failed")
        return False

    return True


def verify_curses_adapter():
    """Verify CursesAdapter implementation."""
    from ui.adapters import CursesAdapter
    from ui.interfaces.base_ui import BaseUI

    print("\nChecking CursesAdapter...")

    # Check inheritance
    if issubclass(CursesAdapter, BaseUI):
        print("  ✓ Inherits from BaseUI")
    else:
        print("  ✗ Does not inherit from BaseUI")
        return False

    # Check all abstract methods are implemented
    adapter = CursesAdapter()
    abstract_methods = []

    for name, method in inspect.getmembers(BaseUI):
        if name.startswith('_'):
            continue
        if inspect.isabstract(method):
            if not hasattr(adapter, name) or not callable(getattr(adapter, name)):
                abstract_methods.append(name)

    if abstract_methods:
        print(f"  ✗ Missing implementations: {', '.join(abstract_methods)}")
        return False
    else:
        print("  ✓ All abstract methods implemented")

    # Check get_mode returns correct value
    from ui.interfaces.base_ui import UIMode
    if adapter.get_mode() == UIMode.CURSES:
        print("  ✓ get_mode returns correct UIMode")
    else:
        print("  ✗ get_mode returns wrong UIMode")
        return False

    return True


def verify_game_ui_bridge():
    """Verify GameUIBridge implementation."""
    from ui.game_ui_bridge import GameUIBridge, EventType, GameEvent, GameState

    print("\nChecking GameUIBridge...")

    # Check EventType enum
    expected_events = [
        'PLAYER_DAMAGED', 'COW_SPAWNED', 'COMBAT_STARTED',
        'ITEM_OBTAINED', 'GAME_OVER', 'NOTIFICATION'
    ]

    for event_name in expected_events:
        if hasattr(EventType, event_name):
            print(f"  ✓ EventType.{event_name} defined")
        else:
            print(f"  ✗ EventType.{event_name} missing")
            return False

    # Check GameEvent dataclass
    try:
        event = GameEvent(type=EventType.NOTIFICATION, data={'message': 'test'})
        print("  ✓ GameEvent dataclass works")
    except:
        print("  ✗ GameEvent dataclass failed")
        return False

    # Check GameState dataclass
    try:
        state = GameState()
        if hasattr(state, 'player_hp') and hasattr(state, 'current_floor'):
            print("  ✓ GameState dataclass properly defined")
        else:
            print("  ✗ GameState missing fields")
            return False
    except:
        print("  ✗ GameState dataclass failed")
        return False

    return True


def verify_ui_factory():
    """Verify UIFactory implementation."""
    from ui.ui_factory import UIFactory
    from ui.interfaces.base_ui import UIMode

    print("\nChecking UIFactory...")

    # Check factory methods
    required_methods = ['register', 'create', 'get_current',
                       'list_registered', 'is_registered', 'clear_registry']

    for method_name in required_methods:
        if hasattr(UIFactory, method_name):
            print(f"  ✓ {method_name} defined")
        else:
            print(f"  ✗ {method_name} missing")
            return False

    # Test registration
    UIFactory.clear_registry()
    from ui.adapters import CursesAdapter
    UIFactory.register(UIMode.CURSES, CursesAdapter)

    if UIFactory.is_registered(UIMode.CURSES):
        print("  ✓ Registration works")
    else:
        print("  ✗ Registration failed")
        return False

    registered = UIFactory.list_registered()
    if UIMode.CURSES in registered:
        print("  ✓ list_registered works")
    else:
        print("  ✗ list_registered failed")
        return False

    return True


def main():
    """Run all verification tests."""
    print("="*60)
    print("UI ABSTRACTION LAYER STRUCTURE VERIFICATION")
    print("="*60)

    results = {
        'BaseUI Interface': verify_base_ui_interface(),
        'CursesAdapter': verify_curses_adapter(),
        'GameUIBridge': verify_game_ui_bridge(),
        'UIFactory': verify_ui_factory()
    }

    # Summary
    print("\n" + "="*60)
    print("VERIFICATION RESULTS:")
    for component, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {component:20} {status}")
    print("="*60)

    if all(results.values()):
        print("\n✓ All structure verification passed!")
        print("\nThe UI abstraction layer is correctly implemented.")
        print("The structure allows for both Curses and Textual implementations.")
        print("\nNote: Interactive testing requires a proper terminal environment.")
        return 0
    else:
        print("\n✗ Some verifications failed. Please review the errors above.")
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