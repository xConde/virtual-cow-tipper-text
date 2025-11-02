#!/usr/bin/env python3
"""
Main entry point using the new UI abstraction layer.
Supports both Curses and Textual UI modes.
"""

import asyncio
import sys
import os
from typing import Optional

# Add UI package to path
sys.path.insert(0, '.')

from ui.ui_factory import UIFactory
from ui.interfaces.base_ui import UIMode
from ui.adapters import CursesAdapter, TextualAdapter
from ui.game_ui_bridge import GameUIBridge


async def main_async(ui_mode: UIMode = UIMode.CURSES):
    """
    Main async entry point for the game.

    Args:
        ui_mode: Which UI implementation to use
    """
    # Register UI implementations
    UIFactory.register(UIMode.CURSES, CursesAdapter)
    UIFactory.register(UIMode.TEXTUAL, TextualAdapter)

    # Create UI instance
    ui = UIFactory.create(ui_mode)

    # Create bridge
    bridge = GameUIBridge(ui)

    try:
        # Start the bridge and UI
        await bridge.start()

        # Show main menu
        while True:
            choice = await ui.show_menu(
                [
                    "New Game",
                    "Continue",
                    "Career Progress",
                    "How to Play",
                    "Quit"
                ],
                title="VIRTUAL COW TIPPER"
            )

            if not choice:
                break

            if choice.label == "Quit":
                break

            elif choice.label == "New Game":
                await start_new_game(ui, bridge)

            elif choice.label == "Continue":
                await continue_game(ui, bridge)

            elif choice.label == "Career Progress":
                await show_career_progress(ui)

            elif choice.label == "How to Play":
                await show_how_to_play(ui)

    except KeyboardInterrupt:
        await ui.show_text("\nGame interrupted. Goodbye!")

    except Exception as e:
        await ui.show_error(f"An error occurred: {e}", fatal=False)
        raise

    finally:
        # Cleanup
        await bridge.stop()


async def start_new_game(ui, bridge):
    """Start a new game."""
    from save_manager import SaveManager

    # Check for existing save
    if SaveManager.save_exists():
        result = await ui.show_menu(
            ["Yes, start new game", "No, return to menu"],
            title="Warning: Starting a new game will overwrite your saved game!"
        )

        if not result or result.label.startswith("No"):
            return

        SaveManager.delete_save()

    # Ask for tutorial
    tutorial_choice = await ui.show_menu(
        ["Yes, show tutorial", "No, skip tutorial"],
        title="First time playing?"
    )
    show_tutorial = tutorial_choice and tutorial_choice.label.startswith("Yes")

    # Get player name
    player_name = await ui.get_input("Enter your name")

    # Check for easter eggs
    from easter_eggs import check_developer_name
    if check_developer_name(player_name):
        await ui.show_text(
            "Developer mode activated! Extra bonuses applied.",
            style="success",
            duration=3
        )

    # Start the game
    await run_game(ui, bridge, player_name, show_tutorial, load_save=False)


async def continue_game(ui, bridge):
    """Continue a saved game."""
    from save_manager import SaveManager

    save_data = SaveManager.load_game()
    if not save_data:
        await ui.show_text(
            "No save file found!",
            style="error",
            duration=2
        )
        return

    player_name = save_data['player']['name']
    await run_game(ui, bridge, player_name, show_tutorial=False, load_save=True)


async def run_game(ui, bridge, player_name: str, show_tutorial: bool, load_save: bool):
    """
    Run the main game loop.

    For now, this is a placeholder that demonstrates the UI system.
    The actual game logic will be integrated in the next phase.
    """
    from ui.game_ui_bridge import EventType, GameEvent

    # Send game start event
    await bridge.send_event(
        GameEvent(
            type=EventType.GAME_LOADED if load_save else EventType.SCREEN_CHANGED,
            data={'screen': 'game', 'player': player_name}
        )
    )

    # Placeholder game loop
    await ui.show_text(
        f"Welcome, {player_name}!\n\n"
        f"The game UI is being migrated to Textual.\n"
        f"This is a demonstration of the abstraction layer.\n\n"
        f"Press any key to return to menu...",
        style="info"
    )


async def show_career_progress(ui):
    """Display career progress."""
    from career_stats import CareerStats

    career = CareerStats.load()

    # Format career stats
    stats_text = "=== CAREER PROGRESS ===\n\n"
    stats_text += f"Total Runs: {career.total_runs}\n"
    stats_text += f"Best Score: {career.best_score}\n"
    stats_text += f"Total Cows Defeated: {career.total_cows_defeated}\n"
    stats_text += f"Total Cash Earned: ${career.total_cash_earned}\n"
    stats_text += f"Highest Floor: {career.highest_floor}\n"

    if career.unlocks:
        stats_text += "\n=== UNLOCKS ===\n"
        for unlock in career.unlocks:
            stats_text += f"✓ {unlock}\n"

    await ui.show_text(stats_text)


async def show_how_to_play(ui):
    """Display help/tutorial."""
    from help_screen import HELP_TEXT

    await ui.show_text(HELP_TEXT)


def main():
    """
    Main entry point.
    Determines UI mode and starts async loop.
    """
    # Determine UI mode from command line or environment
    ui_mode = UIMode.CURSES  # Default to curses for now

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--textual":
            ui_mode = UIMode.TEXTUAL
        elif sys.argv[1] == "--curses":
            ui_mode = UIMode.CURSES
        elif sys.argv[1] == "--help":
            print("Usage: python main_ui.py [--curses|--textual]")
            print("  --curses   Use classic curses interface (default)")
            print("  --textual  Use modern Textual interface")
            sys.exit(0)

    # Check environment variable
    if os.environ.get("VCT_UI_MODE"):
        mode_str = os.environ["VCT_UI_MODE"].lower()
        if mode_str == "textual":
            ui_mode = UIMode.TEXTUAL

    print(f"Starting Virtual Cow Tipper with {ui_mode.value} UI...")

    # Run async main
    try:
        asyncio.run(main_async(ui_mode))
    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye!")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()