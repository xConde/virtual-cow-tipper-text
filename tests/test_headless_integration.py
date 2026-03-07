"""
Headless integration tests — drive full game sessions without curses.

Simulates realistic encounter sequences by building game objects manually
and exercising the complete data flow: cow generation -> interaction ->
stat tracking -> save/load.
"""
import os
import random
import tempfile
import shutil

from cow import Cow
from cow_attack import CowAttack
from player import Player
from models import GameStats, CowProperties
from save_manager import SaveManager
from career_stats import CareerStats
from item import Weapon, Shield, HealthPotion, CowBell, Bucket
from game_config import (
    VICTORY_COWS_DEFEATED,
    NUM_COW_PACKS,
    PLAYER_MAX_HP,
    COMBAT_CASH_MULTIPLIER,
    PACK_SCORE_COMBAT_WIN,
)


# ---------------------------------------------------------------------------
# Mock objects — replace curses terminal with no-ops
# ---------------------------------------------------------------------------

class MockStdscr:
    """Mock curses stdscr with all methods the codebase calls."""

    def refresh(self):
        pass

    def addstr(self, *args):
        pass

    def getch(self):
        return ord('\n')


class MockTerminal:
    """Drop-in replacement for GameTerminal.

    Every method is a no-op so the full Player / Cow / CowInteraction code
    paths can execute without a real curses session.
    """

    MENU_Y_START = 20
    MENU_Y_END = 26
    PROMPT_INPUT_Y = 27

    def __init__(self):
        self.stdscr = MockStdscr()

    def set_player_stats(self, *args):
        pass

    def draw_player_stats(self):
        pass

    def draw_game_title(self):
        pass

    def draw_separator(self):
        pass

    def draw_dialog(self, text):
        pass

    def refresh(self):
        pass

    def close_game_terminal(self):
        pass

    def clear_screen(self):
        pass

    def set_cow_stats(self, *args):
        pass

    def clear_area(self, *args):
        pass

    def save_dialog_state(self):
        return None

    def restore_dialog_state(self, state):
        pass

    def get_menu_choice(self, menu_items, prompt=None):
        return 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_player(terminal, name="TestPlayer", hp=20, cash=50):
    """Create a Player wired to MockTerminal."""
    p = Player(terminal, name, starting_hp=hp, starting_cash=cash)
    p.damage_bonus = 0
    p.dairy_heal_bonus = 0
    return p


def make_aggro_cow(terminal, player, strength=5, hp=15, cash=40):
    """Create a guaranteed-aggro Cow."""
    props = CowProperties(
        name="TestBull",
        req_amount=5,
        likeliness=5,
        strength=strength,
        hp=hp,
        cash=cash,
        is_shop=False,
        is_aggro=True,
        pack=1,
        approach="A hostile cow charges at you!",
    )
    return Cow(terminal, props)


def make_shop_cow(terminal):
    props = CowProperties(
        name="ShopCow",
        req_amount=5,
        likeliness=7,
        strength=3,
        hp=10,
        cash=0,
        is_shop=True,
        is_aggro=False,
        pack=2,
        approach="A cow with a shop sign appears.",
    )
    return Cow(terminal, props)


def make_neutral_cow(terminal):
    props = CowProperties(
        name="ChillCow",
        req_amount=5,
        likeliness=5,
        strength=3,
        hp=10,
        cash=20,
        is_shop=False,
        is_aggro=False,
        pack=3,
        approach="A calm cow gazes at you.",
    )
    return Cow(terminal, props)


def simulate_combat(player, cow, stats):
    """Run a deterministic combat loop: player attacks until cow dies,
    cow attacks back each round. Returns True if player survived."""
    while cow.hp > 0 and player.hp > 0:
        damage_dealt, _ = player.deal_damage(cow)
        stats.total_damage_dealt += damage_dealt

        if cow.hp <= 0:
            cash_reward = int(cow.cash * COMBAT_CASH_MULTIPLIER)
            player.update_cash(cash_reward)
            stats.cows_defeated += 1
            stats.cash_earned += cash_reward
            break

        # Cow attacks back
        hp_before = player.hp
        CowAttack.cow_attack(player, cow)
        damage_taken = hp_before - player.hp
        if damage_taken > 0:
            stats.total_damage_taken += damage_taken

    return player.hp > 0


# ---------------------------------------------------------------------------
# Test 1 — Full game session with 10 encounters
# ---------------------------------------------------------------------------

class TestFullGameSession:
    def test_full_game_session_10_encounters(self):
        """Simulate 10 encounters exercising the full data pipeline."""
        random.seed(42)
        terminal = MockTerminal()
        player = make_player(terminal, hp=60, cash=80)
        stats = GameStats()
        cow_packs = {pack: 0.0 for pack in range(1, NUM_COW_PACKS + 1)}

        starting_cash = player.cash
        encounters = 10

        for _ in range(encounters):
            # Generate a cow via the real generation pipeline
            props = Cow.generate_random_cow_properties(player)
            cow = Cow(terminal, props)

            if cow.is_aggro:
                survived = simulate_combat(player, cow, stats)
                cow_packs[cow.pack] += PACK_SCORE_COMBAT_WIN
                if not survived:
                    break
            else:
                # Shop or neutral — skip (just destroy)
                pass

        # At least some cows should have been aggro and defeated
        assert stats.cows_defeated > 0, "Expected at least one cow defeated"
        assert stats.total_damage_dealt > 0, "Expected damage to have been dealt"
        assert player.cash != starting_cash, "Cash should have changed from combat rewards"


# ---------------------------------------------------------------------------
# Test 2 — Save / Load roundtrip preserves full state
# ---------------------------------------------------------------------------

class TestSaveLoadRoundtrip:
    def setup_method(self):
        """Use a temp directory so tests don't clobber real saves."""
        self._orig_save_dir = SaveManager.get_save_path.__module__
        self._tmpdir = tempfile.mkdtemp()
        # Monkey-patch SAVE_DIR inside save_manager module
        import save_manager
        self._orig_dir = save_manager.SAVE_DIR
        save_manager.SAVE_DIR = self._tmpdir

    def teardown_method(self):
        import save_manager
        save_manager.SAVE_DIR = self._orig_dir
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_save_load_preserves_full_state(self):
        """Play 5 encounters, save, load, verify all state matches."""
        random.seed(99)
        terminal = MockTerminal()
        player = make_player(terminal, name="SaveTestHero", hp=50, cash=100)
        stats = GameStats()
        cow_packs = {pack: 0.0 for pack in range(1, NUM_COW_PACKS + 1)}
        current_floor = 2
        encounters_this_floor = 3

        # Add inventory items so they survive the roundtrip
        weapon = Weapon("Test Sword", 5, 12, "uncommon", 2)
        player.inventory.append(weapon)
        player.weapon = weapon

        shield = Shield("Test Buckler", 2, 6, "common", 1)
        player.inventory.append(shield)
        player.shield = shield

        potion = HealthPotion("normal")
        player.inventory.append(potion)

        cowbell = CowBell()
        player.inventory.append(cowbell)

        # Run 5 encounters to accumulate stats
        for _ in range(5):
            props = Cow.generate_random_cow_properties(player)
            cow = Cow(terminal, props)
            if cow.is_aggro:
                simulate_combat(player, cow, stats)
                cow_packs[cow.pack] += PACK_SCORE_COMBAT_WIN

        # Snapshot state before save
        snap_hp = player.hp
        snap_cash = player.cash
        snap_name = player.name
        snap_stats = {
            'cows_defeated': stats.cows_defeated,
            'total_damage_dealt': stats.total_damage_dealt,
            'cash_earned': stats.cash_earned,
            'shops_visited': stats.shops_visited,
        }
        snap_packs = dict(cow_packs)
        snap_inv_count = len(player.inventory)

        # Save
        assert SaveManager.save_game(
            player, stats, cow_packs, current_floor, encounters_this_floor
        ), "Save should succeed"

        # Load into fresh objects
        save_data = SaveManager.load_game()
        assert save_data is not None, "Load should return data"

        # restore_player restores hp/cash/inventory/weapon/shield but NOT name.
        # The real game creates the Player with the saved name upfront, so we
        # replicate that here by reading the name from save_data first.
        saved_name = save_data['player']['name']
        new_player = make_player(terminal, name=saved_name)
        new_stats = GameStats()

        SaveManager.restore_player(new_player, save_data)
        SaveManager.restore_stats(new_stats, save_data)

        # Verify player state
        assert new_player.hp == snap_hp
        assert new_player.cash == snap_cash
        assert new_player.name == snap_name

        # Verify stats
        assert new_stats.cows_defeated == snap_stats['cows_defeated']
        assert new_stats.total_damage_dealt == snap_stats['total_damage_dealt']
        assert new_stats.cash_earned == snap_stats['cash_earned']

        # Verify cow packs
        assert save_data['cow_packs'] == snap_packs

        # Verify floor/encounter counts
        assert save_data['current_floor'] == current_floor
        assert save_data['encounters_this_floor'] == encounters_this_floor

        # Verify inventory count survived roundtrip
        assert len(new_player.inventory) == snap_inv_count

        # Verify weapon and shield survived
        assert new_player.weapon is not None
        assert new_player.weapon.name == "Test Sword"
        assert new_player.shield is not None
        assert new_player.shield.name == "Test Buckler"


# ---------------------------------------------------------------------------
# Test 3 — Career progression across runs
# ---------------------------------------------------------------------------

class TestCareerProgression:
    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        self._orig_file = None
        import career_stats as cs_mod
        self._orig_file = cs_mod.CAREER_FILE
        cs_mod.CAREER_FILE = os.path.join(self._tmpdir, "career_stats.json")

    def teardown_method(self):
        import career_stats as cs_mod
        cs_mod.CAREER_FILE = self._orig_file
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_career_progression_across_runs(self):
        """Simulate 2 runs and verify career stats accumulate."""
        random.seed(7)
        terminal = MockTerminal()

        # --- Run 1: defeat 30 cows ---
        career = CareerStats()
        stats1 = GameStats()
        player1 = make_player(terminal, hp=80, cash=100)

        defeated = 0
        attempts = 0
        max_attempts = 200  # safety valve
        while defeated < 30 and attempts < max_attempts:
            attempts += 1
            cow = make_aggro_cow(terminal, player1, strength=3, hp=10, cash=30)
            survived = simulate_combat(player1, cow, stats1)
            if not survived:
                # Revive player to keep going (simulating restart)
                player1.hp = 80
            defeated = stats1.cows_defeated

        assert stats1.cows_defeated >= 30, f"Expected 30+ defeats, got {stats1.cows_defeated}"

        career.add_run_stats(stats1, victory=False)
        career.check_unlocks()
        career.save()

        # Verify career stats after run 1
        assert career.total_runs == 1
        assert career.total_cows_defeated >= 30

        # --- Run 2: load career, verify bonuses apply ---
        career2 = CareerStats.load()
        assert career2.total_cows_defeated >= 30, "Career stats should persist"

        bonuses = career2.get_starting_bonuses()
        # With 30 cows defeated, BONUS_HP_10 (requires 25) should be unlocked
        assert bonuses['extra_hp'] >= 10, f"Expected +10 HP bonus, got {bonuses['extra_hp']}"

        # Run 2 stats
        stats2 = GameStats()
        player2 = make_player(
            terminal,
            hp=20 + bonuses['extra_hp'],
            cash=50 + bonuses['extra_cash'],
        )

        for _ in range(10):
            cow = make_aggro_cow(terminal, player2, strength=3, hp=10, cash=30)
            survived = simulate_combat(player2, cow, stats2)
            if not survived:
                player2.hp = 50

        career2.add_run_stats(stats2, victory=False)
        career2.check_unlocks()

        # Career should accumulate across runs
        assert career2.total_runs == 2
        assert career2.total_cows_defeated >= 40


# ---------------------------------------------------------------------------
# Test 4 — Game ends on player death
# ---------------------------------------------------------------------------

class TestPlayerDeath:
    def test_game_ends_on_player_death(self):
        """Create a player with 1 HP and have a strong cow attack."""
        random.seed(123)
        terminal = MockTerminal()
        player = make_player(terminal, hp=1, cash=50)

        # Strong cow that will certainly kill the player
        cow = make_aggro_cow(terminal, player, strength=50, hp=200, cash=10)

        # A single cow attack should kill the player
        hp_before = player.hp
        CowAttack.cow_attack(player, cow)

        # Even if the first attack misses, keep attacking until dead
        max_rounds = 50
        rounds = 0
        while player.hp > 0 and rounds < max_rounds:
            CowAttack.cow_attack(player, cow)
            rounds += 1

        assert player.hp <= 0, f"Player should be dead, but has {player.hp} HP"


# ---------------------------------------------------------------------------
# Test 5 — Victory condition: cows defeated threshold
# ---------------------------------------------------------------------------

class TestVictoryCondition:
    def test_victory_condition_cows_defeated(self):
        """Set stats.cows_defeated to 49, defeat one more, verify victory."""
        random.seed(55)
        terminal = MockTerminal()
        player = make_player(terminal, hp=80, cash=100)
        stats = GameStats()
        stats.cows_defeated = VICTORY_COWS_DEFEATED - 1  # 49

        assert not stats.check_victory(), "Should not be victory yet"

        # Defeat one more cow
        cow = make_aggro_cow(terminal, player, strength=3, hp=10, cash=30)
        simulate_combat(player, cow, stats)

        assert stats.cows_defeated >= VICTORY_COWS_DEFEATED, (
            f"Expected {VICTORY_COWS_DEFEATED}+ cows defeated, got {stats.cows_defeated}"
        )
        assert stats.check_victory(), "Victory condition should be met"
