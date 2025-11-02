#!/usr/bin/env python3
"""
Main entry point for Virtual Cow Tipper with Textual UI.
This provides a direct integration with the existing game logic.
"""

import sys
import os

# Determine if we should use Textual or fallback to curses
USE_TEXTUAL = True

# Check command line arguments
if len(sys.argv) > 1:
    if sys.argv[1] == "--curses":
        USE_TEXTUAL = False
    elif sys.argv[1] == "--help":
        print("Usage: python main_textual.py [--curses]")
        print("  --curses   Use classic curses interface")
        print("  (default)  Use modern Textual interface")
        sys.exit(0)

# Check environment variable
if os.environ.get("VCT_UI_MODE") == "curses":
    USE_TEXTUAL = False

# Check if Textual is available
if USE_TEXTUAL:
    try:
        import textual
        # Add Textual venv to path if needed
        if os.path.exists('./venv_textual/lib/python3.13/site-packages'):
            sys.path.insert(0, './venv_textual/lib/python3.13/site-packages')
    except ImportError:
        print("Textual not available, falling back to curses...")
        USE_TEXTUAL = False

if USE_TEXTUAL:
    # Use the new Textual UI with game integration
    print("Starting Virtual Cow Tipper with Textual UI...")

    # Import and run the Textual game adapter
    from game_textual_integration import TextualGameAdapter
    import asyncio

    async def run_textual_game():
        """Run the game with Textual UI."""
        game = TextualGameAdapter()
        try:
            await game.start()
        except KeyboardInterrupt:
            print("\nGame interrupted by user")
        except Exception as e:
            print(f"Game error: {e}")
            import traceback
            traceback.print_exc()

    # Run the async game
    asyncio.run(run_textual_game())

else:
    # Fallback to original curses implementation
    print("Starting Virtual Cow Tipper with Curses UI...")

    # Import and run the original game
    from game import VirtualCowTipper
    from main_menu import MainMenu

    def run_curses_game():
        """Run the original curses game."""
        menu = MainMenu()

        try:
            while True:
                choice = menu.show()

                if choice == 'quit':
                    menu.cleanup()
                    print("\nThanks for playing Virtual Cow Tipper!")
                    break

                elif choice == 'career':
                    menu.cleanup()
                    menu.show_career_progress()
                    menu = MainMenu()

                elif choice == 'how_to_play':
                    menu.show_how_to_play()

                elif choice == 'continue':
                    menu.cleanup()
                    from save_manager import SaveManager

                    save_data = SaveManager.load_game()
                    if save_data:
                        player_name = save_data['player']['name']
                        game = VirtualCowTipper(player_name, show_tutorial=False, load_save=True)
                        game.start()
                    else:
                        print("\nNo save file found!")
                        input("Press Enter to continue...")

                    menu = MainMenu()

                elif choice == 'new_game':
                    menu.cleanup()

                    # Warn if save exists
                    from save_manager import SaveManager
                    if SaveManager.save_exists():
                        print("\nWarning: Starting a new game will overwrite your saved game!")
                        confirm = input("Continue? (y/n): ").strip().lower()
                        if confirm != 'y':
                            menu = MainMenu()
                            continue

                        SaveManager.delete_save()

                    # Ask if player wants tutorial
                    print("\n" + "="*60)
                    show_tutorial = input("First time playing? Show tutorial? (y/n): ").strip().lower() == 'y'

                    if show_tutorial:
                        from tutorial import show_tutorial as display_tutorial
                        display_tutorial()

                    player_name = input('\nEnter your name: ')

                    # Easter egg: Developer cow
                    from easter_eggs import check_developer_name, EasterEggRewards
                    if check_developer_name(player_name):
                        EasterEggRewards.developer_encounter()
                        input("\nPress Enter to start...")

                    game = VirtualCowTipper(player_name, show_tutorial=show_tutorial)
                    game.start()

                    # After game ends, reinitialize menu
                    menu = MainMenu()

        except KeyboardInterrupt:
            menu.cleanup()
            print("\n\nGame interrupted. Goodbye!")
        except Exception as e:
            menu.cleanup()
            print(f"\n\nAn error occurred: {e}")
            raise

    # Run the curses game
    run_curses_game()