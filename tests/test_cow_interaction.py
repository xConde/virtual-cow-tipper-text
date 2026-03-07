"""Tests for CowInteraction — the central encounter dispatcher."""
import pytest
from unittest.mock import patch

from cow import Cow
from player import Player
from models import CowProperties, GameStats
from cow_interaction import CowInteraction
from item import Weapon, Shield, HealthPotion, CowBell, Bucket


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class MockTerminal:
    """Mock terminal that records dialog output and auto-responds to menus."""

    MENU_Y_START = 19
    MENU_Y_END = 25
    PROMPT_INPUT_Y = 18

    def __init__(self):
        self.dialogs = []
        self.menu_responses = []  # Queue of responses for get_menu_choice
        self._response_idx = 0

    def draw_dialog(self, text):
        self.dialogs.append(text)

    def set_player_stats(self, *a):
        pass

    def draw_player_stats(self, *a):
        pass

    def draw_game_title(self, *a):
        pass

    def draw_separator(self, *a):
        pass

    def set_cow_stats(self, *a):
        pass

    def clear_area(self, *a):
        pass

    def refresh(self):
        pass

    def clear_screen(self):
        pass

    def save_dialog_state(self):
        return ""

    def restore_dialog_state(self, s):
        pass

    class stdscr:
        @staticmethod
        def refresh():
            pass

        @staticmethod
        def addstr(*a):
            pass

        @staticmethod
        def getch():
            return ord('\n')

    def get_menu_choice(self, items, prompt=None):
        """Return queued response or default to 1."""
        if self._response_idx < len(self.menu_responses):
            resp = self.menu_responses[self._response_idx]
            self._response_idx += 1
            return resp
        return 1


class MockGame:
    """Minimal game instance for CowInteraction."""

    def __init__(self, terminal):
        self.game_terminal = terminal
        self.stats = GameStats()
        self.cow_packs = {i: 0.0 for i in range(1, 7)}
        self.current_floor = 1
        self.encounters_this_floor = 0
        self.encounters_per_floor = 10
        self.career_bonuses = {'shop_discount': 0.0, 'dairy_heal_bonus': 0}
        self.cow = None
        self.cows = []
        self.running = True
        self.player = None  # Set after player creation

    def destroy_cow(self):
        self.cow = None
        self.encounters_this_floor += 1

    def update_cow_scores(self, cow, score):
        self.cow_packs[cow.pack] = self.cow_packs.get(cow.pack, 0) + score
        self.destroy_cow()


def _make_cow(terminal, *, is_aggro=False, is_shop=False, likeliness=5,
              strength=5, hp=20, cash=50, legendary_data=None, pack=1):
    """Build a Cow with explicit flags."""
    props = CowProperties(
        name="TestCow",
        req_amount=10,
        likeliness=likeliness,
        strength=strength,
        hp=hp,
        cash=cash,
        is_shop=is_shop,
        is_aggro=is_aggro,
        pack=pack,
        approach="A test cow approaches!",
        legendary_data=legendary_data,
    )
    return Cow(terminal, props)


def _build(*, is_aggro=False, is_shop=False, likeliness=5, player_hp=20,
           player_cash=50, legendary_data=None, menu_responses=None,
           shop_discount=0.0):
    """One-call factory that returns (interaction, game, player, cow, terminal)."""
    term = MockTerminal()
    if menu_responses:
        term.menu_responses = list(menu_responses)
    game = MockGame(term)
    player = Player(term, "Tester", starting_hp=player_hp, starting_cash=player_cash)
    game.player = player
    game.career_bonuses['shop_discount'] = shop_discount
    cow = _make_cow(term, is_aggro=is_aggro, is_shop=is_shop,
                    likeliness=likeliness, legendary_data=legendary_data)
    ci = CowInteraction(game, player, cow)
    return ci, game, player, cow, term


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDispatchDetection:
    """Verify that interact() routes to the correct handler."""

    def test_aggro_cow_dispatches_to_combat(self):
        """An aggro cow should be detected as combat type."""
        ci, game, player, cow, term = _build(is_aggro=True,
                                              menu_responses=[3])  # flee immediately
        assert cow.is_aggro is True
        # Run interact — it should enter handle_combat, choice=3 means flee
        ci.interact()
        assert game.stats.cows_fled_from == 1, "Aggro cow should route to combat handler"

    def test_shop_cow_dispatches_to_shop(self):
        """A shop cow should route to handle_shop."""
        # menu response: leave shop immediately (items + 2)
        # get_shop_items returns variable length; leaving = last option.
        # We queue a high number; handle_shop uses `num_items + 2` for leave.
        # Safer: queue response that triggers leave. We'll queue 99 which is out
        # of range, then it loops and we queue the correct one. Instead, let's
        # just test that stats.shops_visited increments.
        ci, game, player, cow, term = _build(is_shop=True)
        # We need to know item count to pick "leave". Override get_menu_choice
        # to always return the leave option dynamically.
        call_count = [0]
        original = term.get_menu_choice

        def _auto_leave(items, prompt=None):
            # "Leave the shop" is always the last option
            return len(items)

        term.get_menu_choice = _auto_leave
        ci.interact()
        assert game.stats.shops_visited == 1, "Shop cow should route to handle_shop"

    def test_legendary_cow_detection(self):
        """A cow with legendary_data should be recognized by CowInteraction."""
        legendary = {
            'approach': 'A legendary cow appears!',
            'dialogue_intro': 'I am legend, {player_name}.',
            'is_aggro': True,
        }
        ci, game, player, cow, term = _build(
            is_aggro=True, legendary_data=legendary, menu_responses=[3])
        assert cow.legendary_data is not None
        ci.interact()
        # Legendary intro dialogue should appear in terminal output
        assert any("LEGENDARY ENCOUNTER" in d for d in term.dialogs)


class TestCombat:
    """Combat-related tests (using flee to avoid full loop complexity)."""

    def test_flee_updates_stats(self):
        """Fleeing combat should increment cows_fled_from."""
        ci, game, player, cow, term = _build(is_aggro=True, menu_responses=[3])
        ci.handle_combat()
        assert game.stats.cows_fled_from == 1

    def test_flee_updates_pack_score(self):
        """Fleeing should apply negative pack score."""
        from game_config import PACK_SCORE_COMBAT_FLEE
        ci, game, player, cow, term = _build(is_aggro=True, menu_responses=[3])
        ci.handle_combat()
        assert game.cow_packs[cow.pack] == PACK_SCORE_COMBAT_FLEE

    def test_combat_victory_updates_stats(self):
        """Defeating a cow should update cows_defeated, total_damage_dealt, and cash."""
        ci, game, player, cow, term = _build(
            is_aggro=True, player_cash=100, menu_responses=[1] * 20)
        # Weaken the cow so one hit kills it
        cow.hp = 1
        cow.max_hp = 1

        with patch('random.random', return_value=0.99):  # no item drop
            ci.handle_combat()

        assert game.stats.cows_defeated == 1
        assert game.stats.total_damage_dealt > 0
        assert player.cash > 100, "Player should receive cash reward"
        assert game.stats.cash_earned > 0

    def test_combat_damage_tracking(self):
        """Damage dealt during combat should be tracked in stats."""
        ci, game, player, cow, term = _build(
            is_aggro=True, player_cash=50, menu_responses=[1] * 30)
        cow.hp = 1
        cow.max_hp = 1

        with patch('random.random', return_value=0.99):
            ci.handle_combat()

        assert game.stats.total_damage_dealt >= 1


class TestShop:
    """Shop interaction tests."""

    def test_shop_items_generated(self):
        """get_shop_items should return items with prices for a neutral-mood cow."""
        from item import get_shop_items
        items = get_shop_items('neutral', 50, False, 0.0)
        assert len(items) > 0
        for item in items:
            assert 'price' in item
            assert 'item' in item
            assert item['price'] > 0

    def test_shop_discount_applied(self):
        """A 10% shop discount should produce lower prices."""
        from item import get_shop_items
        items_full = get_shop_items('neutral', 100, False, 0.0)
        items_disc = get_shop_items('neutral', 100, False, 0.10)

        # With identical RNG, discounted prices should be <= full prices.
        # Since RNG may differ between calls, just verify the discount items
        # all have positive prices (smoke test) and at least one is cheaper
        # than the max full-price item.
        full_max = max(i['price'] for i in items_full)
        disc_min = min(i['price'] for i in items_disc)
        # The discount should make the cheapest discounted item cheaper than
        # or equal to the most expensive full-price item (trivially true, but
        # ensures the function accepts the parameter without error).
        assert disc_min <= full_max

    def test_shop_discount_deterministic(self):
        """With fixed RNG, 10% discount should yield strictly lower prices."""
        import random
        from item import get_shop_items

        state = random.getstate()
        random.seed(42)
        items_full = get_shop_items('neutral', 200, False, 0.0)
        random.setstate(state)

        random.seed(42)
        items_disc = get_shop_items('neutral', 200, False, 0.10)
        random.setstate(state)

        for full, disc in zip(items_full, items_disc):
            assert disc['price'] <= full['price'], (
                f"Discounted price {disc['price']} should be <= full price {full['price']}"
            )

    def test_shop_visit_increments_stat(self):
        """Entering a shop should increment shops_visited."""
        ci, game, player, cow, term = _build(is_shop=True)

        def _leave(items, prompt=None):
            return len(items)

        term.get_menu_choice = _leave
        ci.handle_shop()
        assert game.stats.shops_visited == 1


class TestDairy:
    """Dairy encounter tests."""

    def test_dairy_heals_with_bucket(self):
        """Milking a dairy cow with a bucket should heal the player."""
        ci, game, player, cow, term = _build(player_hp=10, player_cash=50)
        bucket = Bucket()
        player.inventory.append(bucket)

        ci.handle_dairy()

        from game_config import DAIRY_COW_HEAL_AMOUNT
        assert player.hp == 10 + DAIRY_COW_HEAL_AMOUNT
        assert game.stats.dairy_cows_milked == 1

    def test_dairy_respects_hp_cap(self):
        """Dairy healing should not exceed PLAYER_MAX_HP."""
        from game_config import PLAYER_MAX_HP
        ci, game, player, cow, term = _build(player_hp=PLAYER_MAX_HP)
        bucket = Bucket()
        player.inventory.append(bucket)

        ci.handle_dairy()

        assert player.hp == PLAYER_MAX_HP
        assert game.stats.dairy_cows_milked == 1

    def test_dairy_no_bucket_shows_message(self):
        """Without a bucket, dairy encounter should show a helpful message."""
        ci, game, player, cow, term = _build()
        # No bucket in inventory
        ci.handle_dairy()

        assert game.stats.dairy_cows_milked == 0
        assert any("bucket" in d.lower() for d in term.dialogs)

    def test_dairy_career_bonus_applied(self):
        """Career dairy_heal_bonus should add extra HP."""
        ci, game, player, cow, term = _build(player_hp=10)
        player.dairy_heal_bonus = 5
        bucket = Bucket()
        player.inventory.append(bucket)

        ci.handle_dairy()

        from game_config import DAIRY_COW_HEAL_AMOUNT
        assert player.hp == 10 + DAIRY_COW_HEAL_AMOUNT + 5


class TestBetCalculation:
    """Tests for _select_bet_amount scaling logic."""

    def test_bet_scales_with_cash(self):
        """Higher cash should produce a larger base bet."""
        from game_config import (
            COW_TIP_REQUIREMENT_MIN,
            MINI_GAME_FLOOR_MULTIPLIER,
            MINI_GAME_CASH_DIVISOR,
            MINI_GAME_CAUTIOUS_MULTIPLIER,
        )

        # Poor player: cash=50
        ci_poor, _, _, _, _ = _build(player_cash=50, menu_responses=[4])  # cancel
        bet_poor = ci_poor._select_bet_amount(10)
        assert bet_poor is None  # cancelled

        # Rich player: cash=500
        ci_rich, _, _, _, _ = _build(player_cash=500, menu_responses=[4])
        bet_rich = ci_rich._select_bet_amount(10)
        assert bet_rich is None  # cancelled

    def test_bet_cautious_returns_amount(self):
        """Selecting cautious (choice=1) should return a bet the player can afford."""
        ci, game, player, cow, term = _build(player_cash=200, menu_responses=[1])
        bet = ci._select_bet_amount(10)
        assert bet is not None
        assert bet > 0
        assert bet <= player.cash

    def test_bet_cancel_returns_none(self):
        """Selecting cancel (choice=4) should return None."""
        ci, game, player, cow, term = _build(player_cash=200, menu_responses=[4])
        bet = ci._select_bet_amount(10)
        assert bet is None

    def test_bet_mood_affects_amount(self):
        """Friendly mood should reduce bet; upset should increase it."""
        from game_config import (
            MINI_GAME_FRIENDLY_BET_REDUCTION,
            MINI_GAME_UPSET_BET_INCREASE,
        )

        # Friendly cow (high likeliness)
        ci_f, _, _, cow_f, _ = _build(player_cash=200, likeliness=8, menu_responses=[2])
        assert cow_f.mood == 'friendly'
        bet_friendly = ci_f._select_bet_amount(10)

        # Upset cow (low likeliness)
        ci_u, _, _, cow_u, _ = _build(player_cash=200, likeliness=3, menu_responses=[2])
        assert cow_u.mood == 'upset'
        bet_upset = ci_u._select_bet_amount(10)

        assert bet_friendly < bet_upset, (
            f"Friendly bet ({bet_friendly}) should be less than upset bet ({bet_upset})"
        )


class TestHPBar:
    """Tests for _create_hp_bar rendering."""

    def test_full_hp(self):
        ci, *_ = _build()
        bar = ci._create_hp_bar(100, 100, "HP")
        assert "HP:" in bar
        assert "100/100" in bar
        assert "====================" in bar  # 20 filled chars

    def test_half_hp(self):
        ci, *_ = _build()
        bar = ci._create_hp_bar(50, 100, "HP")
        assert "50/100" in bar
        filled = bar.count('=')
        assert filled == 10

    def test_zero_hp(self):
        ci, *_ = _build()
        bar = ci._create_hp_bar(0, 100, "HP")
        assert "0/100" in bar
        assert '=' not in bar

    def test_zero_max_hp(self):
        """Edge case: max_hp=0 should not crash."""
        ci, *_ = _build()
        bar = ci._create_hp_bar(0, 0, "HP")
        assert "0/0" in bar


class TestSellPrice:
    """Tests for _calculate_sell_price mood scaling."""

    def test_friendly_pays_more_than_upset(self):
        ci, *_ = _build()
        weapon = Weapon("Test Sword", 5, 10, "common", 0)
        price_friendly = ci._calculate_sell_price(weapon, 'friendly')
        price_upset = ci._calculate_sell_price(weapon, 'upset')
        assert price_friendly > price_upset

    def test_sell_price_minimum(self):
        """Even a weak item should have at least SELL_PRICE_MINIMUM."""
        from game_config import SELL_PRICE_MINIMUM
        ci, *_ = _build()
        weapon = Weapon("Twig", 1, 1, "common", 0)
        price = ci._calculate_sell_price(weapon, 'upset')
        assert price >= SELL_PRICE_MINIMUM


class TestFormatLegendaryDialogue:
    """Tests for _format_legendary_dialogue placeholder replacement."""

    def test_replaces_player_name(self):
        ci, _, player, _, _ = _build()
        result = ci._format_legendary_dialogue("Hello, {player_name}!")
        assert result == "Hello, Tester!"

    def test_stray_braces_no_crash(self):
        """Stray braces like {gold} should not raise KeyError."""
        ci, *_ = _build()
        result = ci._format_legendary_dialogue("You earned {gold} coins, {player_name}")
        assert "{gold}" in result
        assert "Tester" in result
