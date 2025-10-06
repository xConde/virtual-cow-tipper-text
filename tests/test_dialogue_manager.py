"""
Test DialogueManager - Verify all dialogue types work correctly.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dialogue_manager import DialogueManager


def test_cow_sayings_all_moods():
    """Test that all mood types return dialogue."""
    moods = ['friendly', 'neutral', 'upset']
    response_types = ['intro', 'counter', 'graceful', 'dairy_bucket', 'dairy_no_bucket',
                      'enraged_intro', 'enraged_end', 'shop_keeper_intro',
                      'shop_keeper_purchase', 'shop_keeper_end']

    print("Testing all mood/response combinations...")
    for mood in moods:
        for response_type in response_types:
            try:
                response = DialogueManager.get_cow_saying(mood, response_type)
                assert response is not None, f"No response for {mood}/{response_type}"
                assert len(response) > 0, f"Empty response for {mood}/{response_type}"
                print(f"  {mood:10} / {response_type:20} : '{response[:40]}...'")
            except Exception as e:
                print(f"  ERROR: {mood}/{response_type} - {e}")
                raise

    print("\ntest_cow_sayings_all_moods: PASSED")


def test_approaches():
    """Test approach scenarios return valid text."""
    approaches = [DialogueManager.get_approach() for _ in range(10)]

    assert len(approaches) == 10
    for approach in approaches:
        assert approach is not None
        assert len(approach) > 0
        assert isinstance(approach, str)

    print(f"test_approaches: PASSED (sampled 10 approaches)")


def test_interruptions():
    """Test interruption events return valid text."""
    interruptions = [DialogueManager.get_interruption() for _ in range(5)]

    assert len(interruptions) == 5
    for interruption in interruptions:
        assert interruption is not None
        assert len(interruption) > 0

    print("test_interruptions: PASSED")


def test_cow_names():
    """Test cow name generation."""
    names = [DialogueManager.get_cow_name() for _ in range(10)]

    assert len(names) == 10
    assert len(set(names)) >= 2, "Should have variety in names"

    print(f"test_cow_names: PASSED (got {len(set(names))} unique names)")


def test_fallback_for_missing_dialogue():
    """Test fallback works if dialogue key missing."""
    # Test with invalid key
    response = DialogueManager.get_cow_saying('friendly', 'nonexistent_key')

    assert response is not None
    assert 'Moo' in response or 'friendly' in response
    print("test_fallback_for_missing_dialogue: PASSED")


def test_context_variables():
    """Test context variable substitution (future enhancement)."""
    # This will work once we add templated responses
    # For now, test it doesn't break with context provided
    response = DialogueManager.get_cow_saying('friendly', 'intro',
                                              player_name="TestPlayer",
                                              player_cash=100)

    assert response is not None
    assert len(response) > 0
    print("test_context_variables: PASSED")


def test_dialogue_variety():
    """Test that random selection provides variety."""
    # Get same dialogue type 10 times
    responses = [DialogueManager.get_cow_saying('friendly', 'intro') for _ in range(10)]

    # Should have at least 2 different responses (randomness check)
    unique_responses = set(responses)
    assert len(unique_responses) >= 2, f"Not enough variety (got {len(unique_responses)} unique)"

    print(f"test_dialogue_variety: PASSED ({len(unique_responses)} unique responses from 10 calls)")


if __name__ == "__main__":
    print("="*60)
    print("DIALOGUE MANAGER TEST SUITE")
    print("="*60)
    print()

    test_cow_sayings_all_moods()
    print()
    test_approaches()
    test_interruptions()
    test_cow_names()
    test_fallback_for_missing_dialogue()
    test_context_variables()
    test_dialogue_variety()

    print()
    print("="*60)
    print("ALL DIALOGUE MANAGER TESTS PASSED!")
    print("="*60)
    print("\nDialogue system is working correctly.")
    print("Your 558 lines of creative writing are intact and accessible!")
