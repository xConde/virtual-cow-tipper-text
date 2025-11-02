"""
TextualAdapter - Modern Textual UI implementation of BaseUI interface.
This adapter provides the new Textual-based UI for the game.
"""

from typing import Optional, List, Dict, Any, Callable
from textual.app import App, ComposeResult
from textual.widgets import Label, Button, Input, Static, Header, Footer
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
import asyncio

from ui.interfaces.base_ui import BaseUI, UIMode, MenuChoice


class TextualAdapter(BaseUI):
    """
    Adapter that implements the UI using Textual framework.
    Provides modern terminal UI with CSS styling and reactive components.
    """

    def __init__(self):
        """Initialize the Textual adapter."""
        self.app: Optional[TextualApp] = None
        self.is_initialized = False
        self._current_screen = None
        self._event_queue = asyncio.Queue()

    async def initialize(self) -> None:
        """Setup Textual application."""
        try:
            # Create Textual app instance
            self.app = TextualApp(self)

            # Start app in background task
            self._app_task = asyncio.create_task(self.app.run_async())
            self.is_initialized = True

            # Wait for app to be ready
            await asyncio.sleep(0.1)

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Textual: {e}")

    async def shutdown(self) -> None:
        """Cleanup Textual application."""
        if self.is_initialized and self.app:
            try:
                await self.app.exit()
                if hasattr(self, '_app_task'):
                    self._app_task.cancel()
                    try:
                        await self._app_task
                    except asyncio.CancelledError:
                        pass
                self.is_initialized = False
            except:
                pass  # Ignore errors during cleanup

    # ==================== Display Methods ====================

    async def show_text(
        self,
        text: str,
        style: Optional[str] = None,
        duration: Optional[float] = None
    ) -> None:
        """Display text to the user."""
        if not self.app:
            print(text)  # Fallback
            return

        # TODO: Implement text display widget
        # For now, use notification system
        await self.show_notification(text, notification_type=style or "info")

        if duration:
            await asyncio.sleep(duration)

    async def show_menu(
        self,
        items: List[str],
        title: Optional[str] = None,
        allow_cancel: bool = True
    ) -> Optional[MenuChoice]:
        """Display menu and return user selection."""
        if not self.app:
            # Fallback
            for i, item in enumerate(items):
                print(f"{i+1}. {item}")
            try:
                choice = int(input("Choose: ")) - 1
                if 0 <= choice < len(items):
                    return MenuChoice(index=choice, label=items[choice], value=choice)
            except:
                pass
            return None

        # TODO: Implement menu screen
        # For now, return first item
        if items:
            return MenuChoice(index=0, label=items[0], value=0)
        return None

    async def get_input(
        self,
        prompt: str,
        validator: Optional[Callable[[str], bool]] = None,
        default: Optional[str] = None
    ) -> str:
        """Get text input from user with validation."""
        if not self.app:
            # Fallback
            result = input(f"{prompt}: ")
            return result if result else default or ""

        # TODO: Implement input dialog
        return default or ""

    # ==================== Game-Specific Displays ====================

    async def update_stats(
        self,
        player_stats: Dict[str, Any],
        cow_stats: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update status displays."""
        # TODO: Implement stats widget update
        pass

    async def show_combat(
        self,
        player_hp: tuple,
        cow_hp: tuple,
        combat_log: List[str]
    ) -> None:
        """Display combat state."""
        # TODO: Implement combat screen
        pass

    async def show_dialogue(
        self,
        speaker: str,
        text: str,
        choices: Optional[List[str]] = None
    ) -> Optional[int]:
        """Display dialogue with optional choices."""
        # TODO: Implement dialogue widget
        if not choices:
            await self.show_text(f"[{speaker}]: {text}")
            return None

        result = await self.show_menu(choices, title=f"[{speaker}]: {text}")
        return result.index if result else None

    async def show_inventory(
        self,
        items: List[Dict[str, Any]],
        equipped: Dict[str, Any]
    ) -> None:
        """Display inventory screen."""
        # TODO: Implement inventory screen
        pass

    async def show_shop(
        self,
        shop_items: List[Dict[str, Any]],
        player_cash: int,
        player_inventory: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Display shop interface."""
        # TODO: Implement shop screen
        return None

    # ==================== Event Handlers ====================

    async def on_pause(self) -> bool:
        """Handle pause request."""
        # TODO: Implement pause screen
        return True

    async def show_error(
        self,
        message: str,
        fatal: bool = False
    ) -> None:
        """Display error message."""
        # TODO: Implement error dialog
        await self.show_notification(message, notification_type="error")

        if fatal:
            await self.shutdown()
            import sys
            sys.exit(1)

    async def show_notification(
        self,
        message: str,
        notification_type: str = "info"
    ) -> None:
        """Display temporary notification."""
        if self.app:
            self.app.notify(message, severity=notification_type)

    # ==================== Screen Management ====================

    async def push_screen(
        self,
        screen_name: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Push a new screen onto the navigation stack."""
        # TODO: Implement screen navigation
        pass

    async def pop_screen(self) -> None:
        """Pop current screen from navigation stack."""
        # TODO: Implement screen navigation
        pass

    async def clear_screen(self) -> None:
        """Clear the current screen display."""
        # TODO: Implement screen clearing
        pass

    async def refresh(self) -> None:
        """Refresh the current screen."""
        if self.app:
            self.app.refresh()

    # ==================== Utility Methods ====================

    def get_mode(self) -> UIMode:
        """Get the UI mode of this implementation."""
        return UIMode.TEXTUAL


# ==================== Textual App Implementation ====================

class TextualApp(App):
    """Main Textual application."""

    CSS = """
    Screen {
        background: $surface;
    }

    Label {
        padding: 1;
    }

    Button {
        margin: 1;
    }

    .title {
        text-align: center;
        text-style: bold;
    }

    .stats-panel {
        dock: top;
        height: 3;
        background: $panel;
    }

    .content-area {
        padding: 1;
    }

    .menu-container {
        align: center middle;
        width: 50%;
    }
    """

    def __init__(self, adapter: TextualAdapter):
        """Initialize with reference to adapter."""
        super().__init__()
        self.adapter = adapter

    def compose(self) -> ComposeResult:
        """Create initial UI layout."""
        # TODO: Build full UI structure
        yield Header()
        yield Container(
            Label("Virtual Cow Tipper - Textual UI", classes="title"),
            Label("UI Implementation in Progress...", classes="content-area"),
            id="main-container"
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Handle app mount event."""
        self.title = "Virtual Cow Tipper"
        self.sub_title = "Textual Edition"


# ==================== Screen Implementations ====================

class MainMenuScreen(Screen):
    """Main menu screen."""

    def compose(self) -> ComposeResult:
        """Build main menu UI."""
        yield Container(
            Label("Virtual Cow Tipper", classes="title"),
            Vertical(
                Button("New Game", id="new_game"),
                Button("Continue", id="continue"),
                Button("Career", id="career"),
                Button("How to Play", id="how_to_play"),
                Button("Quit", id="quit"),
                classes="menu-container"
            )
        )


class GameScreen(Screen):
    """Main game screen."""

    def compose(self) -> ComposeResult:
        """Build game UI."""
        # TODO: Implement full game screen
        yield Container(
            Static("Game Screen - TODO", classes="title")
        )


class ShopScreen(Screen):
    """Shop interface screen."""

    def compose(self) -> ComposeResult:
        """Build shop UI."""
        # TODO: Implement shop screen
        yield Container(
            Static("Shop - TODO", classes="title")
        )


class InventoryScreen(Screen):
    """Inventory management screen."""

    def compose(self) -> ComposeResult:
        """Build inventory UI."""
        # TODO: Implement inventory screen
        yield Container(
            Static("Inventory - TODO", classes="title")
        )