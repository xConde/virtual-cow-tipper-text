"""
Test meta-progression and career stats system.
"""
import os

from career_stats import CareerStats, Unlock
from models import GameStats


def test_career_stats_creation():
    """Test career stats can be created and saved."""
    career = CareerStats()

    assert career.total_runs == 0
    assert career.total_cows_defeated == 0
    assert len(career.unlocks) == 0


def test_unlock_checking():
    """Test unlock thresholds work correctly."""
    career = CareerStats()

    # No unlocks initially
    unlocks = career.check_unlocks()
    assert len(unlocks) == 0

    # Add stats to trigger unlock
    career.total_cows_defeated = 25

    unlocks = career.check_unlocks()
    assert Unlock.BONUS_HP_10 in unlocks, "Should unlock +10 HP at 25 cows"

    # Second check shouldn't return same unlock
    unlocks2 = career.check_unlocks()
    assert len(unlocks2) == 0, "Already unlocked items shouldn't unlock again"


def test_starting_bonuses():
    """Test starting bonuses are calculated from unlocks."""
    career = CareerStats()

    # No unlocks = no bonuses
    bonuses = career.get_starting_bonuses()
    assert bonuses['extra_hp'] == 0
    assert bonuses['extra_cash'] == 0
    assert len(bonuses['starting_items']) == 0

    # Add unlocks
    career.unlocks = [Unlock.BONUS_HP_10, Unlock.BONUS_CASH_25, Unlock.STARTING_COWBELL]

    bonuses = career.get_starting_bonuses()
    assert bonuses['extra_hp'] == 10
    assert bonuses['extra_cash'] == 25
    assert 'cowbell' in bonuses['starting_items']


def test_run_stats_accumulation():
    """Test that run stats accumulate correctly."""
    career = CareerStats()

    # Simulate first run
    run1_stats = GameStats(
        cows_defeated=10,
        cash_earned=200,
        dairy_cows_milked=2
    )

    career.add_run_stats(run1_stats, victory=False)

    assert career.total_runs == 1
    assert career.total_cows_defeated == 10
    assert career.total_cash_earned == 200
    assert career.total_victories == 0

    # Simulate second run (victory)
    run2_stats = GameStats(
        cows_defeated=50,
        cash_earned=1500,
        dairy_cows_milked=5
    )

    career.add_run_stats(run2_stats, victory=True)

    assert career.total_runs == 2
    assert career.total_cows_defeated == 60  # 10 + 50
    assert career.total_cash_earned == 1700  # 200 + 1500
    assert career.total_victories == 1
    assert career.total_dairy_milked == 7


def test_multiple_unlocks():
    """Test earning multiple unlocks at once."""
    career = CareerStats()

    # Set stats to trigger multiple unlocks
    career.total_cows_defeated = 100  # Triggers: +10 HP, +20 HP, starting weapon
    career.total_cash_earned = 5000   # Triggers: +$25, +$50

    unlocks = career.check_unlocks()

    # Should unlock 5 things
    assert len(unlocks) >= 3, f"Should unlock at least 3 items, got {len(unlocks)}"


def test_save_load_career():
    """Test career stats persist across sessions."""
    # Clean up any existing file
    if os.path.exists("career_stats.json"):
        os.remove("career_stats.json")

    # Create and save career
    career1 = CareerStats()
    career1.total_cows_defeated = 30
    career1.total_cash_earned = 800
    career1.unlocks = [Unlock.BONUS_HP_10]
    career1.save()

    # Load in new instance
    career2 = CareerStats.load()

    assert career2.total_cows_defeated == 30
    assert career2.total_cash_earned == 800
    assert Unlock.BONUS_HP_10 in career2.unlocks

    # Cleanup
    if os.path.exists("career_stats.json"):
        os.remove("career_stats.json")
