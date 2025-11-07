#!/usr/bin/env python3
"""
Test script for the UI abstraction layer.
Tests both CursesAdapter and basic UI functionality.
"""

import asyncio
import sys
import traceback

# Add current directory to path
sys.path.insert(0, '.')

from ui.ui_factory import UIFactory
from ui.interfaces.base_ui import UIMode, MenuChoice
from ui.adapters import CursesAdapter
from ui.game_ui_bridge import GameUIBridge, EventType, GameEvent

# Try to import TextualAdapter if available
try:
    from ui.adapters import TextualAdapter
    TEXTUAL_AVAILABLE = True
except ImportError:
    TextualAdapter = None
    TEXTUAL_AVAILABLE = False


async def test_curses_adapter():
    """Test the CursesAdapter implementation."""
    print("Testing CursesAdapter...")

    # Register adapter
    UIFactory.register(UIMode.CURSES, CursesAdapter)

    # Create UI
    ui = UIFactory.create(UIMode.CURSES)

    try:
        # Initialize
        await ui.initialize()
        print("✓ UI initialized")

        # Test 1: Show text
        await ui.show_text(
            "Welcome to UI Abstraction Test!\n"
            "This tests the CursesAdapter implementation.\n"
            "Press any key to continue...",
            style="info"
        )
        print("✓ Text display works")

        # Test 2: Show menu
        result = await ui.show_menu(
            ["Option 1", "Option 2", "Option 3", "Exit"],
            title="Test Menu",
            allow_cancel=True
        )

        if result:
            await ui.show_text(
                f"You selected: {result.label} (index: {result.index})",
                style="success",
                duration=2
            )
        else:
            await ui.show_text("Menu cancelled", style="warning", duration=2)
        print("✓ Menu system works")

        # Test 3: Get input
        name = await ui.get_input(
            "Enter your name",
            default="Player"
        )
        await ui.show_text(f"Hello, {name}!", duration=2)
        print("✓ Input system works")

        # Test 4: Update stats
        await ui.update_stats(
            {
                'hp': 18,
                'max_hp': 20,
                'cash': 100,
                'floor': 1,
                'weapon': 'Rusty Sword',
                'shield': None
            },
            {
                'name': 'Test Cow',
                'hp': (10, 15),
                'type': 'Normal',
                'mood': 'Aggressive'
            }
        )
        await asyncio.sleep(2)
        print("✓ Stats display works")

        # Test 5: Show dialogue
        choice = await ui.show_dialogue(
            "Mysterious Cow",
            "Moo? What brings you here, traveler?",
            ["I'm here to tip cows", "Just passing through", "None of your business"]
        )
        if choice is not None:
            await ui.show_text(
                f"You chose response #{choice + 1}",
                duration=2
            )
        print("✓ Dialogue system works")

        # Test 6: Notifications
        await ui.show_notification("This is an info notification", "info")
        await asyncio.sleep(1)
        await ui.show_notification("This is a success notification", "success")
        await asyncio.sleep(1)
        await ui.show_notification("This is a warning notification", "warning")
        await asyncio.sleep(1)
        print("✓ Notification system works")

        # Test 7: Error handling
        await ui.show_error("This is a non-fatal error", fatal=False)
        print("✓ Error display works")

        # Final message
        await ui.show_text(
            "=== TEST COMPLETE ===\n\n"
            "All UI abstraction tests passed!\n"
            "The CursesAdapter is working correctly.\n\n"
            "Press any key to exit...",
            style="success"
        )

        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        await ui.shutdown()
        print("✓ UI shutdown complete")


async def test_game_bridge():
    """Test the GameUIBridge."""
    print("\nTesting GameUIBridge...")

    # Register adapter
    UIFactory.register(UIMode.CURSES, CursesAdapter)
    ui = UIFactory.create(UIMode.CURSES)

    # Create bridge
    bridge = GameUIBridge(ui)

    try:
        await bridge.start()
        print("✓ Bridge started")

        # Send test events
        await bridge.send_event(
            GameEvent(
                type=EventType.NOTIFICATION,
                data={'message': 'Bridge test started', 'type': 'info'}
            )
        )

        await asyncio.sleep(1)

        await bridge.send_event(
            GameEvent(
                type=EventType.PLAYER_DAMAGED,
                data={'hp': 15, 'damage': 5}
            )
        )

        await asyncio.sleep(1)

        await bridge.send_event(
            GameEvent(
                type=EventType.ITEM_OBTAINED,
                data={'item': {'name': 'Health Potion'}}
            )
        )

        await asyncio.sleep(2)

        print("✓ Events processed")

        return True

    except Exception as e:
        print(f"✗ Bridge test failed: {e}")
        traceback.print_exc()
        return False

    finally:
        await bridge.stop()
        print("✓ Bridge stopped")


async def main():
    """Run all tests."""
    print("="*60)
    print("UI ABSTRACTION LAYER TEST SUITE")
    print("="*60)

    # Test CursesAdapter
    curses_result = await test_curses_adapter()

    # Test GameUIBridge
    bridge_result = await test_game_bridge()

    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS:")
    print(f"  CursesAdapter: {'PASS' if curses_result else 'FAIL'}")
    print(f"  GameUIBridge:  {'PASS' if bridge_result else 'FAIL'}")
    print("="*60)

    if curses_result and bridge_result:
        print("\n✓ All tests passed! UI abstraction layer is working.")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        traceback.print_exc()
        sys.exit(1)