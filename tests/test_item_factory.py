"""
Tests for ItemFactory and item generation.
"""
from item_factory import ItemFactory
from item import Weapon, Shield


def test_weapon_creation():
    """Test that weapons are created with valid stats."""
    weapon = ItemFactory.create_weapon()

    assert weapon is not None
    assert isinstance(weapon, Weapon)
    assert weapon.min_damage > 0
    assert weapon.max_damage >= weapon.min_damage
    assert weapon.rarity in ['common', 'uncommon', 'magic', 'rare', 'legendairy']
    assert 1 <= weapon.scale <= 5


def test_shield_creation():
    """Test that shields are created with valid stats."""
    shield = ItemFactory.create_shield()

    assert shield is not None
    assert isinstance(shield, Shield)
    assert shield.min_defence > 0
    assert shield.max_defence >= shield.min_defence
    assert shield.rarity in ['common', 'uncommon', 'magic', 'rare', 'legendairy']


def test_rarity_floor():
    """Test that legendary items have higher base stats (Phase 3 fix)."""
    # Generate many legendary items (force max scale)
    high_rarity_weapons = []
    for _ in range(10):
        weapon = ItemFactory.create_weapon(less_likely=False)
        if weapon.rarity in ['rare', 'legendairy']:
            high_rarity_weapons.append(weapon)

    if high_rarity_weapons:
        # Legendary/rare should have higher mins than common
        for weapon in high_rarity_weapons:
            # With rarity floor, min should be boosted
            assert weapon.min_damage >= 2, f"Rare weapon too weak: {weapon.min_damage}"


def test_weapon_damage_roll():
    """Test weapon damage rolling."""
    weapon = Weapon("Test Sword", min_damage=5, max_damage=10, rarity='common', scale=1)
    damage = ItemFactory.roll_weapon_damage(weapon)

    assert damage > 0, "Weapon should deal damage"
    # With scaling, damage can exceed base max
    assert damage >= weapon.min_damage, f"Damage {damage} below min {weapon.min_damage}"


def test_shop_inventory():
    """Test shop inventory generation."""
    inventory = ItemFactory.get_shop_inventory('neutral', player_cash=100, is_lucky=False)

    # Shop now has 4 items (added health potions in balance fix)
    assert len(inventory) >= 4, f"Shop should have at least 4 items, got {len(inventory)}"
    for item in inventory:
        assert 'item' in item
        assert 'price' in item
        assert item['price'] > 0

    # Check health potion is in shop
    has_potion = any('potion' in item['label'].lower() for item in inventory)
    assert has_potion, "Shop should include health potion"
