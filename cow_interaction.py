from typing import Optional, Type
import random
import time
import os

from item import CowBell, Bucket, get_shop_items, Tool
from cow_attack import CowAttack
from dialogue_manager import DialogueManager
from utils import safe_print
from game_config import (
    DAIRY_ENCOUNTER_BASE_CHANCE,
    DAIRY_ENCOUNTER_WITH_COWBELL,
    COWBELL_BREAK_CHANCE_BASE,
    PACK_SCORE_COMBAT_WIN,
    PACK_SCORE_COMBAT_FLEE,
    PACK_SCORE_SHOP_BASE,
    PACK_SCORE_SHOP_EXPENSIVE_BONUS,
    SHOP_LUCKY_CHANCE_UPSET,
    SHOP_LUCKY_CHANCE_FRIENDLY,
)

class CowInteraction:
    """Handles all cow interaction types: combat, shop, dairy, tipping."""

    def __init__(self, game_instance, player, cow):
        self.game_instance = game_instance
        self.game_terminal = self.game_instance.game_terminal
        self.player = player
        self.cow = cow

    def interact(self) -> None:
        """Route to appropriate interaction handler based on cow type."""
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
                bell_msg = 'Your cowbell helps attract the cow.'
                if random.random() < break_chance:
                    bell_msg += '\n\nThe cowbell breaks in the process.'
                    self.player.inventory.remove(cow_bell)

                self.game_terminal.draw_dialog(bell_msg)
                self.pause_with_prompt("[Continue...]")
        return is_dairy

    def handle_dairy(self) -> None:
        """Handle dairy cow encounter (requires bucket to milk)."""
        # Cow introduction already shown in game.py player_turn()
        bucket = self.get_item_from_inventory(Bucket)
        if bucket:
            from game_config import DAIRY_COW_HEAL_AMOUNT, PLAYER_MAX_HP

            liquid_gold = bucket.use()
            self.player.update_inventory(liquid_gold, "add")
            self.player.update_inventory(bucket, "remove")
            self.game_instance.stats.dairy_cows_milked += 1

            # HEALING: Milking dairy cows restores HP! (+ career bonus)
            dairy_heal = DAIRY_COW_HEAL_AMOUNT + getattr(self.player, 'dairy_heal_bonus', 0)
            old_hp = self.player.hp
            self.player.hp = min(self.player.hp + dairy_heal, PLAYER_MAX_HP)
            healed = self.player.hp - old_hp

            # Show dairy interaction results
            dairy_msg = f"Dairy Cow Milked!\n\nYou milk {self.cow.name} and obtain liquid gold."
            if healed > 0:
                dairy_msg += f"\n\nHP restored: +{healed} (now {self.player.hp} HP)"

            self.game_terminal.draw_dialog(dairy_msg)

            # Pause
            self.pause_with_prompt("[Press any key to continue...]")
        else:
            no_bucket_msg = (
                f"Dairy Cow - No Bucket\n\n"
                f"You encounter {self.cow.name}, but you don't have a bucket to milk it.\n\n"
                f"Find a bucket at a shop to milk dairy cows!"
            )
            self.game_terminal.draw_dialog(no_bucket_msg)

            # Pause
            self.pause_with_prompt("[Press any key to continue...]")

        self.game_instance.destroy_cow()

    def handle_combat(self) -> None:
        """Handle combat encounter with aggressive cow."""
        self.game_terminal.draw_dialog(self.cow.approach)
        self.game_terminal.set_cow_stats(self.cow.get_combat_stats())

        cow_strength = self.cow.strength

        while self.player.hp > 0 and self.cow.hp > 0:
            if self.player.stunned_turns > 0:
                stun_msg = f"Stunned! You can't act!\n({self.player.stunned_turns} turns remaining)\n\n"
                self.player.stunned_turns -= 1

                hp_before_stun = self.player.hp
                attack_msg = CowAttack.cow_attack(self.player, self.cow)
                stun_damage_taken = hp_before_stun - self.player.hp
                if stun_damage_taken > 0:
                    self.game_instance.stats.total_damage_taken += stun_damage_taken
                if attack_msg:
                    stun_msg += attack_msg

                self.player.display_info(combat=True)
                self.game_terminal.set_cow_stats(self.cow.get_combat_stats())
                self.game_terminal.draw_dialog(stun_msg)
                self.pause_with_prompt("[Continue...]")
                continue

            actions = {
                "attack": "Attack",
                "inventory": "Inventory",
                "flee": "Flee"
            }

            choice = self.handle_menu_choice(actions)

            if choice in range(1, 4):
                choice = int(choice)
                if choice == 1:
                    damage_dealt, flavor_text = self.player.deal_damage(self.cow)
                    self.game_instance.stats.total_damage_dealt += damage_dealt

                    if flavor_text:
                        damage_msg = flavor_text
                        if self.cow.hp <= 0:
                            damage_msg += f"\n\n{self.cow.name} is defeated!"
                        else:
                            damage_msg += f"\n\n{self.cow.name}: {self.cow.hp} HP remaining"
                    else:
                        damage_msg = f"{self.player.name} attacks {self.cow.name}!"
                        if self.cow.hp <= 0:
                            damage_msg += f"\n\n{self.cow.name} is defeated!"
                        else:
                            damage_msg += f"\n\n{self.cow.name}: {self.cow.hp} HP remaining"

                    self.game_terminal.draw_dialog(damage_msg)

                    if self.cow.hp <= 0:
                        from game_config import COMBAT_CASH_MULTIPLIER, COMBAT_ITEM_DROP_CHANCE

                        cash_reward = int(self.cow.cash * COMBAT_CASH_MULTIPLIER)

                        self.game_instance.update_cow_scores(self.cow, PACK_SCORE_COMBAT_WIN)
                        self.player.update_cash(cash_reward)
                        self.game_instance.stats.cows_defeated += 1
                        self.game_instance.stats.cash_earned += cash_reward

                        victory_msg = f"=== VICTORY ===\nYou defeat {self.cow.name}!\n\nRewards:\n  Cash: +${cash_reward}"

                        import random
                        if random.random() < COMBAT_ITEM_DROP_CHANCE:
                            from item_factory import ItemFactory
                            drop = ItemFactory.create_random_item(less_likely=True)
                            self.player.inventory.append(drop)
                            if hasattr(drop, 'rarity') and drop.rarity == 'legendairy':
                                self.game_instance.stats.legendary_items_found += 1
                            victory_msg += f"\n  Item Drop: {drop.name}!"

                        self.game_terminal.draw_dialog(victory_msg)
                        self.pause_with_prompt("[Press any key to continue...]")
                        break
                    else:
                        self.pause_with_prompt("[Continue to cow's turn...]")
                elif choice == 2:
                    self.player.check_inventory()
                    continue
                elif choice == 3:
                    self.game_instance.update_cow_scores(self.cow, PACK_SCORE_COMBAT_FLEE)
                    self.game_instance.stats.cows_fled_from += 1
                    flee_msg = f"Fled!\n\nYou escape from {self.cow.name}."
                    self.game_terminal.draw_dialog(flee_msg)
                    self.pause_with_prompt("[Escaping...]")
                    break
            else:
                error_msg = "Invalid choice. Please enter 1, 2, or 3."
                self.game_terminal.draw_dialog(error_msg)
                self.game_terminal.stdscr.refresh()
                continue

            if self.cow.hp > 0:
                hp_before = self.player.hp
                attack_msg = CowAttack.cow_attack(self.player, self.cow)
                damage_taken = hp_before - self.player.hp
                if damage_taken > 0:
                    self.game_instance.stats.total_damage_taken += damage_taken
                if attack_msg:
                    self.player.display_info(combat=True)
                    self.game_terminal.set_cow_stats(self.cow.get_combat_stats())
                    self.game_terminal.draw_dialog(attack_msg)
                    self.pause_with_prompt("[Continue...]")
                
    def handle_shop(self) -> None:
        """Handle shop encounter (buy and sell items)."""
        self.game_instance.stats.shops_visited += 1
        starting_cash = self.player.cash
        purchases = []
        sales = []
        lucky_chance = SHOP_LUCKY_CHANCE_UPSET if self.cow.mood == 'upset' else SHOP_LUCKY_CHANCE_FRIENDLY
        isLucky = random.random() < lucky_chance

        greeting_msg = f"{self.cow.name}'s Shop\n\n"
        if self.cow.mood == 'friendly' and isLucky:
            greeting_msg += "The shop owner greets you warmly!"
        elif self.cow.mood == 'upset' and isLucky:
            greeting_msg += f"{self.cow.name} grudgingly serves you."
        else:
            greeting_msg += f"Welcome to the shop. ({self.cow.mood} mood)"

        self.game_terminal.draw_dialog(greeting_msg)
        self.pause_with_prompt("[Browse items...]")

        saved_shop_greeting = greeting_msg

        while True:
            shop_discount = getattr(self.game_instance, 'career_bonuses', {}).get('shop_discount', 0.0)
            available_items = get_shop_items(self.cow.mood, self.player.cash, isLucky, shop_discount)
            num_items = len(available_items)

            item_strings = []
            for i, item in enumerate(available_items):
                item_name = item['label'] if self.cow.mood != 'friendly' else item['item'].name
                price = item["price"]
                item_strings.append(f"{i + 1}. {item_name} - ${price}")

            item_strings.append(f"{num_items + 1}. Sell items")
            item_strings.append(f"{num_items + 2}. Leave the shop")

            menu_items = item_strings
            choice = self.game_terminal.get_menu_choice(menu_items)

            if choice in range(1, num_items + 3):
                choice = int(choice)
                if choice <= num_items:
                    item_choice = available_items[choice - 1]
                    item_price = item_choice['price']
                    if self.player.cash >= item_price:
                        self.player.update_cash(-item_price)
                        self.player.update_inventory(item_choice['item'], "add")
                        self.player.display_info()

                        self.game_instance.stats.cash_spent += item_price
                        self.game_instance.stats.items_purchased += 1
                        if hasattr(item_choice['item'], 'rarity') and item_choice['item'].rarity == 'legendairy':
                            self.game_instance.stats.legendary_items_found += 1

                        item_name = item_choice['item'].name
                        purchases.append((item_name, item_price))
                        total_spent = sum(price for _, price in purchases)
                        if item_choice['item'].type in ['weapon', 'shield']:
                            item_display = item_choice['item'].stats()
                        else:
                            item_display = item_choice['item'].name

                        purchase_msg = (
                            f"Purchased: {item_display}\n"
                            f"Paid: ${item_price} | Remaining: ${self.player.cash}\n\n"
                            f"Visit Total: {len(purchases)} items | ${total_spent} spent"
                        )

                        self.game_terminal.draw_dialog(purchase_msg)
                        self.pause_with_prompt("[Continue shopping...]")

                        self.game_terminal.draw_dialog(saved_shop_greeting)
                    else:
                        error_msg = (
                            f"Not Enough Cash\n\n"
                            f"Item costs: ${item_price}\n"
                            f"You have: ${self.player.cash}\n\n"
                            f"Come back when you have more cash!"
                        )
                        self.game_terminal.draw_dialog(error_msg)

                        self.pause_with_prompt("[Continue shopping...]")

                        self.game_terminal.draw_dialog(saved_shop_greeting)
                elif choice == num_items + 1:
                    sellable = [item for item in self.player.inventory if hasattr(item, 'stats')]
                    if not sellable:
                        no_items_msg = "No items to sell.\n\nYou don't have any sellable items."
                        self.game_terminal.draw_dialog(no_items_msg)
                        self.pause_with_prompt("[Continue shopping...]")

                        self.game_terminal.draw_dialog(saved_shop_greeting)
                        continue

                    sell_menu = [f"{i+1}. {item.name} - ${self._calculate_sell_price(item, self.cow.mood)}"
                                 for i, item in enumerate(sellable)]
                    sell_menu.append(f"{len(sellable)+1}. Cancel")

                    sell_choice = self.game_terminal.get_menu_choice(sell_menu, "Select item to sell:")
                    if sell_choice <= len(sellable):
                        sold_item = sellable[sell_choice - 1]
                        sell_price = self._calculate_sell_price(sold_item, self.cow.mood)
                        self.player.update_inventory(sold_item, "remove")
                        self.player.update_cash(sell_price)
                        self.player.display_info()

                        self.game_instance.stats.cash_earned += sell_price
                        self.game_instance.stats.items_sold += 1

                        sales.append((sold_item.name, sell_price))
                        total_earned = sum(price for _, price in sales)
                        sale_msg = (
                            f"Sold: {sold_item.name}\n"
                            f"Received: ${sell_price} | Balance: ${self.player.cash}\n\n"
                            f"Visit Total: {len(sales)} sold | ${total_earned} earned"
                        )
                        self.game_terminal.draw_dialog(sale_msg)
                        self.pause_with_prompt("[Continue shopping...]")

                        self.game_terminal.draw_dialog(saved_shop_greeting)
                    else:
                        cancel_msg = "Sale cancelled."
                        self.game_terminal.draw_dialog(cancel_msg)
                        self.pause_with_prompt("[Continue shopping...]")

                        self.game_terminal.draw_dialog(saved_shop_greeting)
                elif choice == num_items + 2:
                    # Calculate total shop score based on transactions
                    total_shop_score = 0
                    for item_name, price in purchases:
                        total_shop_score += PACK_SCORE_SHOP_BASE + int(price // PACK_SCORE_SHOP_EXPENSIVE_BONUS)

                    # Leave the shop with visit summary
                    if purchases or sales:
                        exit_msg = f"Leaving {self.cow.name}'s Shop\n\n"

                        if purchases:
                            exit_msg += f"Purchased: {len(purchases)} items\n"
                            for item_name, price in purchases:
                                exit_msg += f"  • {item_name} (${price})\n"

                        if sales:
                            exit_msg += f"\nSold: {len(sales)} items\n"
                            for item_name, price in sales:
                                exit_msg += f"  • {item_name} (${price})\n"

                        total_spent = sum(price for _, price in purchases)
                        total_earned = sum(price for _, price in sales)
                        net_change = total_earned - total_spent

                        exit_msg += f"\nCash: ${starting_cash} → ${self.player.cash}"
                        if net_change < 0:
                            exit_msg += f" (spent ${abs(net_change)})"
                        elif net_change > 0:
                            exit_msg += f" (profit ${net_change})"
                    else:
                        exit_msg = f"Leaving {self.cow.name}'s Shop\n\nYou browsed but didn't transact."

                    self.game_terminal.draw_dialog(exit_msg)
                    self.pause_with_prompt("[Continue adventure...]")

                    # Update pack scores based on total shop interaction
                    if total_shop_score > 0:
                        self.cow.likeliness += total_shop_score
                        for queued_cow in self.game_instance.cows:
                            queued_cow.likeliness += total_shop_score
                        self.game_instance.cow_packs[self.cow.pack] += total_shop_score

                    self.game_instance.destroy_cow()
                    return
            else:
                error_msg = f"Invalid choice. Please select 1-{num_items + 2}."
                self.game_terminal.draw_dialog(error_msg)
                self.pause_with_prompt("[Try again...]")

                self.game_terminal.draw_dialog(saved_shop_greeting)

    def _select_bet_amount(self, base_amount: int) -> Optional[int]:
        """
        Let player choose bet amount with multi-factor balanced scaling.

        Factors: Floor progression (40%), Cash wealth (40%), Encounter progress (20%)

        Returns:
            Bet amount, or None if cancelled
        """
        from game_config import (
            MINI_GAME_CAUTIOUS_MULTIPLIER,
            MINI_GAME_NORMAL_MULTIPLIER,
            MINI_GAME_BOLD_MULTIPLIER,
            MINI_GAME_FRIENDLY_BET_REDUCTION,
            MINI_GAME_UPSET_BET_INCREASE,
            MINI_GAME_FLOOR_MULTIPLIER,
            MINI_GAME_CASH_DIVISOR,
            COW_TIP_REQUIREMENT_MIN
        )

        # Multi-factor bet scaling
        floor_component = (self.game_instance.current_floor - 1) * MINI_GAME_FLOOR_MULTIPLIER
        encounter_pct = self.game_instance.encounters_this_floor / 10
        encounter_component = int(encounter_pct * self.game_instance.current_floor)
        cash_component = self.player.cash // MINI_GAME_CASH_DIVISOR

        base_amount = COW_TIP_REQUIREMENT_MIN + floor_component + encounter_component + cash_component

        # Adjust for personality (applied to final amount)
        if self.cow.mood == 'friendly':
            base_amount = int(base_amount * MINI_GAME_FRIENDLY_BET_REDUCTION)
        elif self.cow.mood == 'upset':
            base_amount = int(base_amount * MINI_GAME_UPSET_BET_INCREASE)

        cautious = int(base_amount * MINI_GAME_CAUTIOUS_MULTIPLIER)
        normal = base_amount
        bold = int(base_amount * MINI_GAME_BOLD_MULTIPLIER)

        # Build bet selection message with personality flavor
        mood_text = ""
        if self.cow.mood == 'friendly':
            mood_text = f"\n{self.cow.name} seems friendly - lower stakes!"
        elif self.cow.mood == 'upset':
            mood_text = f"\n{self.cow.name} wants higher stakes!"

        bet_msg = f"Choose Your Bet{mood_text}\n\nHow much do you want to wager?"

        self.game_terminal.draw_dialog(bet_msg)

        # Ensure all bet amounts are integers (round appropriately)
        cautious = max(1, cautious)  # Minimum $1
        normal = max(1, normal)
        bold = max(2, bold)

        # Build menu with affordability indicators
        menu_items = []
        if self.player.cash >= cautious:
            menu_items.append(f"1. Cautious (${cautious}) - Play it safe")
        else:
            menu_items.append(f"1. Cautious (${cautious}) - Need ${cautious - self.player.cash} more")

        if self.player.cash >= normal:
            menu_items.append(f"2. Normal (${normal}) - Standard bet")
        else:
            menu_items.append(f"2. Normal (${normal}) - Need ${normal - self.player.cash} more")

        if self.player.cash >= bold:
            menu_items.append(f"3. Bold (${bold}) - High risk, high reward!")
        else:
            menu_items.append(f"3. Bold (${bold}) - Need ${bold - self.player.cash} more")

        menu_items.append("4. Cancel")

        choice = self.game_terminal.get_menu_choice(menu_items, "Select bet:")

        # Map choice to bet amount and validate
        if choice <= 3:
            bet_amounts = [cautious, normal, bold]
            bet_amount = bet_amounts[choice - 1]

            if self.player.cash >= bet_amount:
                return bet_amount
            else:
                error_msg = f"Insufficient Funds\n\nNeed ${bet_amount}, you have ${self.player.cash}\n\nPlease choose a different bet or cancel."
                self.game_terminal.draw_dialog(error_msg)
                self.pause_with_prompt("[Press any key...]")
                return None  # Return to encounter menu

        return None  # Cancelled

    def _offer_rematch(self, bet_amount: int, original_mood: str) -> bool:
        """
        Offer rematch after loss with personality-driven dialogue.

        Returns:
            True if player wants rematch, False otherwise
        """
        # Cow mood shifts to upset
        mood_shift_msg = ""
        if original_mood == 'friendly':
            mood_shift_msg = f"\n\n{self.cow.name} doesn't look so friendly anymore..."
        elif original_mood == 'neutral':
            mood_shift_msg = f"\n\n{self.cow.name} is getting competitive..."

        # Check if player can afford rematch
        if self.player.cash < bet_amount:
            from game_config import MINI_GAME_LOSS_SCORE

            broke_msg = (
                f"Out of Cash!{mood_shift_msg}\n\n"
                f"{self.cow.name} wanted a rematch, but you can't afford it.\n\n"
                f"You walk away defeated..."
            )
            self.game_terminal.draw_dialog(broke_msg)
            self.pause_with_prompt("[Press any key...]")

            # Apply loss penalty before leaving
            self.cow.likeliness += MINI_GAME_LOSS_SCORE
            self.game_instance.update_cow_scores(self.cow, MINI_GAME_LOSS_SCORE)

            return False

        rematch_msg = (
            f"Rematch Offer{mood_shift_msg}\n\n"
            f"{self.cow.name}: 'Want to win it back?'\n\n"
            f"Double-or-nothing: Bet ${bet_amount} again!"
        )

        self.game_terminal.draw_dialog(rematch_msg)

        menu_items = [
            f"1. Rematch (bet ${bet_amount} again)",
            "2. Walk away (accept loss)"
        ]

        choice = self.game_terminal.get_menu_choice(menu_items, "Your decision:")

        # Shift cow mood for rematch
        if choice == 1:
            self.cow.mood = 'upset'
            self.game_terminal.set_cow_stats(f"{self.cow.name} | Angry")
            return True

        return False

    def handle_tip_or_leave(self) -> None:
        """Handle regular cow encounter (tip for mini-game or leave)."""
        self.game_terminal.set_cow_stats(self.cow.get_mood_status())
        self.cow.print_response(self.cow.name, 'intro', False)
        actions = {
            "play_mini_game": f"Play mini-game with {self.cow.name}",
            "leave": "Leave"
        }

        choice = self.handle_menu_choice(actions)

        if choice == 1:
            from game_config import (
                MINI_GAME_FRIENDLY_WIN_THRESHOLD,
                MINI_GAME_NEUTRAL_WIN_THRESHOLD
            )

            original_mood = self.cow.mood

            # Step 1: Select bet amount
            bet_amount = self._select_bet_amount(self.cow.req_amount)
            if bet_amount is None:
                return

            # Determine win threshold based on personality
            win_threshold = MINI_GAME_FRIENDLY_WIN_THRESHOLD if self.cow.mood == 'friendly' else MINI_GAME_NEUTRAL_WIN_THRESHOLD

            # Step 2: Show game intro with personality
            if self.cow.mood == 'friendly':
                flavor = "I'll go easy on you!"
            elif self.cow.mood == 'upset':
                flavor = "You better not waste my time!"
            else:
                flavor = "May the odds be with you!"

            game_msg = (
                f"Dice Rolling Game!\n\n"
                f"{self.cow.name}: \"{flavor}\"\n"
                f"Bet: ${bet_amount}\n\n"
                f"Roll two dice - get {win_threshold} or higher to win!\n"
                f"({win_threshold}-12 wins, 2-{win_threshold-1} loses)"
            )
            self.game_terminal.draw_dialog(game_msg)
            self.pause_with_prompt("[Press ENTER to roll the dice...]")
            rolling_msg = (
                f"Rolling the dice...\n\n"
                f"🎲 🎲\n\n"
                f"The dice tumble..."
            )
            self.game_terminal.draw_dialog(rolling_msg)
            self.pause_with_prompt("[Press ENTER to see result...]")

            # Step 3: Roll dice
            self.player.update_cash(-bet_amount)
            self.game_instance.stats.cash_spent += bet_amount
            die1 = random.randint(1, 6)
            die2 = random.randint(1, 6)
            total = die1 + die2
            won = total >= win_threshold

            # Step 4: Show result and handle outcome
            if won:
                from game_config import (
                    MINI_GAME_WIN_SCORE_BASE,
                    MINI_GAME_WIN_SCORE_PER_BET_MULTIPLIER
                )

                self.game_instance.stats.mini_games_won += 1
                profit = bet_amount
                self.player.update_cash(bet_amount * 2)
                self.game_instance.stats.cash_earned += bet_amount * 2

                win_msg = (
                    f"🎲 You Rolled: {die1} + {die2} = {total} 🎲\n\n"
                    f"YOU WIN!\n\n"
                    f"The dice favor you!\n"
                    f"Profit: +${profit}"
                )
                self.game_terminal.draw_dialog(win_msg)

                # Scaled reputation based on bet size
                bet_multiplier = bet_amount / self.cow.req_amount
                score = MINI_GAME_WIN_SCORE_BASE + (bet_multiplier * MINI_GAME_WIN_SCORE_PER_BET_MULTIPLIER)
                self.cow.likeliness += score
                self.game_instance.update_cow_scores(self.cow, score)

                self.pause_with_prompt("[Press any key to continue...]")

            else:
                # LOSS - Show result and offer rematch
                from game_config import (
                    MINI_GAME_LOSS_SCORE,
                    MINI_GAME_REMATCH_WIN_SCORE,
                    MINI_GAME_REMATCH_LOSS_SCORE
                )

                self.game_instance.stats.mini_games_lost += 1

                loss_msg = (
                    f"🎲 You Rolled: {die1} + {die2} = {total} 🎲\n\n"
                    f"You Lose\n\n"
                    f"Not lucky this time.\n"
                    f"Lost: ${bet_amount}"
                )
                self.game_terminal.draw_dialog(loss_msg)
                self.pause_with_prompt("[Press any key...]")

                # Offer rematch
                wants_rematch = self._offer_rematch(bet_amount, original_mood)

                if wants_rematch:
                    # REMATCH GAME
                    rematch_intro = (
                        f"Rematch!\n\n"
                        f"{self.cow.name} deals again.\n"
                        f"Bet: ${bet_amount}\n\n"
                        f"Win: Break even (+${bet_amount})\n"
                        f"Lose: Double loss (-${bet_amount} more)"
                    )
                    self.game_terminal.draw_dialog(rematch_intro)
                    self.pause_with_prompt("[Press ENTER to roll...]")

                    # Rematch roll
                    self.player.update_cash(-bet_amount)
                    self.game_instance.stats.cash_spent += bet_amount
                    die1 = random.randint(1, 6)
                    die2 = random.randint(1, 6)
                    total = die1 + die2
                    rematch_won = total >= win_threshold

                    if rematch_won:
                        # WIN REMATCH - Break even
                        self.game_instance.stats.mini_games_won += 1
                        self.player.update_cash(bet_amount * 2)
                        self.game_instance.stats.cash_earned += bet_amount * 2

                        rematch_win_msg = (
                            f"🎲 Rematch: {die1} + {die2} = {total} 🎲\n\n"
                            f"REMATCH WIN!\n\n"
                            f"You got your ${bet_amount} back!\n"
                            f"Final result: Break even (±$0)"
                        )
                        self.game_terminal.draw_dialog(rematch_win_msg)

                        # Neutral score
                        self.game_instance.update_cow_scores(self.cow, MINI_GAME_REMATCH_WIN_SCORE)

                        self.pause_with_prompt("[Press any key to continue...]")

                    else:
                        # LOSE REMATCH - Double loss
                        self.game_instance.stats.mini_games_lost += 1
                        rematch_loss_msg = (
                            f"🎲 Rematch: {die1} + {die2} = {total} 🎲\n\n"
                            f"REMATCH LOST!\n\n"
                            f"{self.cow.name} takes your money.\n"
                            f"Total lost: ${bet_amount * 2}"
                        )
                        self.game_terminal.draw_dialog(rematch_loss_msg)

                        # Heavy penalty
                        self.cow.likeliness += MINI_GAME_REMATCH_LOSS_SCORE
                        self.game_instance.update_cow_scores(self.cow, MINI_GAME_REMATCH_LOSS_SCORE)

                        self.pause_with_prompt("[Press any key to continue...]")

                else:
                    # Declined rematch - just accept the loss
                    self.cow.likeliness += MINI_GAME_LOSS_SCORE
                    self.game_instance.update_cow_scores(self.cow, MINI_GAME_LOSS_SCORE)

        elif choice == 2:
            leave_msg = (
                f"Leaving {self.cow.name}\n\n"
                f"You decided to leave.\n"
                f"The cow seems disappointed but understanding."
            )
            self.game_terminal.draw_dialog(leave_msg)

            score = -1  # Less harsh penalty for leaving
            self.cow.likeliness += score
            self.game_instance.update_cow_scores(self.cow, score)
            self.pause_with_prompt("[Press any key to continue...]")
        else:
            error_msg = f"Invalid choice. Please select 1 or 2."
            self.game_terminal.draw_dialog(error_msg)
            self.pause_with_prompt("[Press any key to try again...]")
            return self.handle_tip_or_leave()

    def pause_with_prompt(self, prompt_text="[Continue...]"):
        """Show a pause prompt and wait for key, with menu area cleared."""
        self.game_terminal.clear_area(self.game_terminal.MENU_Y_START, self.game_terminal.MENU_Y_END)
        self.game_terminal.clear_area(self.game_terminal.PROMPT_INPUT_Y)

        prompt_y = self.game_terminal.PROMPT_INPUT_Y
        self.game_terminal.stdscr.addstr(prompt_y, 2, prompt_text)
        self.game_terminal.stdscr.refresh()
        self.game_terminal.stdscr.getch()

    def handle_menu_choice(self, actions, prompt=None):
        menu_items = [f"{i + 1}. {action}" for i, action in enumerate(actions.values())]
        choice = self.game_terminal.get_menu_choice(menu_items, prompt)
        return choice

    def get_item_from_inventory(self, item_class):
        """Find first item of given type in player inventory."""
        for item in self.player.inventory:
            if isinstance(item, item_class):
                return item
        return None

    def _calculate_sell_price(self, item, cow_mood: str) -> int:
        """Calculate sell price for item (50-70% of value based on mood)."""
        from item_factory import ItemFactory
        from game_config import (
            SELL_PRICE_VALUE_MULTIPLIER,
            SELL_PRICE_FRIENDLY,
            SELL_PRICE_NEUTRAL,
            SELL_PRICE_UPSET,
            SELL_PRICE_MINIMUM
        )

        # Estimate item value based on median stat
        median_stat = ItemFactory.calculate_item_median_stat(item)
        base_value = int(median_stat * SELL_PRICE_VALUE_MULTIPLIER)

        # Mood affects sell price (friendly pays more)
        sell_percentages = {
            'friendly': SELL_PRICE_FRIENDLY,
            'neutral': SELL_PRICE_NEUTRAL,
            'upset': SELL_PRICE_UPSET
        }
        sell_percentage = sell_percentages.get(cow_mood, SELL_PRICE_NEUTRAL)

        return max(SELL_PRICE_MINIMUM, int(base_value * sell_percentage))

    def _create_hp_bar(self, current_hp: int, max_hp: int, label: str) -> str:
        """Create visual HP bar."""
        bar_width = 20
        filled = int((current_hp / max_hp) * bar_width) if max_hp > 0 else 0
        empty = bar_width - filled

        hp_bar = '[' + ('=' * filled) + (' ' * empty) + ']'
        return f"{label}: {hp_bar} {current_hp}/{max_hp} HP"
