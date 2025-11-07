# UI Migration Tasks: Curses → Textual [QA-Approved]

## Executive Summary
Systematic migration of Virtual Cow Tipper from curses (manual coordinate system) to Textual (reactive component framework). Total estimated effort: 160-200 hours.

## Critical Path Dependencies
```
Task 1 → Task 2 → Task 3 → Task 4 → Task 5
                     ↓
                   Task 6 → Task 12 → Task 18
                     ↓         ↓
                   Task 7 → Task 13 → Task 19
```

## Pre-Migration Requirements

### Task 0: Pre-Flight Checklist
**Time Estimate:** 2 hours
**Dependencies:** None
**Risk Level:** Low

- [ ] Verify Python version >= 3.8
- [ ] Create feature branch: `git checkout -b feature/textual-ui`
- [ ] Backup current working state: `git stash save "pre-migration-backup"`
- [ ] Document current terminal requirements (min size, color support)
- [ ] Run full test suite and save baseline: `python run_tests.py > tests_baseline.txt`
- [ ] Profile current performance:
  ```python
  import cProfile
  cProfile.run('game.start()', 'curses_profile.stats')
  ```
- [ ] Take screenshots of all current screens for comparison
- [ ] Create `migration_log.md` to track progress and issues

**Rollback:** `git checkout main`

### Task 1: Install and Validate Textual Environment
**Time Estimate:** 3 hours
**Dependencies:** Task 0
**Risk Level:** Low

#### 1.1 Installation
```bash
# Create virtual environment for isolation
python -m venv venv_textual
source venv_textual/bin/activate  # or `venv_textual\Scripts\activate` on Windows

# Install with exact versions for reproducibility
pip install textual==0.41.0 textual-dev==1.2.0
pip freeze > requirements_textual.txt
```

#### 1.2 Validation Steps
- [ ] Run Textual demo: `python -m textual`
- [ ] Test async compatibility: Create `test_async.py`:
  ```python
  from textual.app import App
  import asyncio

  class TestApp(App):
      async def on_mount(self):
          await asyncio.sleep(1)
          self.exit("Async works!")

  if __name__ == "__main__":
      app = TestApp()
      result = app.run()
      print(f"Result: {result}")
  ```
- [ ] Test on target terminals:
  - [ ] Windows Terminal
  - [ ] macOS Terminal.app
  - [ ] iTerm2
  - [ ] Linux gnome-terminal
  - [ ] VS Code integrated terminal
- [ ] Verify mouse support in each terminal
- [ ] Document any terminal-specific issues

**Success Criteria:** Demo runs, async test passes, all terminals support basic Textual features

**Rollback:** `rm -rf venv_textual && git clean -fd`

### Task 2: Architecture Documentation and Planning
**Time Estimate:** 5 hours
**Dependencies:** Task 1
**Risk Level:** Low

#### 2.1 Create Component Hierarchy Document
**File:** `docs/ui_architecture.md`

```markdown
# UI Component Hierarchy

## Screen Tree
```
CowTipperApp
├── MainMenuScreen
│   ├── TitleWidget (ASCII art)
│   ├── MenuListWidget
│   └── VersionFooter
├── GameScreen
│   ├── StatsHeaderWidget
│   │   ├── PlayerStatsWidget
│   │   └── CowStatsWidget
│   ├── GameViewport
│   │   ├── CombatWidget
│   │   ├── DialogueWidget
│   │   ├── ShopWidget
│   │   └── EventWidget
│   └── ActionBarWidget
├── PauseScreen (Modal)
├── SettingsScreen
├── CareerScreen
└── HelpScreen
```
```

#### 2.2 Map Current Functions to New Components
- [ ] Create mapping table:
  ```
  Current Function          → New Component
  game_terminal.draw_menu() → MenuListWidget.render()
  game_terminal.get_key()   → App.on_key()
  player.display_info()     → PlayerStatsWidget.update()
  ```
- [ ] Identify all curses-specific code (search for `curses.`, `stdscr`, `getch`)
- [ ] List all coordinate-based positioning (search for hardcoded x,y values)
- [ ] Document all game state that needs UI updates

#### 2.3 Design State Management Strategy
- [ ] Define UI state vs game state boundaries
- [ ] Create state flow diagram
- [ ] Design event system for game→UI communication
- [ ] Plan reactive bindings (which data triggers which updates)

**Deliverables:**
- `docs/ui_architecture.md`
- `docs/component_mapping.csv`
- `docs/state_flow_diagram.png`

**Success Criteria:** Complete mapping of all UI operations, clear component boundaries

## Phase 1: Foundation Layer

### Task 3: Create UI Abstraction Interface
**Time Estimate:** 8 hours
**Dependencies:** Task 2
**Risk Level:** Medium

#### 3.1 Define Core Interface
**File:** `ui/interfaces/base_ui.py`

```python
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

class UIMode(Enum):
    CURSES = "curses"
    TEXTUAL = "textual"

@dataclass
class MenuChoice:
    index: int
    label: str
    value: Any

class BaseUI(ABC):
    """Abstract base class for UI implementations"""

    @abstractmethod
    async def initialize(self) -> None:
        """Setup UI system"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Cleanup UI system"""
        pass

    # Display Methods
    @abstractmethod
    async def show_text(self, text: str, style: Optional[str] = None,
                       duration: Optional[float] = None) -> None:
        """Display text with optional styling and auto-dismiss"""
        pass

    @abstractmethod
    async def show_menu(self, items: List[str], title: Optional[str] = None,
                       allow_cancel: bool = True) -> Optional[MenuChoice]:
        """Display menu and return selection"""
        pass

    @abstractmethod
    async def get_input(self, prompt: str, validator: Optional[Callable] = None,
                       default: Optional[str] = None) -> str:
        """Get text input from user with validation"""
        pass

    # Game-Specific Displays
    @abstractmethod
    async def update_stats(self, player_stats: Dict, cow_stats: Optional[Dict] = None) -> None:
        """Update status displays"""
        pass

    @abstractmethod
    async def show_combat(self, player_hp: tuple, cow_hp: tuple,
                         combat_log: List[str]) -> None:
        """Display combat state (hp is (current, max))"""
        pass

    @abstractmethod
    async def show_dialogue(self, speaker: str, text: str,
                           choices: Optional[List[str]] = None) -> Optional[int]:
        """Display dialogue with optional choices"""
        pass

    @abstractmethod
    async def show_inventory(self, items: List[Dict], equipped: Dict) -> None:
        """Display inventory screen"""
        pass

    # Event Handlers
    @abstractmethod
    async def on_pause(self) -> bool:
        """Handle pause request, return True to resume"""
        pass

    @abstractmethod
    async def show_error(self, message: str, fatal: bool = False) -> None:
        """Display error message"""
        pass
```

#### 3.2 Create Factory and Registry
**File:** `ui/ui_factory.py`

```python
from typing import Dict, Type
from .interfaces.base_ui import BaseUI, UIMode

class UIFactory:
    _registry: Dict[UIMode, Type[BaseUI]] = {}
    _current_ui: Optional[BaseUI] = None

    @classmethod
    def register(cls, mode: UIMode, ui_class: Type[BaseUI]) -> None:
        cls._registry[mode] = ui_class

    @classmethod
    def create(cls, mode: UIMode, **kwargs) -> BaseUI:
        if mode not in cls._registry:
            raise ValueError(f"UI mode {mode} not registered")

        ui_class = cls._registry[mode]
        cls._current_ui = ui_class(**kwargs)
        return cls._current_ui

    @classmethod
    def get_current(cls) -> Optional[BaseUI]:
        return cls._current_ui
```

#### 3.3 Implement Curses Adapter (Preserve Current Functionality)
**File:** `ui/adapters/curses_adapter.py`

- [ ] Wrap existing GameTerminal class
- [ ] Implement all BaseUI methods using current curses code
- [ ] Add async compatibility layer (use `asyncio.create_task`)
- [ ] Test that game still works identically with adapter

**Testing:**
```python
# test_ui_adapter.py
async def test_curses_adapter_preserves_functionality():
    ui = UIFactory.create(UIMode.CURSES)
    await ui.initialize()

    # Test each method matches current behavior
    result = await ui.show_menu(["Attack", "Defend", "Run"])
    assert result is not None

    await ui.shutdown()
```

**Success Criteria:** Game runs identically through adapter interface

**Rollback:** Remove ui/ directory, revert game.py changes

### Task 4: Create Textual Application Shell
**Time Estimate:** 6 hours
**Dependencies:** Task 3
**Risk Level:** Medium

#### 4.1 Basic Application Structure
**File:** `ui/textual_app.py`

```python
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual import events
from typing import Dict, Any
import asyncio

class CowTipperApp(App):
    """Main Textual application for Virtual Cow Tipper"""

    CSS_PATH = "ui/styles/main.css"
    TITLE = "Virtual Cow Tipper"

    BINDINGS = [
        Binding("escape", "pause", "Pause", priority=True),
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("f1", "help", "Help"),
        Binding("f5", "quicksave", "Quick Save"),
        Binding("f9", "quickload", "Quick Load"),
    ]

    def __init__(self, game_instance=None):
        super().__init__()
        self.game = game_instance
        self.screens: Dict[str, Screen] = {}
        self.game_task: Optional[asyncio.Task] = None

    async def on_mount(self) -> None:
        """Initialize app and load first screen"""
        # Register screens
        from .screens import MainMenuScreen, GameScreen
        self.screens['main_menu'] = MainMenuScreen()
        self.screens['game'] = GameScreen()

        # Start with main menu
        await self.push_screen('main_menu')

    async def action_pause(self) -> None:
        """Handle pause action"""
        if self.game and self.game.running:
            await self.push_screen('pause')

    async def run_game_loop(self) -> None:
        """Run game logic in background"""
        while self.game and self.game.running:
            # Let game process one frame
            await self.game.process_frame()

            # Update UI based on game state
            await self.update_display()

            # Yield control to UI
            await asyncio.sleep(0.016)  # ~60 FPS

    async def update_display(self) -> None:
        """Sync game state to UI"""
        if current_screen := self.screen:
            if hasattr(current_screen, 'update_from_game'):
                await current_screen.update_from_game(self.game)
```

#### 4.2 Create CSS Foundation
**File:** `ui/styles/main.css`

```css
/* Base Theme Variables */
Screen {
    background: $background;
    color: $text;
}

/* Terminal Aesthetic */
$background: #0c0c0c;
$surface: #1a1a1a;
$primary: #00ff00;
$text: #e0e0e0;
$error: #ff3333;
$warning: #ffaa00;
$success: #00ff00;

/* Layout Helpers */
.centered {
    align: center middle;
}

.full-width {
    width: 100%;
}

.padded {
    padding: 1 2;
}

/* Game-Specific Styles */
.hp-bar-full {
    color: $success;
}

.hp-bar-empty {
    color: $surface;
}

.combat-damage {
    color: $error;
    text-style: bold;
}
```

#### 4.3 Implement Error Boundary
**File:** `ui/error_handler.py`

```python
from textual.widgets import Static
from textual.containers import Container
import traceback

class ErrorBoundary:
    @staticmethod
    async def safe_execute(func, *args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Log error
            with open('ui_errors.log', 'a') as f:
                f.write(f"{datetime.now()}: {traceback.format_exc()}\n")

            # Show user-friendly error
            return ErrorWidget(str(e))
```

**Testing Checklist:**
- [ ] App launches without error
- [ ] CSS loads correctly
- [ ] Keybindings respond
- [ ] Error handling works
- [ ] Can switch between screens

**Success Criteria:** Empty Textual app runs with proper structure

### Task 5: Implement Screen Navigation System
**Time Estimate:** 5 hours
**Dependencies:** Task 4
**Risk Level:** Medium

#### 5.1 Create Screen Manager
**File:** `ui/screen_manager.py`

```python
from typing import Dict, Optional, Any
from textual.screen import Screen
import asyncio

class ScreenManager:
    def __init__(self, app):
        self.app = app
        self.screen_stack: List[str] = []
        self.screen_data: Dict[str, Any] = {}

    async def push_screen(self, screen_name: str, data: Optional[Dict] = None) -> None:
        """Push new screen onto stack"""
        # Store data for screen
        if data:
            self.screen_data[screen_name] = data

        # Track navigation
        self.screen_stack.append(screen_name)

        # Actually push screen
        screen = self.app.screens.get(screen_name)
        if not screen:
            raise ValueError(f"Screen {screen_name} not registered")

        await self.app.push_screen(screen)

    async def pop_screen(self) -> None:
        """Return to previous screen"""
        if len(self.screen_stack) > 1:
            leaving = self.screen_stack.pop()
            # Clean up screen data
            self.screen_data.pop(leaving, None)
            await self.app.pop_screen()

    async def replace_screen(self, screen_name: str, data: Optional[Dict] = None) -> None:
        """Replace current screen"""
        await self.pop_screen()
        await self.push_screen(screen_name, data)

    def get_screen_data(self, screen_name: str) -> Optional[Dict]:
        """Get data passed to screen"""
        return self.screen_data.get(screen_name)
```

#### 5.2 Create Screen Transition Effects
**File:** `ui/transitions.py`

```python
class ScreenTransitions:
    @staticmethod
    async def fade_out(widget, duration=0.3):
        # Implement fade effect
        pass

    @staticmethod
    async def slide_in(widget, direction='right', duration=0.3):
        # Implement slide effect
        pass
```

**Testing:**
- [ ] Navigate between 3 screens successfully
- [ ] Data passes between screens
- [ ] Back navigation works
- [ ] No memory leaks on repeated navigation

**Success Criteria:** Smooth screen navigation with data passing

## Phase 2: Core Screen Implementation

### Task 6: Create Main Menu Screen [DETAILED BREAKDOWN]
**Time Estimate:** 8 hours
**Dependencies:** Task 5
**Risk Level:** Low

#### 6.1 Create Menu Screen Layout
**File:** `ui/screens/main_menu_screen.py`

```python
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Header, Footer
from textual.containers import Vertical, Horizontal, Container
from textual.reactive import reactive
from typing import Optional

class MainMenuScreen(Screen):
    """Main menu screen with ASCII art and options"""

    DEFAULT_CSS = """
    MainMenuScreen {
        align: center middle;
    }

    #menu-container {
        width: 60;
        height: 30;
        border: solid $primary;
    }

    #ascii-art {
        height: 10;
        content-align: center middle;
        color: $primary;
    }

    .menu-button {
        width: 100%;
        margin: 1 4;
    }

    .menu-button:hover {
        background: $primary;
        color: $background;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="menu-container"):
            yield Static(self.get_ascii_art(), id="ascii-art")
            with Vertical(id="menu-options"):
                yield Button("New Game", id="new-game", classes="menu-button")
                yield Button("Continue", id="continue", classes="menu-button")
                yield Button("Career Progress", id="career", classes="menu-button")
                yield Button("How to Play", id="help", classes="menu-button")
                yield Button("Settings", id="settings", classes="menu-button")
                yield Button("Quit", id="quit", classes="menu-button")

    def get_ascii_art(self) -> str:
        return """
    ╔════════════════════════════════════════╗
    ║      VIRTUAL COW TIPPER v2.0          ║
    ║                                        ║
    ║              (__)                      ║
    ║              (oo)                      ║
    ║        /------\/                       ║
    ║       / |    ||                        ║
    ║      *  /\---/\                        ║
    ║         ~~   ~~                        ║
    ╚════════════════════════════════════════╝
        """

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "new-game":
            await self.start_new_game()
        elif button_id == "continue":
            await self.continue_game()
        elif button_id == "career":
            await self.show_career()
        elif button_id == "help":
            await self.show_help()
        elif button_id == "settings":
            await self.show_settings()
        elif button_id == "quit":
            self.app.exit()

    async def start_new_game(self) -> None:
        # Check for existing save
        from save_manager import SaveManager
        if SaveManager.save_exists():
            result = await self.app.push_screen("confirm_dialog", {
                "message": "Starting new game will overwrite save. Continue?",
                "options": ["Yes", "No"]
            })
            if result != "Yes":
                return

        # Get player name
        name = await self.app.push_screen("text_input", {
            "prompt": "Enter your name:",
            "default": "Cowboy"
        })

        # Start game
        await self.app.start_game(name)
```

#### 6.2 Add Keyboard Navigation
- [ ] Implement arrow key navigation
- [ ] Number key shortcuts (1-6 for menu items)
- [ ] Enter to select
- [ ] Tab cycling
- [ ] Vim keys (j/k) support

#### 6.3 Add Mouse Support
- [ ] Hover effects
- [ ] Click handling
- [ ] Tooltip on hover

#### 6.4 Add Sound Effects (Optional)
- [ ] Menu navigation sound
- [ ] Selection sound
- [ ] Background music

**Testing:**
- [ ] All menu options trigger correct actions
- [ ] Keyboard navigation works
- [ ] Mouse interaction works
- [ ] ASCII art displays correctly
- [ ] Responsive to window size

**Success Criteria:** Fully functional main menu matching current functionality

### Task 7: Create Game Screen Components [DETAILED BREAKDOWN]
**Time Estimate:** 12 hours
**Dependencies:** Task 6
**Risk Level:** High

#### 7.1 Create Stats Header Widget
**File:** `ui/widgets/stats_header.py`

```python
from textual.widget import Widget
from textual.reactive import reactive
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table

class StatsHeader(Widget):
    """Display player and cow stats in header"""

    player_hp = reactive((20, 20))
    player_cash = reactive(50)
    player_weapon = reactive("Fists")
    player_shield = reactive("None")
    current_floor = reactive(1)

    cow_name = reactive("")
    cow_hp = reactive((0, 0))
    cow_type = reactive("")
    cow_mood = reactive("")

    def render(self) -> RenderableType:
        # Create two-column layout
        table = Table(show_header=False, show_edge=False, expand=True)
        table.add_column("Player", width=40)
        table.add_column("Cow", width=40)

        # Player stats
        player_text = f"""HP: {self.render_hp_bar(self.player_hp)}
Cash: ${self.player_cash}
Weapon: {self.player_weapon}
Shield: {self.player_shield}
Floor: {self.current_floor}"""

        # Cow stats
        if self.cow_name:
            cow_text = f"""Name: {self.cow_name}
HP: {self.render_hp_bar(self.cow_hp)}
Type: {self.cow_type}
Mood: {self.cow_mood}"""
        else:
            cow_text = "No cow present"

        table.add_row(player_text, cow_text)
        return Panel(table, title="Game Status", border_style="green")

    def render_hp_bar(self, hp_tuple: tuple) -> str:
        current, max_hp = hp_tuple
        if max_hp == 0:
            return "N/A"

        filled = int((current / max_hp) * 10)
        empty = 10 - filled

        bar = "█" * filled + "░" * empty
        color = "green" if filled > 5 else "yellow" if filled > 2 else "red"

        return f"[{color}]{bar}[/] {current}/{max_hp}"
```

#### 7.2 Create Combat Display Widget
**File:** `ui/widgets/combat_display.py`

```python
from textual.widgets import Static
from textual.containers import Vertical
from textual.reactive import reactive
from collections import deque

class CombatDisplay(Static):
    """Display combat with HP bars and combat log"""

    DEFAULT_CSS = """
    CombatDisplay {
        height: 100%;
        padding: 1;
    }

    .hp-bar {
        height: 3;
        border: solid $primary;
        margin: 1;
    }

    .combat-log {
        height: 10;
        border: solid $surface;
        overflow-y: scroll;
    }

    .damage-text {
        color: $error;
        text-style: bold;
    }

    .heal-text {
        color: $success;
    }
    """

    combat_log = reactive(deque(maxlen=20))

    def __init__(self):
        super().__init__()
        self.player_hp = (100, 100)
        self.cow_hp = (50, 50)

    def compose(self) -> ComposeResult:
        yield Static(id="player-hp", classes="hp-bar")
        yield Static(id="cow-hp", classes="hp-bar")
        yield Static(id="combat-log", classes="combat-log")

    def add_combat_message(self, message: str, msg_type: str = "normal") -> None:
        """Add message to combat log"""
        styled_msg = self.style_message(message, msg_type)
        self.combat_log.append(styled_msg)
        self.refresh()

    def style_message(self, message: str, msg_type: str) -> str:
        if msg_type == "damage":
            return f"[red bold]{message}[/]"
        elif msg_type == "heal":
            return f"[green]{message}[/]"
        elif msg_type == "critical":
            return f"[yellow bold]⚡ {message} ⚡[/]"
        else:
            return message

    async def animate_damage(self, target: str, amount: int) -> None:
        """Show damage animation"""
        # Flash effect
        widget = self.query_one(f"#{target}-hp")
        original_style = widget.styles.background
        widget.styles.background = "red"
        await asyncio.sleep(0.1)
        widget.styles.background = original_style

        # Floating damage number
        self.add_combat_message(f"-{amount}", "damage")

    async def animate_attack(self, attacker: str, attack_name: str) -> None:
        """Show attack animation"""
        # Screen shake for powerful attacks
        if "critical" in attack_name.lower():
            await self.screen_shake()

        self.add_combat_message(f"{attacker} uses {attack_name}!", "normal")
```

#### 7.3 Create Dialogue Widget
**File:** `ui/widgets/dialogue_widget.py`

```python
from textual.widgets import Static
from textual.timer import Timer
from typing import Optional, List

class DialogueWidget(Static):
    """Display dialogue with typewriter effect"""

    DEFAULT_CSS = """
    DialogueWidget {
        height: 8;
        border: double $primary;
        padding: 1;
    }

    .speaker-name {
        color: $primary;
        text-style: bold;
    }

    .dialogue-text {
        margin-top: 1;
    }

    .choice-prompt {
        margin-top: 1;
        color: $warning;
    }
    """

    def __init__(self):
        super().__init__()
        self.current_text = ""
        self.target_text = ""
        self.typewriter_timer: Optional[Timer] = None
        self.typewriter_speed = 0.03  # seconds per character

    async def show_dialogue(self, speaker: str, text: str,
                           instant: bool = False) -> None:
        """Display dialogue with optional typewriter effect"""
        self.update(f"[bold green]{speaker}:[/]\n")

        if instant:
            self.update(f"[bold green]{speaker}:[/]\n{text}")
        else:
            await self.typewriter_effect(text)

    async def typewriter_effect(self, text: str) -> None:
        """Animate text appearing one character at a time"""
        self.target_text = text
        self.current_text = ""

        for char in text:
            self.current_text += char
            self.update(f"[bold green]{self.speaker}:[/]\n{self.current_text}")
            await asyncio.sleep(self.typewriter_speed)

    async def show_choices(self, choices: List[str]) -> int:
        """Display dialogue choices and get selection"""
        choice_text = "\n".join([f"{i+1}. {choice}"
                                for i, choice in enumerate(choices)])

        self.update(self.current_text + f"\n\n[yellow]{choice_text}[/]")

        # Wait for number key
        choice = await self.get_choice_input(len(choices))
        return choice
```

#### 7.4 Create Action Menu Widget
**File:** `ui/widgets/action_menu.py`

```python
from textual.widgets import Static
from textual.binding import Binding
from typing import List, Callable, Optional

class ActionMenu(Static):
    """Bottom action bar with dynamic options"""

    DEFAULT_CSS = """
    ActionMenu {
        dock: bottom;
        height: 4;
        background: $surface;
        border-top: solid $primary;
    }

    .action-item {
        padding: 0 2;
        margin: 0 1;
    }

    .action-item:hover {
        background: $primary;
        color: $background;
    }

    .keybind {
        color: $warning;
        text-style: bold;
    }
    """

    def __init__(self):
        super().__init__()
        self.actions: List[tuple[str, str, Callable]] = []

    def set_actions(self, actions: List[tuple[str, str, Callable]]) -> None:
        """Set available actions (key, label, callback)"""
        self.actions = actions
        self.refresh()

    def render(self) -> str:
        if not self.actions:
            return "No actions available"

        action_text = "  ".join([
            f"[{key}] {label}" for key, label, _ in self.actions
        ])

        return action_text

    async def handle_key(self, key: str) -> bool:
        """Process key press, return True if handled"""
        for action_key, _, callback in self.actions:
            if key == action_key:
                await callback()
                return True
        return False
```

**Testing Checklist:**
- [ ] Stats update correctly
- [ ] HP bars animate
- [ ] Combat log scrolls
- [ ] Dialogue typewriter works
- [ ] Action menu responds to keys

**Success Criteria:** All game screen components functional and styled

### Task 8: Create Shop Screen [DETAILED BREAKDOWN]
**Time Estimate:** 6 hours
**Dependencies:** Task 7
**Risk Level:** Medium

#### 8.1 Shop Layout Implementation
**File:** `ui/screens/shop_screen.py`

```python
from textual.screen import ModalScreen
from textual.containers import Grid, Vertical, Horizontal
from textual.widgets import Static, Button, DataTable, Label
from textual.reactive import reactive

class ShopScreen(ModalScreen):
    """Shop interface for buying/selling items"""

    DEFAULT_CSS = """
    ShopScreen {
        align: center middle;
    }

    #shop-container {
        width: 70;
        height: 40;
        background: $surface;
        border: double $primary;
    }

    #shop-inventory {
        width: 50%;
        border-right: solid $primary;
    }

    #player-inventory {
        width: 50%;
    }

    .inventory-table {
        height: 100%;
        overflow-y: scroll;
    }

    .item-rare {
        color: #3366ff;
    }

    .item-epic {
        color: #9933ff;
    }

    .item-legendary {
        color: #ff9933;
    }

    #transaction-panel {
        dock: bottom;
        height: 5;
        border-top: solid $primary;
        padding: 1;
    }
    """

    player_cash = reactive(0)
    selected_item = reactive(None)

    def compose(self) -> ComposeResult:
        with Container(id="shop-container"):
            yield Label("🏪 YE OLDE COW SHOPPE 🏪", id="shop-title")

            with Horizontal():
                # Shop inventory
                with Vertical(id="shop-inventory"):
                    yield Label("For Sale")
                    yield DataTable(id="shop-items", classes="inventory-table")

                # Player inventory
                with Vertical(id="player-inventory"):
                    yield Label("Your Items")
                    yield DataTable(id="player-items", classes="inventory-table")

            # Transaction panel
            with Horizontal(id="transaction-panel"):
                yield Static(f"Cash: ${self.player_cash}", id="cash-display")
                yield Button("Buy", id="buy-button", disabled=True)
                yield Button("Sell", id="sell-button", disabled=True)
                yield Button("Exit Shop", id="exit-button")

    def on_mount(self) -> None:
        # Setup shop inventory table
        shop_table = self.query_one("#shop-items", DataTable)
        shop_table.add_columns("Item", "Type", "Price", "Stats")

        # Setup player inventory table
        player_table = self.query_one("#player-items", DataTable)
        player_table.add_columns("Item", "Type", "Value", "Equipped")

        # Load inventories
        self.load_shop_inventory()
        self.load_player_inventory()

    def load_shop_inventory(self) -> None:
        """Populate shop with items"""
        shop_table = self.query_one("#shop-items", DataTable)

        # Get items from game
        items = self.app.game.current_shop_items

        for item in items:
            style = self.get_rarity_style(item.rarity)
            shop_table.add_row(
                item.name,
                item.type,
                f"${item.price}",
                item.get_stats_display(),
                key=item.id
            )

    def get_rarity_style(self, rarity: str) -> str:
        """Get CSS class for item rarity"""
        return f"item-{rarity.lower()}"

    async def on_data_table_row_selected(self, event) -> None:
        """Handle item selection"""
        table_id = event.data_table.id
        row_key = event.row_key

        if table_id == "shop-items":
            # Selected shop item to buy
            self.selected_item = ("buy", row_key)
            self.query_one("#buy-button").disabled = False
            self.query_one("#sell-button").disabled = True

        elif table_id == "player-items":
            # Selected player item to sell
            self.selected_item = ("sell", row_key)
            self.query_one("#sell-button").disabled = False
            self.query_one("#buy-button").disabled = True

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "buy-button":
            await self.buy_item()
        elif button_id == "sell-button":
            await self.sell_item()
        elif button_id == "exit-button":
            self.dismiss()

    async def buy_item(self) -> None:
        """Process item purchase"""
        if not self.selected_item or self.selected_item[0] != "buy":
            return

        item_id = self.selected_item[1]
        item = self.app.game.get_shop_item(item_id)

        if self.player_cash >= item.price:
            # Deduct cash
            self.player_cash -= item.price

            # Add to player inventory
            self.app.game.player.add_item(item)

            # Update displays
            self.refresh_displays()

            # Show success message
            await self.show_transaction_message(f"Bought {item.name}!")
        else:
            await self.show_transaction_message("Not enough cash!", error=True)
```

#### 8.2 Implement Buy/Sell Logic
- [ ] Validate transactions
- [ ] Update inventories
- [ ] Handle equipped items
- [ ] Show transaction animations

#### 8.3 Add Item Comparison
- [ ] Show stat differences
- [ ] Highlight upgrades/downgrades
- [ ] Compare with equipped items

**Testing:**
- [ ] Items display with correct rarity colors
- [ ] Buy/sell transactions work
- [ ] Cash updates correctly
- [ ] Can't buy without funds
- [ ] Can't sell equipped items without confirmation

**Success Criteria:** Fully functional shop matching current game mechanics

## Phase 3: Game Integration

### Task 9: Create Textual UI Adapter [CRITICAL PATH]
**Time Estimate:** 10 hours
**Dependencies:** Tasks 3-8
**Risk Level:** High

#### 9.1 Implement BaseUI for Textual
**File:** `ui/adapters/textual_adapter.py`

```python
from typing import Optional, List, Dict, Any
from ..interfaces.base_ui import BaseUI
from ..textual_app import CowTipperApp
import asyncio

class TextualAdapter(BaseUI):
    """Adapter to run game through Textual UI"""

    def __init__(self):
        self.app: Optional[CowTipperApp] = None
        self.game = None
        self._running = False

    async def initialize(self) -> None:
        """Setup Textual UI system"""
        self.app = CowTipperApp()
        self._running = True

        # Start app in background
        self.app_task = asyncio.create_task(self.app.run_async())

        # Wait for app to be ready
        while not self.app.is_running:
            await asyncio.sleep(0.01)

    async def shutdown(self) -> None:
        """Cleanup Textual UI system"""
        self._running = False
        if self.app:
            self.app.exit()
            await self.app_task

    async def show_text(self, text: str, style: Optional[str] = None,
                       duration: Optional[float] = None) -> None:
        """Display text in current screen"""
        if current_screen := self.app.screen:
            if hasattr(current_screen, 'show_text'):
                await current_screen.show_text(text, style, duration)

    async def show_menu(self, items: List[str], title: Optional[str] = None,
                       allow_cancel: bool = True) -> Optional[MenuChoice]:
        """Display menu and return selection"""
        # Get current screen's menu widget
        if current_screen := self.app.screen:
            if hasattr(current_screen, 'action_menu'):
                result = await current_screen.action_menu.show_menu(
                    items, title, allow_cancel
                )
                return MenuChoice(
                    index=result['index'],
                    label=result['label'],
                    value=result['value']
                )
        return None

    async def update_stats(self, player_stats: Dict,
                          cow_stats: Optional[Dict] = None) -> None:
        """Update status displays"""
        if game_screen := self.app.screens.get('game'):
            stats_header = game_screen.query_one("StatsHeader")

            # Update player stats
            stats_header.player_hp = player_stats['hp']
            stats_header.player_cash = player_stats['cash']
            stats_header.player_weapon = player_stats['weapon']
            stats_header.player_shield = player_stats['shield']
            stats_header.current_floor = player_stats['floor']

            # Update cow stats if present
            if cow_stats:
                stats_header.cow_name = cow_stats['name']
                stats_header.cow_hp = cow_stats['hp']
                stats_header.cow_type = cow_stats['type']
                stats_header.cow_mood = cow_stats['mood']

    async def show_combat(self, player_hp: tuple, cow_hp: tuple,
                         combat_log: List[str]) -> None:
        """Display combat state"""
        if game_screen := self.app.screens.get('game'):
            combat_widget = game_screen.query_one("CombatDisplay")

            # Update HP
            combat_widget.player_hp = player_hp
            combat_widget.cow_hp = cow_hp

            # Add new log entries
            for entry in combat_log:
                combat_widget.add_combat_message(entry)

    # Bridge game events to UI
    async def on_game_event(self, event_type: str, data: Dict) -> None:
        """Handle game events and update UI accordingly"""
        if event_type == "combat_start":
            await self.app.screen_manager.push_screen('game')
            await self.show_combat_start(data)

        elif event_type == "damage_dealt":
            await self.animate_damage(data['target'], data['amount'])

        elif event_type == "item_obtained":
            await self.show_item_notification(data['item'])

        elif event_type == "floor_complete":
            await self.show_floor_transition(data['floor'])
```

#### 9.2 Create Game-to-UI Event Bridge
**File:** `ui/game_bridge.py`

```python
from typing import Dict, Any
import asyncio
from collections import deque

class GameUIBridge:
    """Bridges game logic events to UI updates"""

    def __init__(self, ui_adapter):
        self.ui = ui_adapter
        self.event_queue = deque()
        self.processing = False

    async def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Queue event for UI processing"""
        self.event_queue.append((event_type, data))

        if not self.processing:
            await self.process_events()

    async def process_events(self) -> None:
        """Process queued events"""
        self.processing = True

        while self.event_queue:
            event_type, data = self.event_queue.popleft()
            await self.ui.on_game_event(event_type, data)

            # Small delay between events for visual clarity
            await asyncio.sleep(0.05)

        self.processing = False

    # Convenience methods for common events
    async def combat_started(self, player, cow) -> None:
        await self.emit_event("combat_start", {
            'player': player.to_dict(),
            'cow': cow.to_dict()
        })

    async def damage_dealt(self, attacker: str, target: str,
                          amount: int, attack_type: str) -> None:
        await self.emit_event("damage_dealt", {
            'attacker': attacker,
            'target': target,
            'amount': amount,
            'attack_type': attack_type
        })
```

#### 9.3 Update Game Class
**File:** `game.py` (modifications)

```python
# Add to __init__
def __init__(self, player_name: str, ui_mode: str = "textual", ...):
    # Determine UI mode
    from ui.ui_factory import UIFactory, UIMode

    if ui_mode == "curses":
        self.ui = UIFactory.create(UIMode.CURSES)
    else:
        self.ui = UIFactory.create(UIMode.TEXTUAL)

    # Create event bridge
    from ui.game_bridge import GameUIBridge
    self.ui_bridge = GameUIBridge(self.ui)

    # Initialize UI
    asyncio.run(self.ui.initialize())

# Modify display methods
async def display_stats(self):
    """Update UI with current stats"""
    player_stats = {
        'hp': (self.player.hp, self.player.max_hp),
        'cash': self.player.cash,
        'weapon': self.player.weapon.name if self.player.weapon else "Fists",
        'shield': self.player.shield.name if self.player.shield else "None",
        'floor': self.current_floor
    }

    cow_stats = None
    if self.cow:
        cow_stats = {
            'name': self.cow.name,
            'hp': (self.cow.hp, self.cow.max_hp),
            'type': self.cow.type,
            'mood': self.cow.personality
        }

    await self.ui.update_stats(player_stats, cow_stats)
```

**Testing:**
- [ ] Game runs with Textual UI
- [ ] All game events trigger UI updates
- [ ] No race conditions
- [ ] Memory usage stable
- [ ] Can switch between curses and Textual

**Success Criteria:** Game fully playable with new UI

## Phase 4: Polish and Optimization

### Task 10: Add Visual Polish [ENHANCEMENT]
**Time Estimate:** 8 hours
**Dependencies:** Task 9
**Risk Level:** Low

#### 10.1 Implement Animation System
**File:** `ui/animations.py`

```python
import asyncio
from textual.widgets import Widget
from typing import Callable, Optional

class AnimationController:
    """Manage UI animations"""

    @staticmethod
    async def shake(widget: Widget, intensity: int = 2,
                   duration: float = 0.3) -> None:
        """Screen shake effect"""
        original_offset = widget.styles.offset
        steps = int(duration / 0.05)

        for _ in range(steps):
            import random
            x_offset = random.randint(-intensity, intensity)
            y_offset = random.randint(-intensity, intensity)
            widget.styles.offset = (x_offset, y_offset)
            await asyncio.sleep(0.05)

        widget.styles.offset = original_offset

    @staticmethod
    async def flash(widget: Widget, color: str = "white",
                   duration: float = 0.2) -> None:
        """Flash effect"""
        original_bg = widget.styles.background
        widget.styles.background = color
        await asyncio.sleep(duration)
        widget.styles.background = original_bg

    @staticmethod
    async def fade_in(widget: Widget, duration: float = 0.5) -> None:
        """Fade in effect"""
        widget.styles.opacity = 0
        steps = 20
        for i in range(steps):
            widget.styles.opacity = i / steps
            await asyncio.sleep(duration / steps)

    @staticmethod
    async def typewriter(text_widget: Widget, text: str,
                        speed: float = 0.03) -> None:
        """Typewriter text effect"""
        for i in range(len(text)):
            text_widget.update(text[:i+1])
            await asyncio.sleep(speed)
```

#### 10.2 Add Particle Effects
- [ ] Damage numbers floating up
- [ ] Victory confetti
- [ ] Item pickup sparkle
- [ ] Critical hit lightning

#### 10.3 Sound Integration (Optional)
- [ ] Combat sounds
- [ ] UI interaction sounds
- [ ] Background music
- [ ] Victory/defeat jingles

### Task 11: Performance Optimization [CRITICAL]
**Time Estimate:** 6 hours
**Dependencies:** Task 10
**Risk Level:** Medium

#### 11.1 Profile and Benchmark
```python
# Create benchmark suite
import time
import tracemalloc

class UIBenchmark:
    @staticmethod
    async def measure_render_time():
        start = time.perf_counter()
        # Render complex screen
        end = time.perf_counter()
        return end - start

    @staticmethod
    def measure_memory_usage():
        tracemalloc.start()
        # Perform UI operations
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return current, peak
```

#### 11.2 Optimization Targets
- [ ] Menu navigation < 16ms response time
- [ ] Combat updates < 33ms per frame
- [ ] Memory usage < 100MB
- [ ] No memory leaks after 1 hour play

#### 11.3 Implement Optimizations
- [ ] Widget pooling for frequently created/destroyed widgets
- [ ] Lazy loading for off-screen content
- [ ] Batch UI updates
- [ ] Cache computed styles

**Performance Goals:**
- 60 FPS during combat
- Instant menu response
- Smooth scrolling
- No stuttering

## Phase 5: Testing and Validation

### Task 12: Comprehensive Testing [QUALITY ASSURANCE]
**Time Estimate:** 10 hours
**Dependencies:** Tasks 1-11
**Risk Level:** Low

#### 12.1 Unit Tests for Each Component
**File:** `tests/test_ui_components.py`

```python
import pytest
from textual.pilot import Pilot
from ui.screens.main_menu_screen import MainMenuScreen

@pytest.mark.asyncio
async def test_main_menu_navigation():
    """Test main menu keyboard navigation"""
    async with MainMenuScreen().run_test() as pilot:
        # Test arrow navigation
        await pilot.press("down")
        assert pilot.app.focused.id == "continue"

        # Test number shortcut
        await pilot.press("1")
        assert pilot.app.screen_stack[-1].name == "game"

@pytest.mark.asyncio
async def test_combat_display_updates():
    """Test combat display updates correctly"""
    # Test HP bar updates
    # Test combat log
    # Test animations

# Add tests for each widget and screen
```

#### 12.2 Integration Tests
- [ ] Full game flow test (start → combat → shop → victory)
- [ ] Save/load with new UI
- [ ] Screen navigation flow
- [ ] Event propagation

#### 12.3 Cross-Platform Testing
- [ ] Windows 10/11
- [ ] macOS 12+
- [ ] Ubuntu 22.04
- [ ] Different terminal emulators

#### 12.4 Stress Testing
- [ ] Rapid input handling
- [ ] 1000+ combat log entries
- [ ] Window resizing during gameplay
- [ ] Network lag simulation (if applicable)

### Task 13: Migration Rollback Plan [SAFETY NET]
**Time Estimate:** 4 hours
**Dependencies:** All tasks
**Risk Level:** Low

#### 13.1 Create Feature Flags
**File:** `config.py`

```python
import os

class UIConfig:
    # UI mode selection
    UI_MODE = os.getenv("COW_TIPPER_UI", "textual")  # or "curses"

    # Feature flags
    ENABLE_ANIMATIONS = True
    ENABLE_PARTICLES = True
    ENABLE_SOUND = False

    # Performance settings
    TARGET_FPS = 60
    MAX_COMBAT_LOG_ENTRIES = 100

    # Fallback settings
    FALLBACK_ON_ERROR = True
    FALLBACK_UI = "curses"
```

#### 13.2 Implement Graceful Degradation
```python
class UIManager:
    @staticmethod
    def create_ui(preferred_mode: str = "textual"):
        try:
            if preferred_mode == "textual":
                from ui.adapters.textual_adapter import TextualAdapter
                return TextualAdapter()
        except ImportError:
            print("Textual not available, falling back to curses")

        # Fallback to curses
        from ui.adapters.curses_adapter import CursesAdapter
        return CursesAdapter()
```

#### 13.3 Create Rollback Documentation
- [ ] Document all changes made
- [ ] Create rollback script
- [ ] List dependencies added
- [ ] Archive original code

## Post-Migration Checklist

### Final Validation
- [ ] All original features work
- [ ] Performance meets or exceeds curses version
- [ ] No regression in gameplay
- [ ] Documentation updated
- [ ] README includes new UI information
- [ ] Screenshots/GIFs created
- [ ] Installation guide updated

### Performance Benchmarks
| Metric | Curses | Textual | Target |
|--------|--------|---------|--------|
| Startup time | ? | ? | <2s |
| Menu response | ? | ? | <16ms |
| Combat frame time | ? | ? | <33ms |
| Memory usage | ? | ? | <100MB |
| Save/Load time | ? | ? | <1s |

### Known Issues and Workarounds
Document any issues discovered during migration:
1. Issue: [Description]
   Workaround: [Solution]
   Fix planned: [Yes/No]

### Success Metrics
- [ ] Zero crashes in 10 playthroughs
- [ ] All 28 existing tests pass
- [ ] 90%+ code coverage on new UI code
- [ ] Positive user feedback from beta testers
- [ ] Maintainable and extensible codebase

## Risk Mitigation

### High-Risk Areas
1. **Async Integration**: Game loop wasn't designed for async
   - Mitigation: Careful event queue management
   - Fallback: Synchronous adapter layer

2. **Performance**: Textual overhead might impact gameplay
   - Mitigation: Profile early and often
   - Fallback: Disable animations/effects

3. **Compatibility**: Terminal differences
   - Mitigation: Test on multiple terminals
   - Fallback: Curses mode flag

### Communication Plan
- Daily progress updates in migration_log.md
- Screenshots of each completed screen
- Performance metrics after each phase
- Blockers raised immediately

## Timeline and Resource Estimation

### Development Timeline (160-200 hours)
- **Week 1** (40h): Foundation and architecture (Tasks 0-5)
- **Week 2** (40h): Core screens implementation (Tasks 6-8)
- **Week 3** (40h): Integration and migration (Tasks 9-11)
- **Week 4** (40h): Testing and polish (Tasks 12-13)

### Milestones
- **Milestone 1**: Main menu working in Textual
- **Milestone 2**: Combat fully functional
- **Milestone 3**: Complete game playable
- **Milestone 4**: All tests passing

### Go/No-Go Decision Points
1. After Task 5: Can we navigate screens?
2. After Task 8: Is performance acceptable?
3. After Task 11: Is the game fully playable?
4. After Task 13: Are all tests passing?

## Appendix: Code Templates

### A. Screen Template
```python
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Container

class TemplateScreen(Screen):
    """Template for new screens"""

    DEFAULT_CSS = """
    TemplateScreen {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("Template Screen")

    async def on_mount(self) -> None:
        """Initialize screen"""
        pass

    async def on_unmount(self) -> None:
        """Cleanup screen"""
        pass
```

### B. Widget Template
```python
from textual.widget import Widget
from textual.reactive import reactive

class TemplateWidget(Widget):
    """Template for new widgets"""

    DEFAULT_CSS = """
    TemplateWidget {
        height: auto;
        width: 100%;
    }
    """

    data = reactive({})

    def render(self) -> str:
        return "Template Widget"

    def update_data(self, new_data: dict) -> None:
        self.data = new_data
```

### C. Test Template
```python
import pytest
from textual.pilot import Pilot

@pytest.mark.asyncio
async def test_template():
    """Template for UI tests"""
    from ui.screens.template_screen import TemplateScreen

    async with TemplateScreen().run_test() as pilot:
        # Test assertions
        assert pilot.app.screen is not None
```

---

## Final Notes

This migration plan has been designed to be:
- **Incremental**: Each task builds on the previous
- **Testable**: Every component can be validated independently
- **Reversible**: Rollback possible at any point
- **Measurable**: Clear success criteria for each task

The key to success is maintaining the game's playability throughout the migration. The dual-UI approach ensures players can always fall back to the working curses implementation while the Textual UI is being developed.

Good luck with the migration! 🎮