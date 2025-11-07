"""
Abstract base class for UI implementations.
Defines the interface that both Curses and Textual adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum


class UIMode(Enum):
    """UI implementation modes."""
    CURSES = "curses"
    TEXTUAL = "textual"


@dataclass
class MenuChoice:
    """Represents a user's menu selection."""
    index: int
    label: str
    value: Any


class BaseUI(ABC):
    """
    Abstract base class for UI implementations.

    All UI implementations (Curses, Textual) must implement these methods.
    This allows the game logic to remain UI-agnostic.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """
        Setup UI system.
        Called once at application start.
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """
        Cleanup UI system.
        Called once at application end.
        """
        pass

    # ==================== Display Methods ====================

    @abstractmethod
    async def show_text(
        self,
        text: str,
        style: Optional[str] = None,
        duration: Optional[float] = None
    ) -> None:
        """
        Display text to the user.

        Args:
            text: Text to display
            style: Optional style hint ("info", "warning", "error", "success")
            duration: Optional auto-dismiss duration in seconds
        """
        pass

    @abstractmethod
    async def show_menu(
        self,
        items: List[str],
        title: Optional[str] = None,
        allow_cancel: bool = True
    ) -> Optional[MenuChoice]:
        """
        Display menu and return user selection.

        Args:
            items: List of menu options
            title: Optional menu title
            allow_cancel: Whether ESC can cancel

        Returns:
            MenuChoice if selected, None if canceled
        """
        pass

    @abstractmethod
    async def get_input(
        self,
        prompt: str,
        validator: Optional[Callable[[str], bool]] = None,
        default: Optional[str] = None
    ) -> str:
        """
        Get text input from user with validation.

        Args:
            prompt: Input prompt text
            validator: Optional validation function
            default: Optional default value

        Returns:
            User input string
        """
        pass

    # ==================== Game-Specific Displays ====================

    @abstractmethod
    async def update_stats(
        self,
        player_stats: Dict[str, Any],
        cow_stats: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update status displays (HP, cash, equipment, etc.).

        Args:
            player_stats: Dict with 'hp', 'cash', 'weapon', 'shield', 'floor'
            cow_stats: Optional dict with 'name', 'hp', 'type', 'mood'
        """
        pass

    @abstractmethod
    async def show_combat(
        self,
        player_hp: tuple,
        cow_hp: tuple,
        combat_log: List[str]
    ) -> None:
        """
        Display combat state.

        Args:
            player_hp: (current, max) HP tuple
            cow_hp: (current, max) HP tuple
            combat_log: List of combat messages
        """
        pass

    @abstractmethod
    async def show_dialogue(
        self,
        speaker: str,
        text: str,
        choices: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Display dialogue with optional choices.

        Args:
            speaker: Who is speaking
            text: Dialogue text
            choices: Optional list of response choices

        Returns:
            Selected choice index if choices provided, None otherwise
        """
        pass

    @abstractmethod
    async def show_inventory(
        self,
        items: List[Dict[str, Any]],
        equipped: Dict[str, Any]
    ) -> None:
        """
        Display inventory screen.

        Args:
            items: List of item dicts
            equipped: Dict of currently equipped items
        """
        pass

    @abstractmethod
    async def show_shop(
        self,
        shop_items: List[Dict[str, Any]],
        player_cash: int,
        player_inventory: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Display shop interface.

        Args:
            shop_items: Items available for purchase
            player_cash: Player's current cash
            player_inventory: Player's inventory

        Returns:
            Transaction dict or None if exited
        """
        pass

    # ==================== Event Handlers ====================

    @abstractmethod
    async def on_pause(self) -> bool:
        """
        Handle pause request.

        Returns:
            True to resume game, False to quit
        """
        pass

    @abstractmethod
    async def show_error(
        self,
        message: str,
        fatal: bool = False
    ) -> None:
        """
        Display error message.

        Args:
            message: Error message
            fatal: Whether this is a fatal error
        """
        pass

    @abstractmethod
    async def show_notification(
        self,
        message: str,
        notification_type: str = "info"
    ) -> None:
        """
        Display temporary notification.

        Args:
            message: Notification text
            notification_type: "info", "success", "warning", or "error"
        """
        pass

    # ==================== Screen Management ====================

    @abstractmethod
    async def push_screen(
        self,
        screen_name: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Push a new screen onto the navigation stack.

        Args:
            screen_name: Name of screen to push
            data: Optional data to pass to screen
        """
        pass

    @abstractmethod
    async def pop_screen(self) -> None:
        """Pop current screen from navigation stack."""
        pass

    @abstractmethod
    async def clear_screen(self) -> None:
        """Clear the current screen display."""
        pass

    @abstractmethod
    async def refresh(self) -> None:
        """Refresh the current screen."""
        pass

    # ==================== Game Events ====================

    async def on_game_event(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Handle game events and update UI accordingly.

        This method can be overridden to handle specific events.
        Default implementation does nothing.

        Args:
            event_type: Type of event (e.g., "damage_dealt", "item_obtained")
            data: Event data dictionary
        """
        pass

    # ==================== Utility Methods ====================

    def get_mode(self) -> UIMode:
        """
        Get the UI mode of this implementation.

        Returns:
            UIMode enum value
        """
        raise NotImplementedError("Subclass must implement get_mode()")
