"""
Main Textual Application Shell for Virtual Cow Tipper.
Provides the core application structure and screen management.
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Label, Button, ProgressBar, Log
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from typing import Optional, Dict, Any, List
import asyncio
import sys
sys.path.insert(0, '.')

from ui.ascii_art import (
    TITLE_ART_COMPACT,
    get_cow_art,
    SHOP_BANNER,
    COMBAT_BANNER,
    VICTORY_ART,
    GAME_OVER_ART,
    get_item_icon,
    get_status_icon,
    get_mood_indicator
)


class VirtualCowTipperApp(App):
    """
    Main Textual application for Virtual Cow Tipper.
    Manages screens, themes, and global application state.
    """

    CSS_PATH = "ui/styles/main.css"
    TITLE = "Virtual Cow Tipper"
    SUB_TITLE = "Textual Edition"

    DEFAULT_CSS = """
    Screen {
        background: $surface;
        overflow: hidden;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("escape", "back", "Back", show=False),
        Binding("f1", "help", "Help"),
        Binding("f2", "save", "Save"),
        Binding("f3", "load", "Load"),
        Binding("p", "pause", "Pause", show=False),
    ]

    # Application state
    player_name: reactive[str] = reactive("")
    player_hp: reactive[int] = reactive(20)
    player_max_hp: reactive[int] = reactive(20)
    player_cash: reactive[int] = reactive(50)
    current_floor: reactive[int] = reactive(1)
    game_active: reactive[bool] = reactive(False)

    def __init__(self, *args, **kwargs):
        """Initialize the application."""
        super().__init__(*args, **kwargs)
        self.navigation_stack = []
        self.game_state = {}
        self.event_queue = asyncio.Queue()
        self.event_handlers = {}
        self.response_callback = None  # For sending responses back to adapter

    def compose(self) -> ComposeResult:
        """Create the application layout."""
        yield Header()
        yield Footer()

    async def on_mount(self) -> None:
        """Handle application mount."""
        # Clear and set solid background for entire application
        self.screen.styles.background = "$surface"
        self.screen.styles.overflow_x = "hidden"
        self.screen.styles.overflow_y = "hidden"

        # Don't automatically push main_menu - let the game control flow via dialogue screens
        # The game will use show_menu() to display options

        # Start event processing
        asyncio.create_task(self._process_events())

    async def action_quit(self) -> None:
        """Quit the application."""
        if self.game_active:
            # Show save prompt
            self.push_screen("save_prompt")
        else:
            self.exit()

    async def action_back(self) -> None:
        """Go back to previous screen."""
        if len(self.navigation_stack) > 1:
            self.pop_screen()

    async def action_help(self) -> None:
        """Show help screen."""
        self.push_screen("help")

    async def action_save(self) -> None:
        """Save the game."""
        if self.game_active:
            self.push_screen("save_game")

    async def action_load(self) -> None:
        """Load a saved game."""
        self.push_screen("load_game")

    async def action_pause(self) -> None:
        """Pause the game."""
        if self.game_active:
            self.push_screen("pause")

    # ==================== Event Management ====================

    async def _process_events(self) -> None:
        """Process game events from the queue."""
        while True:
            try:
                event = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=0.1
                )
                await self._handle_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.notify(f"Error processing event: {e}", severity="error")

    async def _handle_event(self, event: Dict[str, Any]) -> None:
        """Handle a single game event."""
        event_type = event.get('type')
        data = event.get('data', {})

        # Update reactive properties based on event
        if event_type == 'player_update':
            self.player_hp = data.get('hp', self.player_hp)
            self.player_cash = data.get('cash', self.player_cash)
            self.current_floor = data.get('floor', self.current_floor)

        # Call registered handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(data)
                except Exception as e:
                    self.notify(f"Error in event handler: {e}", severity="error")

    def register_event_handler(self, event_type: str, handler) -> None:
        """Register a handler for a specific event type."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def send_event(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Send an event to be processed."""
        await self.event_queue.put({
            'type': event_type,
            'data': data or {}
        })

    # ==================== Screen Management ====================

    def get_screen_class(self, name: str) -> type:
        """Get screen class by name."""
        screens = {
            'main_menu': MainMenuScreen,
            'game': GameScreen,
            'shop': ShopScreen,
            'inventory': InventoryScreen,
            'pause': PauseScreen,
            'help': HelpScreen,
            'career': CareerScreen,
            'save_game': SaveGameScreen,
            'load_game': LoadGameScreen,
            'save_prompt': SavePromptScreen,
            'combat': CombatScreen,
            'dialogue': DialogueScreen,
            'game_over': GameOverScreen,
            'victory': VictoryScreen,
        }
        return screens.get(name, Screen)

    def push_screen(self, name: str, data: Dict[str, Any] = None) -> None:
        """Push a new screen onto the stack."""
        screen_class = self.get_screen_class(name)
        screen = screen_class(data=data) if data else screen_class()
        self.navigation_stack.append(name)
        super().push_screen(screen)

    def pop_screen(self) -> None:
        """Pop the current screen."""
        if self.navigation_stack:
            self.navigation_stack.pop()
        super().pop_screen()

    def switch_screen(self, name: str, data: Dict[str, Any] = None) -> None:
        """Switch to a different screen (replace current)."""
        self.pop_screen()
        self.push_screen(name, data)

    def send_response(self, response: Dict[str, Any]) -> None:
        """Send a response back to the adapter."""
        if self.response_callback:
            self.response_callback(response)


# ==================== Screen Implementations ====================

class BaseGameScreen(Screen):
    """Base class for all game screens with common functionality."""

    def __init__(self, data: Dict[str, Any] = None, *args, **kwargs):
        """Initialize with optional data."""
        super().__init__(*args, **kwargs)
        self.data = data or {}
        self.app = None

    async def on_mount(self) -> None:
        """Handle screen mount."""
        self.app = self.app  # Store reference

    def notify(self, message: str, severity: str = "information") -> None:
        """Show a notification."""
        if self.app:
            self.app.notify(message, severity=severity)


class MainMenuScreen(BaseGameScreen):
    """Main menu screen."""

    def compose(self) -> ComposeResult:
        """Create main menu layout."""
        yield Container(
            Static(TITLE_ART_COMPACT, classes="title-art"),
            Vertical(
                Button("New Game", id="new_game", variant="primary"),
                Button("Continue", id="continue_game"),
                Button("Career Progress", id="career"),
                Button("How to Play", id="help"),
                Button("Settings", id="settings"),
                Button("Quit", id="quit"),
                classes="menu-buttons"
            ),
            Static("© 2025 Virtual Cow Tipper", classes="footer-text"),
            id="main_menu",
            classes="screen-container"
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        button_id = event.button.id

        if button_id == "new_game":
            self.app.push_screen("game")
        elif button_id == "continue_game":
            self.app.push_screen("load_game")
        elif button_id == "career":
            self.app.push_screen("career")
        elif button_id == "help":
            self.app.push_screen("help")
        elif button_id == "settings":
            self.notify("Settings not yet implemented", severity="warning")
        elif button_id == "quit":
            self.app.exit()


class GameScreen(BaseGameScreen):
    """Main game screen with all UI components."""

    def compose(self) -> ComposeResult:
        """Create game screen layout."""
        with Container(classes="game-screen"):
            # Top panel - Stats with icons
            with Horizontal(classes="stats-panel"):
                yield Label(f"{get_status_icon('hp')}HP: {self.app.player_hp}/{self.app.player_max_hp}", id="hp_display")
                yield Label(f"{get_status_icon('cash')}Cash: ${self.app.player_cash}", id="cash_display")
                yield Label(f"{get_status_icon('floor')}Floor: {self.app.current_floor}", id="floor_display")
                yield Label("", id="weapon_display")
                yield Label("", id="shield_display")

            # Main game area
            with Horizontal(classes="game-area"):
                # Left panel - Game view
                with Vertical(classes="game-view"):
                    yield Static(get_cow_art("normal"), id="cow_art", classes="ascii-art cow-art")
                    yield Log(id="combat_log", classes="combat-log")

                # Right panel - Actions/Info
                with Vertical(classes="side-panel"):
                    yield Static("Actions", classes="panel-header")
                    with ScrollableContainer(classes="action-menu"):
                        yield Button("Approach", id="action_approach")
                        yield Button("Rest", id="action_rest")
                        yield Button("Inventory", id="action_inventory")
                        yield Button("Shop", id="action_shop")
                        yield Button("Use Item", id="action_use_item")
                        yield Button("Save & Quit", id="action_save_quit")

                    yield Static("Cow Info", classes="panel-header")
                    yield Label("No cow nearby", id="cow_info", classes="info-text")

    async def on_mount(self) -> None:
        """Initialize game screen."""
        await super().on_mount()
        self.app.game_active = True

        # Watch for reactive changes
        self.watch(self.app, "player_hp", self._update_hp)
        self.watch(self.app, "player_cash", self._update_cash)
        self.watch(self.app, "current_floor", self._update_floor)

        # Start game logic
        await self._start_game()

    def _update_hp(self, hp: int) -> None:
        """Update HP display with animation."""
        label = self.query_one("#hp_display", Label)
        label.update(f"{get_status_icon('hp')}HP: {hp}/{self.app.player_max_hp}")

        # Add animation class for low HP
        if hp < self.app.player_max_hp * 0.3:
            label.add_class("hp-critical")
        else:
            label.remove_class("hp-critical")

    def _update_cash(self, cash: int) -> None:
        """Update cash display."""
        label = self.query_one("#cash_display", Label)
        label.update(f"{get_status_icon('cash')}Cash: ${cash}")

    def _update_floor(self, floor: int) -> None:
        """Update floor display."""
        label = self.query_one("#floor_display", Label)
        label.update(f"{get_status_icon('floor')}Floor: {floor}")
        label.add_class("floor-change")

    def update_cow_art(self, cow_type: str = "normal", mood: str = "neutral") -> None:
        """Update the cow ASCII art display."""
        cow_display = self.query_one("#cow_art", Static)
        art = get_cow_art(cow_type)

        # Add mood indicator
        if mood:
            art += f"\n    Mood: {get_mood_indicator(mood)}"

        cow_display.update(art)

        # Add animation class based on type
        cow_display.remove_class("cow-aggressive", "cow-happy")
        if cow_type == "aggressive":
            cow_display.add_class("cow-aggressive")
        elif cow_type == "happy":
            cow_display.add_class("cow-happy")

    async def _start_game(self) -> None:
        """Initialize and start the game."""
        # TODO: Connect to actual game logic
        self.notify("Game started!", severity="success")
        log = self.query_one("#combat_log", Log)
        log.write_line("Welcome to Virtual Cow Tipper!")
        log.write_line("A wild cow appears...")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle action buttons."""
        button_id = event.button.id

        if button_id == "action_approach":
            self.app.push_screen("combat")
        elif button_id == "action_inventory":
            self.app.push_screen("inventory")
        elif button_id == "action_shop":
            self.app.push_screen("shop")
        elif button_id == "action_rest":
            self._rest()
        elif button_id == "action_save_quit":
            self.app.push_screen("save_prompt")

    def _rest(self) -> None:
        """Handle rest action."""
        old_hp = self.app.player_hp
        self.app.player_hp = min(self.app.player_hp + 5, self.app.player_max_hp)
        healed = self.app.player_hp - old_hp

        log = self.query_one("#combat_log", Log)
        log.write_line(f"You rest and recover {healed} HP.")
        self.notify(f"Recovered {healed} HP", severity="success")


class CombatScreen(BaseGameScreen):
    """Combat screen for cow encounters."""

    def compose(self) -> ComposeResult:
        """Create combat screen layout."""
        with Container(classes="combat-screen"):
            yield Static(COMBAT_BANNER, classes="combat-banner")
            # Combat area
            with Vertical(classes="combat-area"):
                # HP Bars
                with Horizontal(classes="hp-bars"):
                    with Vertical(classes="player-hp"):
                        yield Label("Player", classes="hp-label")
                        yield ProgressBar(total=100, show_eta=False, id="player_hp_bar")
                        yield Label("20/20", id="player_hp_text", classes="hp-text")

                    with Vertical(classes="cow-hp"):
                        yield Label("Cow", classes="hp-label")
                        yield ProgressBar(total=100, show_eta=False, id="cow_hp_bar")
                        yield Label("10/10", id="cow_hp_text", classes="hp-text")

                # Combat log
                yield Log(id="combat_messages", classes="combat-log", auto_scroll=True)

                # Combat actions
                with Horizontal(classes="combat-actions"):
                    yield Button("Attack", id="combat_attack", variant="error")
                    yield Button("Defend", id="combat_defend", variant="warning")
                    yield Button("Item", id="combat_item", variant="success")
                    yield Button("Run", id="combat_run")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle combat actions."""
        log = self.query_one("#combat_messages", Log)

        if event.button.id == "combat_attack":
            log.write_line("You attack the cow!")
            # TODO: Implement combat logic
        elif event.button.id == "combat_defend":
            log.write_line("You brace for impact...")
        elif event.button.id == "combat_run":
            log.write_line("You flee from the cow!")
            self.app.pop_screen()


class ShopScreen(BaseGameScreen):
    """Shop interface screen."""

    def compose(self) -> ComposeResult:
        """Create shop layout."""
        with Container(classes="shop-screen"):
            yield Static(SHOP_BANNER, classes="shop-banner")
            yield Label(f"Your cash: ${self.app.player_cash}", id="shop_cash", classes="cash-display")

            with ScrollableContainer(classes="shop-items"):
                # TODO: Generate from actual shop items
                yield Button("Health Potion - $10", id="item_health_potion")
                yield Button("Rusty Sword - $50", id="item_rusty_sword")
                yield Button("Wooden Shield - $40", id="item_wooden_shield")
                yield Button("Cow Bell - $25", id="item_cow_bell")

            yield Button("Exit Shop", id="exit_shop", variant="warning")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle shop purchases."""
        if event.button.id == "exit_shop":
            self.app.pop_screen()
        elif event.button.id.startswith("item_"):
            self.notify("Purchase functionality coming soon!", severity="warning")


class InventoryScreen(BaseGameScreen):
    """Inventory management screen."""

    def compose(self) -> ComposeResult:
        """Create inventory layout."""
        with Container(classes="inventory-screen"):
            yield Static("=== INVENTORY ===", classes="screen-title")

            with Horizontal(classes="inventory-layout"):
                # Equipped items
                with Vertical(classes="equipped-panel"):
                    yield Static("EQUIPPED", classes="panel-header")
                    yield Label("Weapon: None", id="equipped_weapon")
                    yield Label("Shield: None", id="equipped_shield")

                # Item list
                with Vertical(classes="items-panel"):
                    yield Static("ITEMS", classes="panel-header")
                    with ScrollableContainer(id="item_list"):
                        yield Label("(empty)")

            yield Button("Back", id="back", variant="primary")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle inventory actions."""
        if event.button.id == "back":
            self.app.pop_screen()


class PauseScreen(BaseGameScreen):
    """Pause menu screen."""

    DEFAULT_CSS = """
    PauseScreen {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        """Create pause menu."""
        with Container(classes="pause-menu"):
            yield Static("GAME PAUSED", classes="pause-title")
            yield Button("Resume", id="resume", variant="success")
            yield Button("Save Game", id="save")
            yield Button("Settings", id="settings")
            yield Button("Main Menu", id="main_menu", variant="warning")
            yield Button("Quit", id="quit", variant="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle pause menu options."""
        if event.button.id == "resume":
            self.app.pop_screen()
        elif event.button.id == "save":
            self.app.push_screen("save_game")
        elif event.button.id == "main_menu":
            self.app.game_active = False
            # Clear screen stack and go to main menu
            while len(self.app.navigation_stack) > 1:
                self.app.pop_screen()
        elif event.button.id == "quit":
            self.app.exit()


class HelpScreen(BaseGameScreen):
    """Help/tutorial screen."""

    def compose(self) -> ComposeResult:
        """Create help screen."""
        with ScrollableContainer(classes="help-screen"):
            yield Static("""
# HOW TO PLAY VIRTUAL COW TIPPER

## Objective
Navigate through floors of aggressive cows, collecting loot and growing stronger!

## Controls
- **Arrow Keys/Enter**: Navigate menus
- **ESC**: Go back / Pause
- **F1**: Help
- **F2**: Save Game
- **F3**: Load Game
- **Ctrl+Q**: Quit

## Gameplay
1. **Encounters**: Each floor has cows to face
2. **Combat**: Choose to attack, defend, use items, or flee
3. **Loot**: Defeated cows drop items and cash
4. **Shop**: Buy equipment between floors
5. **Progress**: Reach higher floors for better rewards

## Tips
- Rest to recover HP when low on health
- Save your game frequently
- Experiment with different items
- Some cows have special dialogue options

Good luck, cow tipper!
            """, classes="help-content")
            yield Button("Back", id="back", variant="primary")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle back button."""
        if event.button.id == "back":
            self.app.pop_screen()


class CareerScreen(BaseGameScreen):
    """Career progress screen."""

    def compose(self) -> ComposeResult:
        """Create career screen."""
        # TODO: Load actual career stats
        with Container(classes="career-screen"):
            yield Static("=== CAREER PROGRESS ===", classes="screen-title")

            with ScrollableContainer():
                yield Label("Total Runs: 0")
                yield Label("Best Score: 0")
                yield Label("Total Cows Defeated: 0")
                yield Label("Total Cash Earned: $0")
                yield Label("Highest Floor: 0")
                yield Static("\n=== UNLOCKS ===", classes="section-header")
                yield Label("No unlocks yet")

            yield Button("Back", id="back", variant="primary")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle back button."""
        if event.button.id == "back":
            self.app.pop_screen()


class DialogueScreen(BaseGameScreen):
    """Dialogue interaction screen - fully modal overlay."""

    DEFAULT_CSS = """
    DialogueScreen {
        /* Full screen coverage */
        width: 100%;
        height: 100%;
        background: black 90%;
        layer: overlay;
        align: center middle;
        overflow: hidden;
    }
    """

    def compose(self) -> ComposeResult:
        """Create dialogue screen with opaque background."""
        speaker = self.data.get('speaker', 'Unknown')
        text = self.data.get('text', '...')
        choices = self.data.get('choices', [])

        # Full-screen wrapper with opaque black background
        with Container(classes="dialogue-screen-wrapper"):
            # Inner dialogue box with content
            with Container(classes="dialogue-screen"):
                # Speaker name
                if speaker and speaker != "System":
                    yield Static(f"╔═══ {speaker} ═══╗", classes="dialogue-speaker")

                # Dialogue text
                yield Static(text, classes="dialogue-text")

                # Choices or continue button
                if choices:
                    with Vertical(classes="dialogue-choices"):
                        for i, choice in enumerate(choices):
                            # Don't add numbers if the choice already has them
                            choice_text = choice if choice[0].isdigit() else f"{i+1}. {choice}"
                            yield Button(choice_text, id=f"choice_{i}", variant="primary")
                else:
                    yield Button("[ Continue ]", id="continue", variant="success")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle dialogue choices."""
        if event.button.id == "continue":
            self.app.pop_screen()
        elif event.button.id.startswith("choice_"):
            choice_idx = int(event.button.id.split("_")[1])
            # Send choice back to game logic
            self.app.send_response({'action': 'choice', 'index': choice_idx})
            self.app.pop_screen()


class SaveGameScreen(BaseGameScreen):
    """Save game screen."""

    def compose(self) -> ComposeResult:
        """Create save screen."""
        with Container(classes="save-screen"):
            yield Static("Save Game", classes="screen-title")
            yield Label("Saving...", id="save_status")
            yield Button("Back", id="back", variant="primary")

    async def on_mount(self) -> None:
        """Handle save on mount."""
        await super().on_mount()
        # TODO: Implement actual save
        await asyncio.sleep(1)  # Simulate save
        status = self.query_one("#save_status", Label)
        status.update("Game saved successfully!")
        self.notify("Game saved!", severity="success")


class LoadGameScreen(BaseGameScreen):
    """Load game screen."""

    def compose(self) -> ComposeResult:
        """Create load screen."""
        with Container(classes="load-screen"):
            yield Static("Load Game", classes="screen-title")
            # TODO: Show actual save files
            yield Label("No save files found", id="save_list")
            yield Button("Back", id="back", variant="primary")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle load actions."""
        if event.button.id == "back":
            self.app.pop_screen()


class SavePromptScreen(BaseGameScreen):
    """Save prompt before quitting."""

    def compose(self) -> ComposeResult:
        """Create save prompt."""
        with Container(classes="save-prompt"):
            yield Static("Save before quitting?", classes="prompt-title")
            yield Button("Save & Quit", id="save_quit", variant="success")
            yield Button("Quit without saving", id="quit", variant="error")
            yield Button("Cancel", id="cancel")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle save prompt choices."""
        if event.button.id == "save_quit":
            # TODO: Save game
            self.app.exit()
        elif event.button.id == "quit":
            self.app.exit()
        elif event.button.id == "cancel":
            self.app.pop_screen()


class GameOverScreen(BaseGameScreen):
    """Game over screen."""

    def compose(self) -> ComposeResult:
        """Create game over screen."""
        with Container(classes="game-over"):
            yield Static(GAME_OVER_ART, classes="game-over-title")
            yield Label(self.data.get('message', 'You have been defeated!'))
            yield Label(f"Score: {self.data.get('score', 0)}")
            yield Button("Main Menu", id="main_menu", variant="primary")
            yield Button("Quit", id="quit", variant="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle game over options."""
        if event.button.id == "main_menu":
            self.app.game_active = False
            while len(self.app.navigation_stack) > 1:
                self.app.pop_screen()
        elif event.button.id == "quit":
            self.app.exit()


class VictoryScreen(BaseGameScreen):
    """Victory screen."""

    def compose(self) -> ComposeResult:
        """Create victory screen."""
        with Container(classes="victory"):
            yield Static(VICTORY_ART, classes="victory-title")
            yield Label(self.data.get('message', 'You have triumphed!'))
            yield Label(f"Final Score: {self.data.get('score', 0)}")
            yield Button("Main Menu", id="main_menu", variant="success")
            yield Button("Quit", id="quit")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle victory options."""
        if event.button.id == "main_menu":
            self.app.game_active = False
            while len(self.app.navigation_stack) > 1:
                self.app.pop_screen()
        elif event.button.id == "quit":
            self.app.exit()


# ==================== App Runner ====================

def run_app():
    """Run the Textual application."""
    app = VirtualCowTipperApp()
    app.run()


if __name__ == "__main__":
    run_app()