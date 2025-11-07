from game import VirtualCowTipper
from main_menu import MainMenu
import os
import sys


def main():
    """Main entry point with menu system."""
    # Clear terminal before starting to prevent text bleed-through
    try:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
    except:
        # Fallback to ANSI escape codes
        print("\033[2J\033[H", end='', flush=True)

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
                tutorial_response = input("First time playing? Show tutorial? (y/n): ").strip().lower()
                # Default to 'n' if empty (just pressed enter)
                show_tutorial = tutorial_response == 'y' if tutorial_response else False

                if show_tutorial:
                    from tutorial import show_tutorial as display_tutorial
                    display_tutorial()

                # Get player name with default
                player_name_input = input('\nEnter your name: ').strip()
                player_name = player_name_input if player_name_input else "Adventurer"

                # Start game directly (no easter egg)
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


if __name__ == "__main__":
    main()
