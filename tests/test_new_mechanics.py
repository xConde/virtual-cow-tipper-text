"""
Tests for mechanics added in feat/velocity-stats-and-combat-pipeline:
- Shield defense in combat
- Power-up strength increment
- GameStats tracking
- Potion save/load roundtrip
- Career bonus application
"""
import random


class MockTerminal:
    """Shared mock terminal for all tests."""
    def set_player_stats(self, *args): pass
    def draw_player_stats(self): pass
    def draw_game_title(self): pass
    def draw_separator(self): pass
    def draw_dialog(self, text): pass
    def refresh(self): pass
    class stdscr:
        @staticmethod
        def refresh(): pass


# --- Shield Defense ---

def test_shield_blocks_damage():
    """Shield should reduce incoming damage."""
    from cow_attack import CowAttack
    from player import Player
    from item import Shield
    from cow import Cow
    from models import CowProperties

    random.seed(100)

    player = Player(MockTerminal(), "Shielded")
    player.hp = 50
    player.shield = Shield("Test Shield", 3, 8, "common", 1)

    props = CowProperties(
        name="Attacker", req_amount=10, likeliness=5, strength=8,
        hp=40, cash=10, is_shop=False, is_aggro=True, pack=1, approach="test"
    )
    cow = Cow(MockTerminal(), props)

    # Run many attacks, compare shielded vs unshielded damage
    shielded_total = 0
    unshielded_total = 0

    for seed in range(200):
        random.seed(seed)
        player.hp = 50
        player.shield = Shield("Test Shield", 3, 8, "common", 1)
        CowAttack.cow_attack(player, cow)
        shielded_total += (50 - player.hp)

        random.seed(seed)
        player.hp = 50
        player.shield = None
        CowAttack.cow_attack(player, cow)
        unshielded_total += (50 - player.hp)

    assert shielded_total < unshielded_total, \
        f"Shield should reduce total damage: shielded={shielded_total} vs unshielded={unshielded_total}"


def test_shield_full_absorb():
    """A strong shield can fully absorb a weak attack."""
    from cow_attack import CowAttack
    from player import Player
    from item import Shield
    from cow import Cow
    from models import CowProperties

    player = Player(MockTerminal(), "Tank")
    player.shield = Shield("Aegis", 10, 22, "legendairy", 5)

    props = CowProperties(
        name="Weakling", req_amount=5, likeliness=5, strength=3,
        hp=10, cash=5, is_shop=False, is_aggro=True, pack=1, approach="test"
    )
    cow = Cow(MockTerminal(), props)

    # With min shield 10 and weak cow (strength 3), many attacks should be fully absorbed
    full_absorbs = 0
    for seed in range(200):
        random.seed(seed)
        player.hp = 50
        msg = CowAttack.cow_attack(player, cow)
        if player.hp == 50 and "absorbs" in msg:
            full_absorbs += 1

    assert full_absorbs > 0, "Strong shield should fully absorb some weak attacks"


# --- Power-up Strength ---

def test_power_up_increases_strength():
    """Power-up snort should increment cow.strength."""
    from cow_attack import CowAttack
    from player import Player
    from cow import Cow
    from models import CowProperties

    player = Player(MockTerminal(), "Tester")
    player.hp = 100

    props = CowProperties(
        name="Beefy", req_amount=10, likeliness=5, strength=5,
        hp=40, cash=10, is_shop=False, is_aggro=True, pack=1, approach="test"
    )
    cow = Cow(MockTerminal(), props)

    initial_strength = cow.strength

    # Run attacks until power_up fires
    for seed in range(500):
        random.seed(seed)
        player.hp = 100  # Keep alive
        msg = CowAttack.cow_attack(player, cow)
        if "powers up" in msg:
            assert cow.strength > initial_strength, "Strength should have increased"
            return

    assert False, "Power-up never fired in 500 attempts"


# --- Stat Tracking ---

def test_game_stats_victory_conditions():
    """Victory conditions should work with tracked stats."""
    from models import GameStats

    stats = GameStats()
    assert not stats.check_victory()

    # Path 1: Cows defeated
    stats.cows_defeated = 50
    assert stats.check_victory()
    stats.cows_defeated = 0

    # Path 2: Cash earned
    stats.cash_earned = 5000
    assert stats.check_victory()
    stats.cash_earned = 0

    # Path 3: Legendary items
    stats.legendary_items_found = 3
    assert stats.check_victory()


def test_career_stats_accumulation():
    """Career stats should accumulate from GameStats correctly."""
    from career_stats import CareerStats
    from models import GameStats

    career = CareerStats()
    stats = GameStats()
    stats.cows_defeated = 10
    stats.cows_fled_from = 3
    stats.cash_earned = 500
    stats.total_damage_dealt = 200
    stats.dairy_cows_milked = 5
    stats.items_purchased = 8
    stats.legendary_items_found = 1

    career.add_run_stats(stats, victory=False)

    assert career.total_cows_defeated == 10
    assert career.total_cows_fled == 3
    assert career.total_cash_earned == 500
    assert career.total_damage_dealt == 200
    assert career.total_dairy_milked == 5
    assert career.total_items_purchased == 8
    assert career.total_legendary_found == 1
    assert career.total_runs == 1
    assert career.total_victories == 0

    # Second run
    career.add_run_stats(stats, victory=True)
    assert career.total_cows_defeated == 20
    assert career.total_runs == 2
    assert career.total_victories == 1


# --- Potion Save/Load ---

def test_potion_save_load_roundtrip():
    """Potions should survive save/load cycle."""
    from save_manager import SaveManager
    from models import GameStats
    from player import Player
    from item import HealthPotion, CowBell, Weapon

    player = Player(MockTerminal(), "Saver")
    player.hp = 30
    player.cash = 100
    player.inventory.append(HealthPotion('minor'))
    player.inventory.append(HealthPotion('greater'))
    player.inventory.append(CowBell())
    player.weapon = Weapon('Test Sword', 3, 8, 'common', 1)

    stats = GameStats()
    stats.cows_defeated = 5
    packs = {i: 0.0 for i in range(1, 7)}

    SaveManager.save_game(player, stats, packs, 2, 3)
    data = SaveManager.load_game()

    player2 = Player(MockTerminal(), "Saver")
    SaveManager.restore_player(player2, data)

    potion_count = sum(1 for i in player2.inventory if i.type == 'potion')
    assert potion_count == 2, f"Expected 2 potions, got {potion_count}"

    # Verify potion properties restored
    potions = [i for i in player2.inventory if i.type == 'potion']
    assert potions[0].boost_amount == 10  # minor heals 10
    assert potions[1].boost_amount == 40  # greater heals 40

    SaveManager.delete_save()


# --- Career Bonus Application ---

def test_career_damage_bonus():
    """Career damage bonus should increase player damage output."""
    from player import Player
    from cow import Cow
    from models import CowProperties

    props = CowProperties(
        name="Target", req_amount=10, likeliness=5, strength=5,
        hp=200, cash=10, is_shop=False, is_aggro=True, pack=1, approach="test"
    )

    # Without bonus
    base_total = 0
    for seed in range(100):
        random.seed(seed)
        player = Player(MockTerminal(), "NoBonusPlayer")
        player.hp = 50
        player.cash = 50
        cow = Cow(MockTerminal(), props)
        cow.hp = 200
        dmg, _ = player.deal_damage(cow)
        base_total += dmg

    # With +5 damage bonus
    bonus_total = 0
    for seed in range(100):
        random.seed(seed)
        player = Player(MockTerminal(), "BonusPlayer")
        player.hp = 50
        player.cash = 50
        player.damage_bonus = 5
        cow = Cow(MockTerminal(), props)
        cow.hp = 200
        dmg, _ = player.deal_damage(cow)
        bonus_total += dmg

    assert bonus_total > base_total, \
        f"Bonus damage should be higher: base={base_total}, bonus={bonus_total}"


# --- Shop Discount ---

def test_shop_discount_applied():
    """Career shop discount should reduce prices."""
    from item_factory import ItemFactory

    random.seed(42)
    items_full = ItemFactory.get_shop_inventory('neutral', 100, False, shop_discount=0.0)

    random.seed(42)
    items_disc = ItemFactory.get_shop_inventory('neutral', 100, False, shop_discount=0.10)

    for full, disc in zip(items_full, items_disc):
        assert disc['price'] <= full['price'], \
            f"Discounted price {disc['price']} should be <= full price {full['price']}"
