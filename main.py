from game import VirtualCowTipper
from main_menu import MainMenu


def main():
    """Main entry point with menu system."""
    menu = MainMenu()

    try:
        while True:
            choice = menu.show()

            if choice == 'quit':
                menu.cleanup()
                print("\nThanks for playing Virtual Cow Tipper!")
                break

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
