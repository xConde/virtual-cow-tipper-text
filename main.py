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

            elif choice == 'new_game':
                menu.cleanup()

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
