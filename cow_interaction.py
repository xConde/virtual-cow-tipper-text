from typing import Optional, Type
import random
import time
import os

from item import CowBell, Bucket, random_item_roll, get_shop_items, Tool
from assets.context import cow_names
from cow_attack import CowAttack
from cow_games import CowGames
from game_config import (
    DAIRY_ENCOUNTER_BASE_CHANCE,
    DAIRY_ENCOUNTER_WITH_COWBELL,
    COWBELL_BREAK_CHANCE_BASE,
    PACK_SCORE_COMBAT_WIN,
    PACK_SCORE_COMBAT_FLEE,
    PACK_SCORE_SHOP_BASE,
    PACK_SCORE_SHOP_EXPENSIVE_BONUS,
)

# rarity should raise the floor for items rare dag should not be min 1

# should be able to sell at the shop

class CowInteraction():
    def __init__(self, game_instance, player, cow):
        self.game_instance = game_instance
        self.game_terminal = self.game_instance.game_terminal
        self.player = player
        self.cow = cow

    def interact(self):
        handlers = {
            "aggro": self.handle_combat,
            "shop": self.handle_shop,
            "dairy": self.handle_dairy,
            "tip_or_leave": self.handle_tip_or_leave
        }
        
        cow_type = "aggro" if self.cow.is_aggro else "shop" if self.cow.is_shop else "dairy" if self.calculate_dairy_chance() else "tip_or_leave"
        handler = handlers[cow_type]
        
        self.game_instance.player.display_info(combat=self.cow.is_aggro)
        handler()

    def calculate_dairy_chance(self) -> bool:
        """Determine if this is a dairy encounter (affected by cow bell)."""
        cow_bell = self.get_item_from_inventory(CowBell)
        dairy_encounter_chance = DAIRY_ENCOUNTER_WITH_COWBELL if cow_bell else DAIRY_ENCOUNTER_BASE_CHANCE
        is_dairy = random.random() < dairy_encounter_chance

        if is_dairy:
            if cow_bell:
                break_chance = COWBELL_BREAK_CHANCE_BASE + int(self.player.cash) // 20 / 100
                print(f'Your cowbell helps attract the cow.')
                if random.random() < break_chance:
                    print('The cowbell breaks in the process.')
                    self.player.inventory.remove(cow_bell)
            else:
                print('You hear a dairy cow mooing in the distance.')
        return is_dairy

    def handle_dairy(self):
        bucket = self.get_item_from_inventory(Bucket)
        if bucket:
            liquid_gold = bucket.use()
            self.player.update_inventory(liquid_gold, "add")
            self.player.update_inventory(bucket, "remove")
            print(f"You milk {self.cow.name} with your bucket and obtain liquid gold.")
            self.cow.print_response(self.cow.name, 'dairy_bucket')
        else:
            print(f"You encounter a dairy cow named {self.cow.name}, but you don't have a bucket to milk it.")
            self.cow.print_response(self.cow.name, 'dairy_no_bucket')
        self.game_instance.destroy_cow()

    def handle_combat(self):
        print(f"A combat with '{self.cow.name}' has started!")
        self.game_terminal.set_cow_stats(self.cow.get_combat_stats())

        cow_strength = self.cow.strength

        while self.player.hp > 0 and self.cow.hp > 0:
            actions = {
                "attack": "Attack",
                "check_inventory": "Check inventory",
                "use_item": "Use an item from inventory",
                "flee": "Flee"
            }

            choice = self.handle_menu_choice(actions)

            if choice in range(1, 5):
                choice = int(choice)
                if choice == 1:
                    self.player.deal_damage(self.cow)
                    if self.cow.hp <= 0:
                        self.game_instance.update_cow_scores(self.cow, PACK_SCORE_COMBAT_WIN)
                        self.player.update_cash(self.cow.cash)
                        victory_msg = f"You defeat {self.cow.name}. You gain ${self.cow.cash}."
                        print(victory_msg)
                        self.game_terminal.type_dialog(victory_msg)
                        self.cow.print_response(self.cow.name, 'enraged_end')
                        break
                elif choice == 2:
                    self.player.check_inventory()
                elif choice == 3:
                    self.player.use_item()
                elif choice == 4:
                    self.game_instance.update_cow_scores(self.cow, PACK_SCORE_COMBAT_FLEE)
                    print("You flee from the combat.")
                    break
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
            
            if self.cow.hp > 0:
                CowAttack.cow_attack(self.player, self.cow)
                
    def handle_shop(self):
        print(f'You enter a shop run by a cow named {self.cow.name} who is currently {self.cow.mood}.')
        self.cow.print_response(self.cow.name, 'shop_keeper_intro', False)
        isLucky = random.randint(0, 99) < (40 if self.cow.mood == 'upset' else 25)
        if (self.cow.mood == 'friendly' and isLucky):
            print(f"The shop owner is very welcoming and shows you all the items in their shop with a smile.")
        elif (self.cow.mood == 'upset' and isLucky):
            print(f"{self.cow.name} grudgingly charges extra, but you're feeling lucky.")
        while True:
            available_items = get_shop_items(self.cow.mood, self.player.cash, isLucky)
            item_strings = []
            for i, item in enumerate(available_items):
                item_name = item['label'] if self.cow.mood != 'friendly' else item['item'].name
                price = item["price"]
                item_strings.append(f"{i + 1}. {item_name} - ${price}")
            item_strings.append("4. Leave the shop")

            menu_items = item_strings
            choice = self.game_terminal.get_menu_choice(menu_items)
            if choice in range(1, 5):
                choice = int(choice)
                if choice == 4:
                    self.cow.print_response(self.cow.name, 'shop_keeper_end')
                    self.game_instance.destroy_cow()
                    return

                item_choice = available_items[choice - 1]
                item_price = item_choice['price']
                if self.player.cash >= item_price:
                    self.player.update_cash(-item_price)
                    score = PACK_SCORE_SHOP_BASE + int(item_choice['price'] // PACK_SCORE_SHOP_EXPENSIVE_BONUS)
                    self.game_instance.update_cow_scores(self.cow, score)
                    self.player.update_inventory(item_choice['item'], "add")
                    self.player.display_info()
                    self.cow.print_response(self.cow.name, 'shop_keeper_purchase', False)
                    if item_choice['item'].type in ['weapon', 'shield']:
                        print(f"You purchased a {item_choice['item'].stats()} for ${item_price}.")
                    else:
                        print(f"You purchased {item_choice['item'].name} for ${item_price}.")
                    print(f"Remaining cash: ${self.player.cash}\n")
                else:
                    print("You don't have enough cash for that item.\n")
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")

    def handle_tip_or_leave(self):
        self.game_terminal.set_cow_stats(self.cow.get_mood_status())
        self.cow.print_response(self.cow.name, 'intro', False)
        actions = {
            "tip": f"Tip {self.cow.name}",
            "leave": "Flee from the cow"
        }

        choice = self.handle_menu_choice(actions)
        if choice == "1":
            min_bet = self.cow.req_amount
            max_bet = min(self.player.cash, self.cow.req_amount * random.randint(2,5))

            actions = {
                "bet min": f"Bet ${min_bet}",
                "bet max": f"Bet ${max_bet}"
            }

            choice = self.handle_menu_choice(actions, f"How much do you want to bet for the mini-game?")
            bet_amount = min_bet if choice == "1" else max_bet
            self.player.update_cash(-bet_amount)
            cow_games_instance = CowGames(self.player, self.cow)
            reward = cow_games_instance.play_random_mini_game(bet_amount)

            if reward > bet_amount:
                win_amount = round(reward - bet_amount, 2)
                print(f"Congratulations! You won ${win_amount}!")
                self.player.update_cash(reward)

                if win_amount >= bet_amount * 1.5:
                    score = 2
                elif win_amount >= bet_amount * 0.5:
                    score = 1
                else:
                    score = 0.5

                self.cow.likeliness += score
                self.game_instance.update_cow_scores(self.cow, score)

            else:
                loss_amount = bet_amount - reward
                self.player.update_cash(reward)

                if loss_amount >= bet_amount * 0.5:
                    score = -0.5
                else:
                    score = -1

                self.cow.likeliness += score
                self.game_instance.update_cow_scores(self.cow, score)

        elif choice == "2":
            print(f"You decided to leave {self.cow.name}.")
            score = -2
            self.cow.likeliness += score
            self.game_instance.update_cow_scores(self.cow, score)
        else:
            print("Please enter a number between 1 and 2.")

    def handle_menu_choice(self, actions, prompt=None):
        menu_items = [f"{i + 1}. {action}" for i, action in enumerate(actions.values())]
        choice = self.game_terminal.get_menu_choice(menu_items, prompt)
        return choice

    def get_item_from_inventory(self, item_class):
        for item in self.player.inventory:
            if isinstance(item, item_class):
                return item
        else:
            return None
