#!/usr/bin/env python3
"""
Comprehensive test suite for Virtual Cow Tipper Textual UI migration.
Tests all components of the new UI system.
"""

import sys
import os
import unittest
import asyncio
from unittest.mock import Mock, patch, MagicMock

# Add paths
sys.path.insert(0, './venv_textual/lib/python3.13/site-packages')
sys.path.insert(0, '.')


class TestUIAbstraction(unittest.TestCase):
    """Test the UI abstraction layer."""

    def test_base_ui_interface(self):
        """Test BaseUI interface is properly defined."""
        from ui.interfaces.base_ui import BaseUI, UIMode, MenuChoice

        # Check UIMode enum
        self.assertTrue(hasattr(UIMode, 'CURSES'))
        self.assertTrue(hasattr(UIMode, 'TEXTUAL'))

        # Check MenuChoice dataclass
        choice = MenuChoice(index=0, label="Test", value="test")
        self.assertEqual(choice.index, 0)
        self.assertEqual(choice.label, "Test")

        # Check abstract methods
        required_methods = [
            'initialize', 'shutdown', 'show_text', 'show_menu',
            'get_input', 'update_stats', 'show_combat', 'show_dialogue'
        ]
        for method in required_methods:
            self.assertTrue(hasattr(BaseUI, method))

    def test_curses_adapter(self):
        """Test CursesAdapter implementation."""
        from ui.adapters.curses_adapter import CursesAdapter
        from ui.interfaces.base_ui import UIMode

        adapter = CursesAdapter()
        self.assertEqual(adapter.get_mode(), UIMode.CURSES)

        # Check all methods are implemented
        methods = [
            'initialize', 'shutdown', 'show_text', 'show_menu',
            'get_input', 'update_stats', 'show_combat', 'show_dialogue',
            'show_inventory', 'show_shop', 'on_pause', 'show_error',
            'show_notification', 'push_screen', 'pop_screen',
            'clear_screen', 'refresh'
        ]
        for method in methods:
            self.assertTrue(hasattr(adapter, method))
            self.assertTrue(callable(getattr(adapter, method)))

    def test_textual_adapter(self):
        """Test TextualAdapter implementation."""
        from ui.adapters.textual_adapter import TextualAdapter
        from ui.interfaces.base_ui import UIMode

        adapter = TextualAdapter()
        self.assertEqual(adapter.get_mode(), UIMode.TEXTUAL)

        # Check implementation completeness
        self.assertTrue(hasattr(adapter, 'app'))
        self.assertTrue(hasattr(adapter, 'initialize'))
        self.assertTrue(hasattr(adapter, 'shutdown'))


class TestTextualApp(unittest.TestCase):
    """Test the Textual application structure."""

    def test_app_creation(self):
        """Test VirtualCowTipperApp can be created."""
        from ui.textual_app import VirtualCowTipperApp

        app = VirtualCowTipperApp()
        self.assertIsNotNone(app)
        self.assertEqual(app.TITLE, "Virtual Cow Tipper")

    def test_screen_registration(self):
        """Test all screens are registered."""
        from ui.textual_app import VirtualCowTipperApp

        app = VirtualCowTipperApp()
        screens = [
            'main_menu', 'game', 'combat', 'shop', 'inventory',
            'pause', 'help', 'career', 'dialogue', 'save_game',
            'load_game', 'save_prompt', 'game_over', 'victory'
        ]

        for screen_name in screens:
            screen_class = app.get_screen_class(screen_name)
            self.assertIsNotNone(screen_class, f"Screen '{screen_name}' not found")

    def test_reactive_properties(self):
        """Test reactive properties are defined."""
        from ui.textual_app import VirtualCowTipperApp

        app = VirtualCowTipperApp()
        self.assertEqual(app.player_hp, 20)
        self.assertEqual(app.player_max_hp, 20)
        self.assertEqual(app.player_cash, 50)
        self.assertEqual(app.current_floor, 1)
        self.assertEqual(app.game_active, False)


class TestGameIntegration(unittest.TestCase):
    """Test game logic integration."""

    def test_game_state_manager(self):
        """Test GameStateManager initialization."""
        from game_textual_integration import GameStateManager

        state = GameStateManager()
        self.assertEqual(state.player_hp, 20)
        self.assertEqual(state.player_cash, 50)
        self.assertEqual(state.current_floor, 1)
        self.assertIsNone(state.current_cow)
        self.assertEqual(len(state.inventory), 0)

    def test_textual_game_adapter(self):
        """Test TextualGameAdapter creation."""
        from game_textual_integration import TextualGameAdapter

        adapter = TextualGameAdapter()
        self.assertIsNotNone(adapter.ui)
        self.assertIsNotNone(adapter.bridge)
        self.assertIsNotNone(adapter.state)

        # Check methods exist
        methods = [
            'start', 'stop', 'main_menu', 'start_new_game',
            'game_loop', 'spawn_cow', 'cow_encounter', 'combat',
            'rest', 'show_inventory', 'visit_shop', 'save_and_quit',
            'game_over', 'victory', 'update_ui_stats'
        ]
        for method in methods:
            self.assertTrue(hasattr(adapter, method))


class TestUIBridge(unittest.TestCase):
    """Test the GameUIBridge."""

    def test_bridge_creation(self):
        """Test GameUIBridge can be created."""
        from ui.game_ui_bridge import GameUIBridge
        from ui.adapters.curses_adapter import CursesAdapter

        ui = CursesAdapter()
        bridge = GameUIBridge(ui)
        self.assertIsNotNone(bridge)
        self.assertEqual(bridge.ui, ui)

    def test_event_types(self):
        """Test all event types are defined."""
        from ui.game_ui_bridge import EventType

        required_events = [
            'PLAYER_DAMAGED', 'PLAYER_HEALED', 'PLAYER_DIED',
            'COW_SPAWNED', 'COW_DEFEATED', 'COMBAT_STARTED',
            'ITEM_OBTAINED', 'GAME_OVER', 'NOTIFICATION'
        ]

        for event_name in required_events:
            self.assertTrue(hasattr(EventType, event_name))

    def test_game_event(self):
        """Test GameEvent creation."""
        from ui.game_ui_bridge import GameEvent, EventType

        event = GameEvent(
            type=EventType.PLAYER_DAMAGED,
            data={'damage': 5, 'hp': 15}
        )
        self.assertEqual(event.type, EventType.PLAYER_DAMAGED)
        self.assertEqual(event.data['damage'], 5)


class TestASCIIArt(unittest.TestCase):
    """Test ASCII art module."""

    def test_cow_art(self):
        """Test cow ASCII art generation."""
        from ui.ascii_art import get_cow_art

        # Test different cow types
        normal = get_cow_art("normal")
        self.assertIn("(oo)", normal)

        aggressive = get_cow_art("aggressive")
        self.assertIn("(><)", aggressive)

        boss = get_cow_art("boss")
        self.assertIn("BOSS COW", boss)

        tipped = get_cow_art("normal", tipped=True)
        self.assertIn("tipped", tipped)

    def test_icons(self):
        """Test icon retrieval."""
        from ui.ascii_art import get_item_icon, get_status_icon, get_mood_indicator

        # Item icons
        self.assertEqual(get_item_icon('weapon'), '⚔️ ')
        self.assertEqual(get_item_icon('shield'), '🛡️ ')

        # Status icons
        self.assertEqual(get_status_icon('hp'), '❤️ ')
        self.assertEqual(get_status_icon('cash'), '💰')

        # Mood indicators
        self.assertEqual(get_mood_indicator('happy'), '😊')
        self.assertEqual(get_mood_indicator('angry'), '😠')


class TestPerformance(unittest.TestCase):
    """Test performance optimization."""

    def test_performance_config(self):
        """Test PerformanceConfig settings."""
        from ui.performance_config import PerformanceConfig

        # Check key settings
        self.assertEqual(PerformanceConfig.MAX_FPS, 60)
        self.assertTrue(PerformanceConfig.ENABLE_DIRTY_TRACKING)
        self.assertEqual(PerformanceConfig.MAX_LOG_ENTRIES, 100)

    def test_optimized_config(self):
        """Test system-based optimization."""
        from ui.performance_config import PerformanceConfig

        config = PerformanceConfig.get_optimized_config()
        # Just check that config is returned with expected keys
        self.assertIn('quality', config)
        self.assertIn('max_fps', config)
        self.assertIn('enable_animations', config)
        self.assertIn('max_widgets', config)

    def test_performance_monitor(self):
        """Test PerformanceMonitor."""
        from ui.performance_config import PerformanceMonitor

        monitor = PerformanceMonitor()
        monitor.enabled = True

        # Simulate frame timing
        monitor.start_frame()
        # Simulate some work
        import time
        time.sleep(0.01)  # 10ms
        monitor.end_frame()

        # Check metrics were recorded
        self.assertGreater(len(monitor.metrics['frame_times']), 0)

        # Get stats
        stats = monitor.get_stats()
        self.assertIn('avg_frame_time', stats)
        self.assertIn('fps', stats)


class TestUIFactory(unittest.TestCase):
    """Test UIFactory functionality."""

    def test_registration(self):
        """Test UI registration and creation."""
        from ui.ui_factory import UIFactory
        from ui.interfaces.base_ui import UIMode
        from ui.adapters.curses_adapter import CursesAdapter

        # Clear registry
        UIFactory.clear_registry()

        # Register adapter
        UIFactory.register(UIMode.CURSES, CursesAdapter)
        self.assertTrue(UIFactory.is_registered(UIMode.CURSES))

        # Create instance
        ui = UIFactory.create(UIMode.CURSES)
        self.assertIsInstance(ui, CursesAdapter)
        self.assertEqual(UIFactory.get_current(), ui)


class TestIntegration(unittest.TestCase):
    """End-to-end integration tests."""

    def test_full_stack(self):
        """Test all components work together."""
        # Import all major components
        from ui.interfaces.base_ui import BaseUI, UIMode
        from ui.adapters.curses_adapter import CursesAdapter
        from ui.adapters.textual_adapter import TextualAdapter
        from ui.textual_app import VirtualCowTipperApp
        from ui.game_ui_bridge import GameUIBridge
        from game_textual_integration import TextualGameAdapter
        from ui.ui_factory import UIFactory

        # Verify all imports successful
        self.assertTrue(all([
            BaseUI, UIMode, CursesAdapter, TextualAdapter,
            VirtualCowTipperApp, GameUIBridge, TextualGameAdapter, UIFactory
        ]))

    def test_both_ui_modes(self):
        """Test both UI modes are available."""
        from ui.interfaces.base_ui import UIMode
        from ui.ui_factory import UIFactory
        from ui.adapters import CursesAdapter

        UIFactory.clear_registry()
        UIFactory.register(UIMode.CURSES, CursesAdapter)

        # Try Textual if available
        try:
            from ui.adapters import TextualAdapter
            if TextualAdapter:
                UIFactory.register(UIMode.TEXTUAL, TextualAdapter)
                self.assertTrue(UIFactory.is_registered(UIMode.TEXTUAL))
        except ImportError:
            pass  # Textual not available

        # Curses should always be available
        self.assertTrue(UIFactory.is_registered(UIMode.CURSES))


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestUIAbstraction,
        TestTextualApp,
        TestGameIntegration,
        TestUIBridge,
        TestASCIIArt,
        TestPerformance,
        TestUIFactory,
        TestIntegration
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)