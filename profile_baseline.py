#!/usr/bin/env python3
"""
Baseline performance profiling for Virtual Cow Tipper
Profiles core game operations (non-UI) before migration
"""

import cProfile
import pstats
import io
from cow import Cow
from player import Player
from item_factory import ItemFactory
from dialogue_manager import DialogueManager
import time

# Mock terminal for Player
class MockTerminal:
    def set_player_stats(self, *args): pass
    def draw_player_stats(self, *args): pass

def profile_cow_generation():
    """Profile cow generation"""
    mock_player = Player(MockTerminal(), "TestPlayer")
    for _ in range(1000):
        props = Cow.generate_random_cow_properties(mock_player)
        cow = Cow(MockTerminal(), props)

def profile_item_creation():
    """Profile item creation"""
    for _ in range(1000):
        weapon = ItemFactory.create_weapon()
        shield = ItemFactory.create_shield()

def profile_dialogue():
    """Profile dialogue system"""
    for _ in range(1000):
        DialogueManager.get_cow_saying("friendly", "greeting")
        DialogueManager.get_approach()
        DialogueManager.get_interruption()

def run_profiling():
    """Run all profiling tasks"""
    print("=" * 60)
    print("VIRTUAL COW TIPPER - PERFORMANCE BASELINE")
    print("=" * 60)
    print()

    # Profile cow generation
    print("Profiling cow generation (1000 iterations)...")
    start = time.perf_counter()
    profile_cow_generation()
    end = time.perf_counter()
    print(f"  Time: {(end - start) * 1000:.2f}ms")
    print(f"  Per cow: {(end - start) * 1000000 / 1000:.2f}μs")
    print()

    # Profile item creation
    print("Profiling item creation (1000 iterations)...")
    start = time.perf_counter()
    profile_item_creation()
    end = time.perf_counter()
    print(f"  Time: {(end - start) * 1000:.2f}ms")
    print(f"  Per item: {(end - start) * 1000000 / 2000:.2f}μs")
    print()

    # Profile dialogue
    print("Profiling dialogue system (1000 iterations)...")
    start = time.perf_counter()
    profile_dialogue()
    end = time.perf_counter()
    print(f"  Time: {(end - start) * 1000:.2f}ms")
    print(f"  Per dialogue: {(end - start) * 1000000 / 3000:.2f}μs")
    print()

    # Detailed cProfile
    print("=" * 60)
    print("DETAILED PROFILING (cProfile)")
    print("=" * 60)
    print()

    profiler = cProfile.Profile()
    profiler.enable()

    # Run all operations
    profile_cow_generation()
    profile_item_creation()
    profile_dialogue()

    profiler.disable()

    # Save stats
    profiler.dump_stats('curses_profile.stats')

    # Print top 20 functions by cumulative time
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)

    print(s.getvalue())

    print()
    print("=" * 60)
    print("Profile saved to: curses_profile.stats")
    print("Use: python -m pstats curses_profile.stats")
    print("=" * 60)

if __name__ == "__main__":
    run_profiling()
