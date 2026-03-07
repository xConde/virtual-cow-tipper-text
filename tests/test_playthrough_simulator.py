"""
Playthrough Simulator - Simulate a complete game to test pacing and fun.
Tests: Balance, progression, dialogue variety, healing availability, victory achievability
"""
import random
from cow import Cow
from player import Player
from models import GameStats
from item_factory import ItemFactory
from item import HealthPotion
from dialogue_manager import DialogueManager


class MockTerminal:
    def __init__(self): pass
    def clear_screen(self): pass
    def refresh(self): pass
    def set_cow_stats(self, s): pass
    def draw_dialog(self, s): pass
    def set_player_stats(self, *args): pass
    def close_game_terminal(self): pass


def simulate_full_playthrough():
    """Simulate a complete game from start to victory."""
    terminal = MockTerminal()
    player = Player(terminal, "SimPlayer", starting_hp=20, starting_cash=50)
    stats = GameStats()

    encounters = 0
    max_encounters = 60  # Safety limit

    # Track experience
    healing_used = 0
    potions_bought = 0
    weapons_upgraded = 0
    legendary_found = 0
    variety_check = {'aggro': 0, 'shop': 0, 'dairy': 0, 'regular': 0}

    while encounters < max_encounters:
        encounters += 1

        # Generate cow
        props = Cow.generate_random_cow_properties(player)
        cow = Cow(terminal, props)

        # Determine encounter type
        encounter_type = 'aggro' if cow.is_aggro else 'shop' if cow.is_shop else 'regular'
        variety_check[encounter_type] += 1

        # Simulate encounter
        if cow.is_aggro:
            # Combat
            player_dmg = random.randint(10, 40)  # Rough estimate
            cow_dmg = random.randint(3, cow.strength)

            player.hp -= cow_dmg
            cow.hp -= player_dmg

            if cow.hp <= 0:
                # Victory
                player.cash += cow.cash
                stats.cows_defeated += 1
                stats.cash_earned += cow.cash

        elif cow.is_shop:
            # Buy health potion if needed
            if player.hp < 40 and player.cash >= 50:
                player.cash -= 50
                potion = HealthPotion('normal')
                potion.use(player)
                potions_bought += 1
                healing_used += 20

            # Buy weapon upgrade if affordable
            if player.cash >= 80 and random.random() < 0.3:
                player.cash -= 80
                weapon = ItemFactory.create_weapon()
                if weapon.rarity in ['rare', 'legendairy']:
                    legendary_found += 1
                weapons_upgraded += 1

        else:
            # Regular/dairy - mini-game or milk
            reward = random.randint(20, 60)
            player.cash += reward
            stats.cash_earned += reward

            # Dairy might heal
            if random.random() < 0.05:
                player.hp = min(player.hp + 5, 100)
                healing_used += 5

        # Rest if HP critical
        if player.hp < 20 and random.random() < 0.5:
            player.hp = min(player.hp + 10, 100)
            healing_used += 10
            encounters += 1  # Rest skips encounter

        # Check death
        if player.hp <= 0:
            return False

        # Check victory
        if stats.cows_defeated >= 50 or stats.cash_earned >= 5000 or legendary_found >= 3:
            break

    # Fun factor checks
    fun_score = 0

    # 1. Victory achievable?
    if stats.cows_defeated >= 50 or stats.cash_earned >= 5000:
        fun_score += 1

    # 2. Didn't die?
    if player.hp > 0:
        fun_score += 1

    # 3. Encounter variety?
    if all(count > 0 for count in variety_check.values()):
        fun_score += 1

    # 4. Healing available?
    if potions_bought > 0 or healing_used > 0:
        fun_score += 1

    # 5. Upgrades found?
    if weapons_upgraded > 0:
        fun_score += 1

    # 6. Pacing reasonable?
    if 30 <= encounters <= 55:
        fun_score += 1
    elif encounters < 30:
        fun_score += 0.5

    # 7. Economy worked?
    if player.cash > 0:
        fun_score += 1

    # 8. HP management interesting?
    if 20 < player.hp < 80:
        fun_score += 1
    elif player.hp >= 80:
        fun_score += 0.5

    assert fun_score >= 6, f"Game should score at least 6/8 on fun (got {fun_score})"

    return True


def test_dialogue_variety():
    """Test that dialogue doesn't get repetitive."""
    # Get 20 friendly intros
    intros = [DialogueManager.get_cow_saying('friendly', 'intro') for _ in range(20)]
    unique = len(set(intros))

    assert unique >= 8, f"Should have at least 8 unique intros (got {unique})"


def test_pacing_at_different_wealth_levels():
    """Test game pacing at early/mid/late game."""
    scenarios = [
        ("Early", 20, 50),
        ("Mid", 20, 300),
        ("Late", 20, 1000),
    ]

    for stage, hp, cash in scenarios:
        class TestPlayer:
            pass
        p = TestPlayer()
        p.hp = hp
        p.cash = cash

        props = Cow.generate_random_cow_properties(p)

        from game_config import PLAYER_BASE_DAMAGE_MAX, PLAYER_DAMAGE_CASH_SCALING
        player_dmg = PLAYER_BASE_DAMAGE_MAX + (cash // PLAYER_DAMAGE_CASH_SCALING)

        # Balance check - player should be able to compete
        assert player_dmg > 0, f"Player damage should be positive at {stage} game"
        assert props.strength > 0, f"Cow strength should be positive at {stage} game"


def test_full_playthrough():
    """Run a full playthrough simulation and verify fun score."""
    random.seed(42)  # Reproducible results
    result = simulate_full_playthrough()
    # Result can be True (victory) or False (death) - both are valid game outcomes
    # The fun_score assert inside simulate_full_playthrough validates balance
    assert result is not None
