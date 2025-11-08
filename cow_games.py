from typing import TYPE_CHECKING
import random
import time
import os
import sys

if TYPE_CHECKING:
    from player import Player
    from cow import Cow

# Cross-platform keyboard detection
try:
    import msvcrt  # Windows
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False
    # Unix/Mac - use termios
    import tty
    import termios

def wait_for_keypress() -> None:
    """Wait for any key press - cross-platform."""
    if HAS_MSVCRT:
        msvcrt.getch()
    else:
        # Unix/Mac
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def check_keypress() -> bool:
    """Check if key was pressed - cross-platform."""
    if HAS_MSVCRT:
        return msvcrt.kbhit()
    else:
        # Unix/Mac - use select
        import select
        return select.select([sys.stdin], [], [], 0.0)[0] != []

class CowGames:
    def __init__(self, player, cow):
        self.player = player
        self.cow = cow

    def play_random_mini_game(self, bet_amount):
        mini_games = ['tipping_bar', 'cow_race', 'guessing_game']
        selected_game = random.choice(mini_games)
        return getattr(self, selected_game)(bet_amount)

    def tipping_bar(self, bet_amount):
        max_tip = bet_amount * 3
        time_interval = max(0.05, 0.3 - 0.01 * bet_amount)
        return self._tipping_bar(bet_amount, max_tip, time_interval)

    def _tipping_bar(self, tip_amount, max_tip, time_interval):
        bar_length = 40
        cow_face_position = random.randint(5, bar_length - 10)
        target_position = random.randint(5, bar_length - 10)

        while abs(cow_face_position - target_position) < 5:
            target_position = random.randint(5, bar_length - 10)

        arrow_position = 0
        direction = 1

        input(f"Tipping Bar | Press ENTER to stop the arrow at the right spot {tip_amount} / {max_tip} | Press ENTER to start!")
        time.sleep(time_interval)

        while not check_keypress():
            arrow_line = [' '] * bar_length
            arrow_line[arrow_position] = '>'

            # Cow face rendering
            cow_face = [
                r'      \^__^/',
                r'      ( oo )\________',
                r'        (__)\        )\/\ ',
                r'            ||----w |',
                r'            ||     ||'
            ]
            cow_face_width = len(cow_face[0])
            for i in range(len(cow_face)):
                cow_face_index = cow_face_position - (cow_face_width // 2) + i
                if cow_face_index >= 0 and cow_face_index < bar_length:
                    cow_face_line = list(cow_face[i])
                    if cow_face_line[0] != ' ':
                        cow_face_line[0] = '|'
                    if cow_face_line[-1] != ' ':
                        cow_face_line[-1] = '|'
                    cow_face_line = ''.join(cow_face_line)
                    arrow_line[cow_face_index] = cow_face_line

            # Display the target
            target = [' '] * bar_length
            target[target_position - 2:target_position + 2] = '|*|-'
            print(''.join(target))

            # Display the arrow
            print(''.join(arrow_line))

            time.sleep(time_interval)
            arrow_position += direction
            if arrow_position == 0 or arrow_position == bar_length - 1:
                direction = -direction

            # Clear the terminal
            os.system('cls' if os.name == 'nt' else 'clear')

        wait_for_keypress()  # clear the key buffer

        # Calculate the tip amount based on whether the arrow_position is within range of the target
        if target_position - 1 <= arrow_position <= target_position + 1:
            tip_amount = arrow_position / (bar_length - 1) * max_tip
        else:
            tip_amount = 0

        return tip_amount
    def cow_race(self, bet_amount):
        race_length = 50
        base_speed = 1
        return self._cow_race(race_length, base_speed)

    def _cow_race(self, race_length, base_speed):
        selected_cow_names = [random.choice(cow_names) for _ in range(3)]

        print("Choose your cow to race with:")
        for i, name in enumerate(selected_cow_names, start=1):
            print(f"{i}. {name}")

        while True:
            try:
                selected_cow = int(input("Enter the number of your choice (1-3): ")) - 1
                if 0 <= selected_cow < 3:
                    break
                else:
                    print("Invalid selection. Please enter a number between 1 and 3.")
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 3.")

        player_cow_position = race_length
        other_cow_positions = [race_length] * 3

        input("Cow Race | Press ENTER to start!")

        while player_cow_position > 0 and not any(pos <= 0 for pos in other_cow_positions):
            os.system('cls' if os.name == 'nt' else 'clear')
            player_cow_position -= base_speed
            other_cow_positions = [pos - random.randint(1, 3) for pos in other_cow_positions]

            print(f"{'🏁'}{' ' * (race_length - 8)}")
            print(f"{' ' * (player_cow_position - 1)}🐄 ({selected_cow_names[selected_cow]})")
            for idx, pos in enumerate(other_cow_positions, start=1):
                if idx - 1 != selected_cow:
                    print(f"{' ' * (pos - 1)}🐄 ({selected_cow_names[idx - 1]})")

            time.sleep(0.5)

        if player_cow_position <= 0:
            print("Congratulations! Your cow won the race!")
            return self.bet_amount * 2
        else:
            print("Your cow lost the race. Better luck next time.")
            return 0

    def guessing_game(self, tip_amount):
        secret_number = random.randint(1, int(tip_amount * 1.5))
        max_guesses = 4
        range_start, range_end = 1, int(tip_amount * 1.5)
        return self._guessing_game(tip_amount, secret_number, max_guesses, range_start, range_end)

    def _guessing_game(self, tip_amount, secret_number, max_guesses, range_start, range_end):
        range_size = range_end - range_start + 1
        guesses = 0
        prev_distance = None
        input(f"Guessing Game | Guess the cow's favorite number between {range_start} and {range_end} | You have {max_guesses} guesses | Press ENTER to start!")
        while guesses < max_guesses:
            try:
                guess = int(input("Enter your guess: "))
                if guess == secret_number:
                    print("You guessed the cow's favorite number!")
                    return tip_amount
                else:
                    guesses += 1
                    remaining_guesses = max_guesses - guesses
                    if remaining_guesses > 0:
                        distance = abs(guess - secret_number) / (range_size - 1)
                        general_hint = ""
                        if distance < 0.1 and range_end > 40:
                            general_hint = "You're very hot!"
                        elif distance < 0.2 and range_end > 20:
                            general_hint = "You're hot!"
                        elif distance < 0.3:
                            general_hint = "You're warm."
                        elif distance < 0.4:
                            general_hint = "You're cool."
                        else:
                            general_hint = "You're cold."
                        
                        warmer_colder_hint = ""
                        if prev_distance is not None:
                            if distance < prev_distance:
                                warmer_colder_hint = "Warmer! "
                            else:
                                warmer_colder_hint = "Colder! "
                        prev_distance = distance

                        print(f"Incorrect! {warmer_colder_hint}{general_hint} You have {remaining_guesses} guesses left.")
                    else:
                        print(f"Sorry, you're out of guesses! The correct number was {secret_number}.")
            except ValueError:
                print("Please enter a valid number.")
            except Exception as e:
                print("An error occurred:", e)
        return 0
