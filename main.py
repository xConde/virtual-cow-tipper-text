from game import VirtualCowTipper
from main_menu import MainMenu
import os
import sys
import shutil


def ensure_dev_save_exists():
    """Auto-replenish dev save if missing (for reliable testing)."""
    save_path = "saves/game_save.json"
    template_path = "saves/dev_save.example.json"

    # If no save exists and template exists, auto-copy
    if not os.path.exists(save_path) and os.path.exists(template_path):
        try:
            shutil.copy(template_path, save_path)
            # Silent replenishment - user will see "Continue" option
        except Exception:
            pass  # Fail silently if can't copy


def main():
    """Main entry point with menu system."""
    # Ensure dev save is always available
    ensure_dev_save_exists()

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

                # Easter egg: Developer name bonus
                from easter_eggs import check_developer_name, EasterEggRewards
                is_developer = check_developer_name(player_name)
                if is_developer:
                    EasterEggRewards.developer_encounter()
                    input("\nPress Enter to continue...")

                game = VirtualCowTipper(player_name, show_tutorial=show_tutorial)

                # Developer bonus: legendary starting weapon
                if is_developer:
                    from item_factory import ItemFactory
                    dev_weapon = ItemFactory.create_weapon(less_likely=True)
                    dev_weapon.rarity = 'legendairy'
                    game.player.weapon = dev_weapon

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
