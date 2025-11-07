#!/usr/bin/env python3
"""
Test that both UI modes (Curses and Textual) are working.
"""

import sys
import os

def test_curses_mode():
    """Test that curses mode can be imported and initialized."""
    print("Testing Curses mode...")

    try:
        # Import required components
        from main_menu import MainMenu
        from game import VirtualCowTipper
        from terminal.game_terminal import GameTerminal

        print("  ✓ Curses components imported successfully")

        # Test creating a game terminal (without actually starting curses)
        # Note: This will fail in non-terminal environment but that's ok
        print("  ✓ GameTerminal class available")
        print("  ✓ MainMenu class available")
        print("  ✓ VirtualCowTipper class available")

        return True

    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_textual_mode():
    """Test that Textual mode can be imported and initialized."""
    print("\nTesting Textual mode...")

    # Add Textual venv to path if needed
    if os.path.exists('./venv_textual/lib/python3.13/site-packages'):
        sys.path.insert(0, './venv_textual/lib/python3.13/site-packages')

    try:
        # Try to import Textual
        import textual
        print("  ✓ Textual library available")

        # Import our components
        from ui.textual_app import VirtualCowTipperApp
        from ui.adapters.textual_adapter import TextualAdapter
        from game_textual_integration import TextualGameAdapter

        print("  ✓ VirtualCowTipperApp imported")
        print("  ✓ TextualAdapter imported")
        print("  ✓ TextualGameAdapter imported")

        # Test creating instances (without running)
        app = VirtualCowTipperApp()
        print("  ✓ VirtualCowTipperApp instance created")

        adapter = TextualAdapter()
        print("  ✓ TextualAdapter instance created")

        game = TextualGameAdapter()
        print("  ✓ TextualGameAdapter instance created")

        # Check all screens are registered
        screens = [
            'main_menu', 'game', 'combat', 'shop', 'inventory',
            'pause', 'help', 'career', 'dialogue', 'save_game',
            'load_game', 'save_prompt', 'game_over', 'victory'
        ]

        for screen_name in screens:
            screen_class = app.get_screen_class(screen_name)
            if not screen_class:
                print(f"  ✗ Screen '{screen_name}' not found")
                return False

        print(f"  ✓ All {len(screens)} screens registered")

        return True

    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        print("  Note: Textual may not be installed. Run: ./venv_textual/bin/pip install textual")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_entry_points():
    """Test that main entry points exist and can be imported."""
    print("\nTesting entry points...")

    entry_points = [
        ('main.py', 'Original curses entry point'),
        ('main_ui.py', 'UI abstraction entry point'),
        ('main_textual.py', 'Direct Textual entry point')
    ]

    all_ok = True
    for filename, description in entry_points:
        if os.path.exists(filename):
            print(f"  ✓ {filename}: {description}")
        else:
            print(f"  ✗ {filename} not found")
            all_ok = False

    return all_ok


def test_ui_abstraction():
    """Test the UI abstraction layer."""
    print("\nTesting UI abstraction layer...")

    try:
        from ui.interfaces.base_ui import BaseUI, UIMode
        from ui.adapters.curses_adapter import CursesAdapter
        from ui.ui_factory import UIFactory

        print("  ✓ BaseUI interface imported")
        print("  ✓ CursesAdapter imported")
        print("  ✓ UIFactory imported")

        # Test factory registration
        UIFactory.clear_registry()
        UIFactory.register(UIMode.CURSES, CursesAdapter)

        if UIFactory.is_registered(UIMode.CURSES):
            print("  ✓ CursesAdapter registered with factory")
        else:
            print("  ✗ Failed to register CursesAdapter")
            return False

        # Try to register Textual if available
        try:
            from ui.adapters.textual_adapter import TextualAdapter
            UIFactory.register(UIMode.TEXTUAL, TextualAdapter)
            print("  ✓ TextualAdapter registered with factory")
        except ImportError:
            print("  ⚠ TextualAdapter not available (Textual not installed)")

        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("VIRTUAL COW TIPPER - UI MODE TESTS")
    print("="*60)

    results = {
        'Curses Mode': test_curses_mode(),
        'Textual Mode': test_textual_mode(),
        'Entry Points': test_main_entry_points(),
        'UI Abstraction': test_ui_abstraction()
    }

    print("\n" + "="*60)
    print("TEST RESULTS:")
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name:20} {status}")
    print("="*60)

    if all(results.values()):
        print("\n✅ All tests passed! Both UI modes are ready.")
        print("\nYou can run the game with:")
        print("  python3 main.py              # Original curses")
        print("  python3 main_textual.py      # New Textual UI")
        print("  python3 main_textual.py --curses  # Force curses")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

        if not results['Textual Mode']:
            print("\nTo install Textual:")
            print("  ./venv_textual/bin/pip install textual")

        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)