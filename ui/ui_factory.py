"""
UI Factory for creating UI implementations.
"""

from typing import Dict, Type, Optional, List
from .interfaces import BaseUI, UIMode


class UIFactory:
    """
    Factory for creating and managing UI implementations.

    Usage:
        # Register implementations
        UIFactory.register(UIMode.CURSES, CursesAdapter)
        UIFactory.register(UIMode.TEXTUAL, TextualAdapter)

        # Create UI
        ui = UIFactory.create(UIMode.TEXTUAL)

        # Get current UI
        current = UIFactory.get_current()
    """

    _registry: Dict[UIMode, Type[BaseUI]] = {}
    _current_ui: Optional[BaseUI] = None

    @classmethod
    def register(cls, mode: UIMode, ui_class: Type[BaseUI]) -> None:
        """
        Register a UI implementation.

        Args:
            mode: UI mode enum
            ui_class: UI class implementing BaseUI
        """
        if not issubclass(ui_class, BaseUI):
            raise TypeError(f"{ui_class} must be a subclass of BaseUI")

        cls._registry[mode] = ui_class
        print(f"✓ Registered UI mode: {mode.value} -> {ui_class.__name__}")

    @classmethod
    def create(cls, mode: UIMode, **kwargs) -> BaseUI:
        """
        Create a UI instance for the specified mode.

        Args:
            mode: UI mode to create
            **kwargs: Additional arguments to pass to UI constructor

        Returns:
            UI instance

        Raises:
            ValueError: If mode not registered
        """
        if mode not in cls._registry:
            available = ", ".join([m.value for m in cls._registry.keys()])
            raise ValueError(
                f"UI mode {mode.value} not registered. "
                f"Available: {available or 'none'}"
            )

        ui_class = cls._registry[mode]
        instance = ui_class(**kwargs)
        cls._current_ui = instance

        print(f"✓ Created UI: {mode.value} ({ui_class.__name__})")
        return instance

    @classmethod
    def get_current(cls) -> Optional[BaseUI]:
        """
        Get the currently active UI instance.

        Returns:
            Current UI or None if none created
        """
        return cls._current_ui

    @classmethod
    def list_registered(cls) -> List[UIMode]:
        """
        List all registered UI modes.

        Returns:
            List of registered UI modes
        """
        return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, mode: UIMode) -> bool:
        """
        Check if a UI mode is registered.

        Args:
            mode: UI mode to check

        Returns:
            True if registered
        """
        return mode in cls._registry

    @classmethod
    def clear_registry(cls) -> None:
        """
        Clear all registered UI implementations.
        Useful for testing.
        """
        cls._registry.clear()
        cls._current_ui = None
