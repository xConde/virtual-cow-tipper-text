#!/usr/bin/env python3
"""
Verify the Textual application structure without running it interactively.
"""

import sys
import os

# Add venv to path
sys.path.insert(0, './venv_textual/lib/python3.13/site-packages')
sys.path.insert(0, '.')


def verify_textual_app():
    """Verify Textual app can be imported and initialized."""
    print("Verifying Textual Application Shell...")

    try:
        from ui.textual_app import VirtualCowTipperApp
        print("  ✓ VirtualCowTipperApp imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import: {e}")
        return False

    # Check all screen classes
    screens = [
        'MainMenuScreen', 'GameScreen', 'CombatScreen', 'ShopScreen',
        'InventoryScreen', 'PauseScreen', 'HelpScreen', 'CareerScreen',
        'DialogueScreen', 'SaveGameScreen', 'LoadGameScreen',
        'SavePromptScreen', 'GameOverScreen', 'VictoryScreen'
    ]

    from ui import textual_app
    for screen_name in screens:
        if hasattr(textual_app, screen_name):
            print(f"  ✓ {screen_name} defined")
        else:
            print(f"  ✗ {screen_name} missing")
            return False

    # Try to create app instance (without running)
    try:
        app = VirtualCowTipperApp()
        print("  ✓ App instance created")

        # Check key methods
        if hasattr(app, 'push_screen') and hasattr(app, 'send_event'):
            print("  ✓ Core methods present")
        else:
            print("  ✗ Missing core methods")
            return False

        # Check screen registry
        test_screens = ['main_menu', 'game', 'shop', 'combat']
        for screen_name in test_screens:
            screen_class = app.get_screen_class(screen_name)
            if screen_class:
                print(f"  ✓ Screen '{screen_name}' registered")
            else:
                print(f"  ✗ Screen '{screen_name}' not found")
                return False

    except Exception as e:
        print(f"  ✗ Failed to create app: {e}")
        return False

    return True


def verify_css():
    """Verify CSS file exists and is valid."""
    print("\nVerifying CSS styles...")

    css_path = "ui/styles/main.css"
    if os.path.exists(css_path):
        print(f"  ✓ CSS file exists: {css_path}")

        with open(css_path, 'r') as f:
            css_content = f.read()

        # Check for key sections
        sections = [
            '/* Global Styles */',
            '/* Main Menu */',
            '/* Game Screen */',
            '/* Combat Screen */',
            '/* Shop Screen */',
        ]

        for section in sections:
            if section in css_content:
                print(f"  ✓ CSS section found: {section}")
            else:
                print(f"  ✗ CSS section missing: {section}")
                return False

    else:
        print(f"  ✗ CSS file not found: {css_path}")
        return False

    return True


def main():
    """Run all verifications."""
    print("="*60)
    print("TEXTUAL APPLICATION SHELL VERIFICATION")
    print("="*60)

    app_ok = verify_textual_app()
    css_ok = verify_css()

    print("\n" + "="*60)
    print("VERIFICATION RESULTS:")
    print(f"  Textual App Structure: {'PASS' if app_ok else 'FAIL'}")
    print(f"  CSS Styles:           {'PASS' if css_ok else 'FAIL'}")
    print("="*60)

    if app_ok and css_ok:
        print("\n✓ Textual application shell is properly structured!")
        print("  - 14 screens implemented")
        print("  - Event system in place")
        print("  - CSS styling configured")
        print("  - Ready for integration with game logic")
        return 0
    else:
        print("\n✗ Some verifications failed.")
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