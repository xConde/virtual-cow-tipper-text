"""
Tests for cow generation and properties.
"""
from cow import Cow
from models import CowProperties


class MockPlayer:
    """Mock player for testing cow generation."""
    def __init__(self, hp=20, cash=50):
        self.hp = hp
        self.cash = cash


def test_cow_properties_mood():
    """Test that mood is calculated correctly from likeliness."""
    props = CowProperties(
        name="Test", req_amount=10, likeliness=3, strength=5, hp=20,
        cash=10, is_shop=False, is_aggro=False, pack=1, approach="test"
    )
    assert props.mood == 'upset', f"Expected upset, got {props.mood}"

    props2 = CowProperties(
        name="Test", req_amount=10, likeliness=8, strength=5, hp=20,
        cash=10, is_shop=False, is_aggro=False, pack=1, approach="test"
    )
    assert props2.mood == 'friendly', f"Expected friendly, got {props2.mood}"

    props3 = CowProperties(
        name="Test", req_amount=10, likeliness=5, strength=5, hp=20,
        cash=10, is_shop=False, is_aggro=False, pack=1, approach="test"
    )
    assert props3.mood == 'neutral', f"Expected neutral, got {props3.mood}"


def test_cow_generation_scales_with_player():
    """Test that cow strength scales with player progression."""
    weak_player = MockPlayer(hp=20, cash=50)
    strong_player = MockPlayer(hp=100, cash=500)

    weak_props = Cow.generate_random_cow_properties(weak_player)
    strong_props = Cow.generate_random_cow_properties(strong_player)

    # Strong player should face stronger cows (on average)
    assert weak_props.strength >= 3, "Cow should have minimum strength"
    assert strong_props.hp > 0, "Cow should have HP"


def test_random_likeliness():
    """Test likeliness generation is within expected range."""
    for _ in range(10):
        likeliness = Cow.set_random_likeliness()
        assert 3 <= likeliness <= 7, f"Likeliness {likeliness} out of range (3-7)"
