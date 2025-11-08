#!/usr/bin/env python3
"""
Test the Textual application shell.
"""

import sys
import os

# Add venv to path
sys.path.insert(0, './venv_textual/lib/python3.13/site-packages')
sys.path.insert(0, '.')

from ui.textual_app import VirtualCowTipperApp


def test_app():
    """Test the Textual app."""
    print("Starting Textual app test...")
    print("Press Ctrl+Q to quit")
    print("-" * 40)

    try:
        app = VirtualCowTipperApp()
        app.run()
        print("\nApp closed successfully!")
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = test_app()
    sys.exit(exit_code)