"""
TextualAdapter - Modern Textual UI implementation of BaseUI interface.
This adapter provides the new Textual-based UI for the game.
"""

from typing import Optional, List, Dict, Any, Callable
import asyncio
import sys
sys.path.insert(0, '.')

from ui.interfaces.base_ui import BaseUI, UIMode, MenuChoice
from ui.textual_app import VirtualCowTipperApp


class TextualAdapter(BaseUI):
    """
    Adapter that implements the UI using Textual framework.
    Provides modern terminal UI with CSS styling and reactive components.
    """

    def __init__(self):
        """Initialize the Textual adapter."""
        self.app: Optional[VirtualCowTipperApp] = None
        self.is_initialized = False
        self._response_queue = asyncio.Queue()
        self._app_task = None

    async def initialize(self) -> None:
        """Setup Textual application."""
        try:
            # Create Textual app instance
            self.app = VirtualCowTipperApp()

            # Set up response callback
            self.app.response_callback = self.send_response

            # Start app in background task
            self._app_task = asyncio.create_task(self._run_app())
            self.is_initialized = True

            # Wait for app to be ready
            await asyncio.sleep(0.5)

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Textual: {e}")

    async def _run_app(self) -> None:
        """Run the Textual app in background."""
        try:
            # Textual apps run synchronously, we need a different approach
            # Run in thread to avoid blocking
            import threading
            self._app_thread = threading.Thread(target=self.app.run, daemon=True)
            self._app_thread.start()
            # Give app time to start
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Textual app error: {e}")

    async def shutdown(self) -> None:
        """Cleanup Textual application."""
        if self.is_initialized and self.app:
            try:
                if self._app_task:
                    # Exit the app
                    self.app.exit()
                    # Cancel the task
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

        # Map style to severity for notifications
        severity_map = {
            "error": "error",
            "success": "success",
            "warning": "warning",
            "info": "information"
        }

        # Show as notification
        self.app.notify(text, severity=severity_map.get(style, "information"))

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
            # Fallback implementation
            for i, item in enumerate(items):
                print(f"{i+1}. {item}")
            try:
                choice = int(input("Choose: ")) - 1
                if 0 <= choice < len(items):
                    return MenuChoice(index=choice, label=items[choice], value=choice)
            except:
                pass
            return None

        # Create dialogue screen with choices
        screen_data = {
            'speaker': 'System',
            'text': title or "Select an option:",
            'choices': items
        }

        self.app.push_screen('dialogue', screen_data)

        # Wait for response
        try:
            response = await asyncio.wait_for(
                self._response_queue.get(),
                timeout=60.0
            )

            if response['action'] == 'choice':
                idx = response['index']
                return MenuChoice(index=idx, label=items[idx], value=idx)

        except asyncio.TimeoutError:
            pass

        return None if allow_cancel else await self.show_menu(items, title, False)

    async def get_input(
        self,
        prompt: str,
        validator: Optional[Callable[[str], bool]] = None,
        default: Optional[str] = None
    ) -> str:
        """Get text input from user with validation."""
        # For now, use notification and return default
        # Full input dialog would need custom screen
        self.app.notify(f"{prompt} (using default: {default})")
        return default or ""

    # ==================== Game-Specific Displays ====================

    async def update_stats(
        self,
        player_stats: Dict[str, Any],
        cow_stats: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update status displays."""
        if not self.app:
            return

        # Update reactive properties
        self.app.player_hp = player_stats.get('hp', self.app.player_hp)
        self.app.player_max_hp = player_stats.get('max_hp', self.app.player_max_hp)
        self.app.player_cash = player_stats.get('cash', self.app.player_cash)
        self.app.current_floor = player_stats.get('floor', self.app.current_floor)

        # Update via event
        await self.app.send_event('player_update', player_stats)

        if cow_stats:
            await self.app.send_event('cow_update', cow_stats)

    async def show_combat(
        self,
        player_hp: tuple,
        cow_hp: tuple,
        combat_log: List[str]
    ) -> None:
        """Display combat state."""
        if not self.app:
            return

        # Push combat screen if not already there
        if not self.app.navigation_stack or self.app.navigation_stack[-1] != 'combat':
            self.app.push_screen('combat')

        # Send combat update event
        await self.app.send_event('combat_update', {
            'player_hp': player_hp,
            'cow_hp': cow_hp,
            'log': combat_log
        })

    async def show_dialogue(
        self,
        speaker: str,
        text: str,
        choices: Optional[List[str]] = None
    ) -> Optional[int]:
        """Display dialogue with optional choices."""
        if not self.app:
            print(f"[{speaker}]: {text}")
            if choices:
                for i, choice in enumerate(choices):
                    print(f"{i+1}. {choice}")
                try:
                    idx = int(input("Choose: ")) - 1
                    if 0 <= idx < len(choices):
                        return idx
                except:
                    pass
            return None

        # Push dialogue screen
        screen_data = {
            'speaker': speaker,
            'text': text,
            'choices': choices
        }

        self.app.push_screen('dialogue', screen_data)

        if not choices:
            # No choices, just wait briefly
            await asyncio.sleep(2)
            self.app.pop_screen()
            return None

        # Wait for choice
        try:
            response = await asyncio.wait_for(
                self._response_queue.get(),
                timeout=60.0
            )

            if response['action'] == 'choice':
                return response['index']

        except asyncio.TimeoutError:
            pass

        return None

    async def show_inventory(
        self,
        items: List[Dict[str, Any]],
        equipped: Dict[str, Any]
    ) -> None:
        """Display inventory screen."""
        if not self.app:
            return

        # Push inventory screen with data
        screen_data = {
            'items': items,
            'equipped': equipped
        }

        self.app.push_screen('inventory', screen_data)

    async def show_shop(
        self,
        shop_items: List[Dict[str, Any]],
        player_cash: int,
        player_inventory: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Display shop interface."""
        if not self.app:
            return None

        # Update player cash
        self.app.player_cash = player_cash

        # Push shop screen with data
        screen_data = {
            'items': shop_items,
            'cash': player_cash,
            'inventory': player_inventory
        }

        self.app.push_screen('shop', screen_data)

        # Wait for purchase or exit
        try:
            response = await asyncio.wait_for(
                self._response_queue.get(),
                timeout=120.0
            )

            if response['action'] == 'buy':
                return response

        except asyncio.TimeoutError:
            pass

        return None

    # ==================== Event Handlers ====================

    async def on_pause(self) -> bool:
        """Handle pause request."""
        if not self.app:
            return True

        # Push pause screen
        self.app.push_screen('pause')

        # Wait for resume/quit
        try:
            response = await asyncio.wait_for(
                self._response_queue.get(),
                timeout=300.0  # 5 minute timeout
            )

            return response.get('resume', True)

        except asyncio.TimeoutError:
            return True

    async def show_error(
        self,
        message: str,
        fatal: bool = False
    ) -> None:
        """Display error message."""
        if self.app:
            self.app.notify(message, severity="error")
        else:
            print(f"ERROR: {message}")

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
            severity_map = {
                "info": "information",
                "success": "success",
                "warning": "warning",
                "error": "error"
            }
            self.app.notify(message, severity=severity_map.get(notification_type, "information"))
        else:
            print(f"[{notification_type.upper()}] {message}")

    # ==================== Screen Management ====================

    async def push_screen(
        self,
        screen_name: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Push a new screen onto the navigation stack."""
        if self.app:
            self.app.push_screen(screen_name, data)

    async def pop_screen(self) -> None:
        """Pop current screen from navigation stack."""
        if self.app:
            self.app.pop_screen()

    async def clear_screen(self) -> None:
        """Clear the current screen display."""
        # Textual handles this automatically
        pass

    async def refresh(self) -> None:
        """Refresh the current screen."""
        if self.app:
            self.app.refresh()

    # ==================== Utility Methods ====================

    def get_mode(self) -> UIMode:
        """Get the UI mode of this implementation."""
        return UIMode.TEXTUAL

    # ==================== Helper Methods ====================

    def send_response(self, response: Dict[str, Any]) -> None:
        """Send a response back to waiting methods."""
        asyncio.create_task(self._response_queue.put(response))