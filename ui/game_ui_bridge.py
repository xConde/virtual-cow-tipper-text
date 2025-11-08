"""
GameUIBridge - Event management and communication between game logic and UI.
Provides a clean separation between game state and UI presentation.
"""

import asyncio
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from queue import Queue
import threading


class EventType(Enum):
    """Types of game events that can be sent to UI."""
    # Player events
    PLAYER_DAMAGED = auto()
    PLAYER_HEALED = auto()
    PLAYER_DIED = auto()
    PLAYER_LEVELED = auto()
    PLAYER_CASH_CHANGED = auto()

    # Cow events
    COW_SPAWNED = auto()
    COW_DAMAGED = auto()
    COW_DEFEATED = auto()
    COW_FLED = auto()
    COW_DIALOGUE = auto()

    # Combat events
    COMBAT_STARTED = auto()
    COMBAT_ENDED = auto()
    ATTACK_PERFORMED = auto()
    DEFENSE_PERFORMED = auto()

    # Item events
    ITEM_OBTAINED = auto()
    ITEM_EQUIPPED = auto()
    ITEM_USED = auto()
    ITEM_SOLD = auto()
    ITEM_BOUGHT = auto()

    # Game flow events
    FLOOR_CHANGED = auto()
    GAME_SAVED = auto()
    GAME_LOADED = auto()
    GAME_PAUSED = auto()
    GAME_RESUMED = auto()
    GAME_OVER = auto()
    GAME_WON = auto()

    # UI events
    SCREEN_CHANGED = auto()
    MENU_OPENED = auto()
    DIALOGUE_STARTED = auto()
    NOTIFICATION = auto()
    ERROR = auto()


@dataclass
class GameEvent:
    """Represents a game event to be processed by UI."""
    type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time())
    priority: int = 0  # Higher priority events processed first


class GameUIBridge:
    """
    Bridge between game logic and UI implementations.
    Manages event queue and state synchronization.
    """

    def __init__(self, ui_adapter):
        """
        Initialize bridge with a UI adapter.

        Args:
            ui_adapter: BaseUI implementation (CursesAdapter or TextualAdapter)
        """
        self.ui = ui_adapter
        self._event_queue = asyncio.Queue()
        self._event_handlers = {}
        self._running = False
        self._game_state = GameState()

        # Register default event handlers
        self._register_default_handlers()

    # ==================== Event Management ====================

    async def send_event(self, event: GameEvent) -> None:
        """
        Send an event from game logic to UI.

        Args:
            event: GameEvent to process
        """
        await self._event_queue.put(event)

    def send_event_sync(self, event_type: EventType, data: Dict[str, Any] = None) -> None:
        """
        Synchronously send an event (for non-async game code).

        Args:
            event_type: Type of event
            data: Event data dictionary
        """
        event = GameEvent(type=event_type, data=data or {})
        asyncio.create_task(self.send_event(event))

    async def process_events(self) -> None:
        """Process queued events."""
        while self._running:
            try:
                # Get event with timeout to allow checking _running flag
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=0.1
                )

                # Process event
                await self._handle_event(event)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                # Log error and continue processing
                print(f"Error processing event: {e}")

    async def _handle_event(self, event: GameEvent) -> None:
        """
        Handle a single event.

        Args:
            event: GameEvent to handle
        """
        # Update game state based on event
        self._update_game_state(event)

        # Call registered handlers
        if event.type in self._event_handlers:
            for handler in self._event_handlers[event.type]:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"Error in event handler for {event.type}: {e}")

        # Update UI based on event
        await self._update_ui_for_event(event)

    def register_handler(
        self,
        event_type: EventType,
        handler: Callable[[GameEvent], None]
    ) -> None:
        """
        Register a custom event handler.

        Args:
            event_type: Type of event to handle
            handler: Async function to call for this event
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    def _register_default_handlers(self) -> None:
        """Register default event handlers."""
        # These could be expanded based on game needs
        pass

    # ==================== State Management ====================

    def _update_game_state(self, event: GameEvent) -> None:
        """
        Update internal game state based on event.

        Args:
            event: Event that occurred
        """
        data = event.data

        if event.type == EventType.PLAYER_DAMAGED:
            self._game_state.player_hp = data.get('hp', self._game_state.player_hp)

        elif event.type == EventType.PLAYER_HEALED:
            self._game_state.player_hp = data.get('hp', self._game_state.player_hp)

        elif event.type == EventType.PLAYER_CASH_CHANGED:
            self._game_state.player_cash = data.get('cash', self._game_state.player_cash)

        elif event.type == EventType.COW_SPAWNED:
            self._game_state.current_cow = data.get('cow')

        elif event.type == EventType.COW_DEFEATED:
            self._game_state.current_cow = None
            self._game_state.cows_defeated += 1

        elif event.type == EventType.FLOOR_CHANGED:
            self._game_state.current_floor = data.get('floor', 1)

        # Add more state updates as needed

    async def _update_ui_for_event(self, event: GameEvent) -> None:
        """
        Update UI based on event type.

        Args:
            event: Event that occurred
        """
        data = event.data

        # Player stat updates
        if event.type in [EventType.PLAYER_DAMAGED, EventType.PLAYER_HEALED,
                          EventType.PLAYER_CASH_CHANGED, EventType.PLAYER_LEVELED]:
            await self.ui.update_stats(self._get_player_stats(), self._get_cow_stats())

        # Combat events
        elif event.type == EventType.COMBAT_STARTED:
            await self.ui.push_screen("combat", data)

        elif event.type == EventType.ATTACK_PERFORMED:
            combat_log = data.get('combat_log', [])
            player_hp = data.get('player_hp', (0, 0))
            cow_hp = data.get('cow_hp', (0, 0))
            await self.ui.show_combat(player_hp, cow_hp, combat_log)

        # Dialogue events
        elif event.type == EventType.COW_DIALOGUE:
            speaker = data.get('speaker', 'Cow')
            text = data.get('text', '')
            choices = data.get('choices')
            result = await self.ui.show_dialogue(speaker, text, choices)
            if result is not None:
                data['selected_choice'] = result

        # Item events
        elif event.type == EventType.ITEM_OBTAINED:
            item_name = data.get('item', {}).get('name', 'item')
            await self.ui.show_notification(
                f"Obtained {item_name}!",
                notification_type="success"
            )

        # Game flow events
        elif event.type == EventType.GAME_PAUSED:
            resume = await self.ui.on_pause()
            if resume:
                await self.send_event(GameEvent(type=EventType.GAME_RESUMED))
            else:
                await self.send_event(GameEvent(type=EventType.GAME_OVER))

        elif event.type == EventType.GAME_OVER:
            await self.ui.show_text(
                "GAME OVER\n" + data.get('message', ''),
                style="error"
            )
            self._running = False

        elif event.type == EventType.GAME_WON:
            await self.ui.show_text(
                "VICTORY!\n" + data.get('message', ''),
                style="success"
            )
            self._running = False

        # Notification events
        elif event.type == EventType.NOTIFICATION:
            await self.ui.show_notification(
                data.get('message', ''),
                notification_type=data.get('type', 'info')
            )

        elif event.type == EventType.ERROR:
            await self.ui.show_error(
                data.get('message', 'An error occurred'),
                fatal=data.get('fatal', False)
            )

    # ==================== Helper Methods ====================

    def _get_player_stats(self) -> Dict[str, Any]:
        """Get current player stats for UI display."""
        return {
            'hp': self._game_state.player_hp,
            'max_hp': self._game_state.player_max_hp,
            'cash': self._game_state.player_cash,
            'floor': self._game_state.current_floor,
            'weapon': self._game_state.equipped_weapon,
            'shield': self._game_state.equipped_shield,
        }

    def _get_cow_stats(self) -> Optional[Dict[str, Any]]:
        """Get current cow stats for UI display."""
        if not self._game_state.current_cow:
            return None

        cow = self._game_state.current_cow
        return {
            'name': cow.get('name', 'Cow'),
            'hp': (cow.get('hp', 0), cow.get('max_hp', 0)),
            'type': cow.get('type', 'Unknown'),
            'mood': cow.get('mood', 'Neutral'),
        }

    # ==================== Lifecycle Methods ====================

    async def start(self) -> None:
        """Start the bridge and UI."""
        self._running = True

        # Initialize UI
        await self.ui.initialize()

        # Start event processing
        self._event_task = asyncio.create_task(self.process_events())

        # Send initial event
        await self.send_event(
            GameEvent(
                type=EventType.SCREEN_CHANGED,
                data={'screen': 'main_menu'}
            )
        )

    async def stop(self) -> None:
        """Stop the bridge and cleanup."""
        self._running = False

        # Wait for event processing to stop
        if hasattr(self, '_event_task'):
            self._event_task.cancel()
            try:
                await self._event_task
            except asyncio.CancelledError:
                pass

        # Shutdown UI
        await self.ui.shutdown()


@dataclass
class GameState:
    """Internal game state tracked by the bridge."""
    # Player state
    player_hp: int = 20
    player_max_hp: int = 20
    player_cash: int = 50
    equipped_weapon: Optional[Dict[str, Any]] = None
    equipped_shield: Optional[Dict[str, Any]] = None

    # Game progress
    current_floor: int = 1
    cows_defeated: int = 0
    items_collected: int = 0

    # Current state
    current_cow: Optional[Dict[str, Any]] = None
    in_combat: bool = False
    game_paused: bool = False