# UI Architecture: Textual Migration

**Document Version:** 1.0
**Date:** 2025-11-01
**Status:** Architecture Planning (Task 2)

## Overview

This document defines the UI component hierarchy and architecture for migrating Virtual Cow Tipper from curses to Textual framework.

## Current Architecture (Curses)

### Current Screens
```
Application
├── MainMenu (main_menu.py)
│   ├── Title ASCII Art
│   ├── Menu Options (1-5)
│   └── Keyboard Input Handler
│
├── GameTerminal (terminal/game_terminal.py)
│   ├── Player Stats Display (top-left)
│   ├── Cow Stats Display (top-right)
│   ├── Game Title (centered)
│   ├── Separator Line
│   ├── Main Display Area (ASCII art/combat)
│   ├── Dialogue Section (2 lines, word-wrapped)
│   ├── Instructions/Prompts
│   ├── Input Area
│   └── Menu Section (dynamic, 3-4 items)
│
└── PauseMenu (terminal/pause_menu.py)
    ├── Save Game
    ├── Resume
    └── Quit
```

### Current Display Methods
- `draw(y, x, text)` - Manual coordinate positioning
- `draw_menu(items, selected)` - Menu rendering
- `draw_dialog(text)` - Word-wrapped dialogue
- `draw_art()` - ASCII art display
- `get_menu_choice()` - Blocking input with keyboard nav

### Current State Management
- Direct attribute manipulation (`self.player_stats = ...`)
- Full screen refresh on updates
- No reactive bindings
- Synchronous, blocking I/O

## Target Architecture (Textual)

### Component Hierarchy

```
CowTipperApp (Main Application)
│
├── MainMenuScreen
│   ├── TitleWidget (ASCII art)
│   ├── MenuListWidget (button list)
│   ├── SaveStatusWidget (shows if save exists)
│   └── VersionFooter
│
├── GameScreen
│   ├── StatsHeader (compound widget)
│   │   ├── PlayerStatsPanel
│   │   │   ├── HPBar
│   │   │   ├── CashDisplay
│   │   │   ├── WeaponDisplay
│   │   │   ├── ShieldDisplay
│   │   │   └── FloorDisplay
│   │   │
│   │   └── CowStatsPanel
│   │       ├── NameDisplay
│   │       ├── HPBar
│   │       ├── TypeDisplay
│   │       └── MoodDisplay
│   │
│   ├── GameViewport (main content area)
│   │   ├── CombatDisplay
│   │   │   ├── PlayerHPBar (visual)
│   │   │   ├── CowHPBar (visual)
│   │   │   ├── ASCIIArtPanel (optional)
│   │   │   └── CombatLog (scrollable)
│   │   │
│   │   ├── DialogueDisplay
│   │   │   ├── SpeakerLabel
│   │   │   ├── DialogueText (typewriter effect)
│   │   │   └── DialogueChoices (if applicable)
│   │   │
│   │   ├── ShopDisplay
│   │   │   ├── ShopInventoryTable
│   │   │   ├── PlayerInventoryTable
│   │   │   ├── ItemDetailPanel
│   │   │   └── TransactionButtons
│   │   │
│   │   └── EventDisplay
│   │       ├── EventText
│   │       └── EventChoices
│   │
│   └── ActionBar (bottom, docked)
│       ├── ActionButtons (dynamic)
│       └── HelpText
│
├── PauseScreen (Modal overlay)
│   ├── PauseMenu
│   │   ├── Resume Button
│   │   ├── Save Button
│   │   ├── Load Button
│   │   ├── Settings Button
│   │   ├── Help Button
│   │   └── Quit Button
│   └── BlurredBackground
│
├── SettingsScreen
│   ├── DisplaySettings
│   │   ├── TextSpeed Slider
│   │   ├── ColorTheme Selector
│   │   └── ASCIIArt Toggle
│   ├── GameplaySettings
│   │   ├── Difficulty Selector
│   │   └── AutoSave Toggle
│   └── KeyBindings
│       └── KeyMapping List
│
├── CareerScreen
│   ├── CareerStats Display
│   ├── Unlocks List
│   └── Progress Bars
│
├── HelpScreen
│   ├── Tutorial Text
│   ├── Controls Reference
│   └── Tips Section
│
└── DialogScreen (reusable modal)
    ├── Title
    ├── Message
    └── Buttons (OK/Cancel/Custom)
```

### Widget Catalog

#### Core Widgets
1. **HPBar** - Visual health bar with color coding
2. **CombatLog** - Scrollable log with syntax highlighting
3. **DialogueWidget** - Text with typewriter effect
4. **ActionMenu** - Dynamic button list with keybindings
5. **InventoryTable** - Sortable data table with rarity colors
6. **ProgressBar** - Generic progress display

#### Container Widgets
1. **StatsHeader** - Composite stats display
2. **GameViewport** - Switchable content area
3. **ModalOverlay** - Dimmed background for modals

#### Screen Widgets
1. **MainMenuScreen** - Entry point
2. **GameScreen** - Primary gameplay
3. **PauseScreen** - Modal pause menu
4. **SettingsScreen** - Configuration
5. **HelpScreen** - Documentation

## State Management Strategy

### UI State vs Game State

```
┌─────────────────────────────────────────────┐
│           Game State (Pure Logic)            │
│  - Player HP, cash, inventory                │
│  - Cow properties, AI state                  │
│  - Floor number, encounter type              │
│  - Combat calculations                       │
│  - Item effects                              │
└─────────────────────────────────────────────┘
                    ↓
          [Event Bridge/Adapter]
                    ↓
┌─────────────────────────────────────────────┐
│            UI State (Reactive)               │
│  - Currently displayed screen                │
│  - Widget visibility states                  │
│  - Animation states                          │
│  - Selected menu items                       │
│  - Scroll positions                          │
└─────────────────────────────────────────────┘
```

### Event Flow

```
Game Logic          Event Bridge         UI Layer
    │                    │                   │
    ├─ damage_dealt() ───→ emit_event() ────→ animate_damage()
    │                    │                   │
    ├─ player_died() ────→ emit_event() ────→ show_defeat_screen()
    │                    │                   │
    ├─ item_obtained() ──→ emit_event() ────→ show_notification()
    │                    │                   │
    └─ floor_complete() ─→ emit_event() ────→ show_transition()
```

### Reactive Bindings Plan

**Textual Reactive Properties:**
```python
class PlayerStatsPanel(Widget):
    hp = reactive((20, 20))           # Triggers HP bar update
    cash = reactive(50)               # Triggers cash display
    weapon = reactive("Fists")        # Triggers weapon display
    shield = reactive("None")         # Triggers shield display
    floor = reactive(1)               # Triggers floor display

    def watch_hp(self, old, new):
        # Automatically called when hp changes
        self.update_hp_bar(new)

    def watch_cash(self, old, new):
        # Automatically called when cash changes
        self.update_cash_display(new)
```

**Benefits:**
- Automatic UI updates when game state changes
- No manual refresh calls needed
- Clean separation of concerns
- Type-safe state management

## Component Mapping

### Screen Mapping
| Current (Curses) | New (Textual) | Notes |
|-----------------|---------------|--------|
| MainMenu | MainMenuScreen | Add save status, better styling |
| GameTerminal | GameScreen | Split into sub-widgets |
| PauseMenu | PauseScreen | Make modal overlay |
| N/A | SettingsScreen | New feature |
| career_stats (print) | CareerScreen | New dedicated screen |
| help_screen (print) | HelpScreen | New dedicated screen |

### Function Mapping
| Current Function | New Component/Method | Notes |
|-----------------|---------------------|--------|
| `game_terminal.draw()` | `Widget.update()` | Reactive, no coordinates |
| `game_terminal.draw_menu()` | `MenuListWidget.render()` | Automatic layout |
| `game_terminal.get_menu_choice()` | `MenuListWidget.on_key()` | Event-driven |
| `game_terminal.draw_dialog()` | `DialogueWidget.show_dialogue()` | Typewriter effect |
| `game_terminal.draw_player_stats()` | `PlayerStatsPanel.update()` | Reactive binding |
| `game_terminal.draw_cow_stats()` | `CowStatsPanel.update()` | Reactive binding |
| `game_terminal.clear_screen()` | `Screen.refresh()` | Automatic |
| `game_terminal.refresh()` | N/A | Textual handles automatically |
| `get_key_variables()` | `Screen.BINDINGS` | Declarative keybindings |

### Data Flow Mapping
| Current Pattern | New Pattern | Example |
|----------------|-------------|---------|
| `player.display_info()` | `stats_panel.hp = player.hp` | Reactive update |
| `stdscr.getch()` | `async def on_key(event)` | Async event handler |
| `clear() + redraw all` | Widget dirty tracking | Efficient partial updates |
| Manual word wrap | `max-width` CSS | Automatic wrapping |
| Hardcoded coordinates | CSS layout | Responsive positioning |

## Curses-Specific Code Patterns

### Pattern 1: Coordinate-Based Drawing
**Current:**
```python
self.stdscr.addstr(y=5, x=10, "Text")
```
**New:**
```python
# Handled by Textual layout engine via CSS
```

### Pattern 2: Blocking Input
**Current:**
```python
key = self.stdscr.getch()  # Blocks thread
```
**New:**
```python
async def on_key(self, event: Key) -> None:
    # Non-blocking event handler
```

### Pattern 3: Manual Refresh
**Current:**
```python
self.stdscr.clear()
# ... draw everything ...
self.stdscr.refresh()
```
**New:**
```python
# Automatic - Textual handles dirty tracking
self.some_widget.update("new text")
```

### Pattern 4: Menu Navigation
**Current:**
```python
selected = 0
while True:
    draw_menu(items, selected)
    key = getch()
    if key == KEY_UP:
        selected = (selected - 1) % len(items)
```
**New:**
```python
# Built-in via OptionList or ListView widgets
# Or declarative bindings:
BINDINGS = [
    Binding("up", "cursor_up", "Up"),
    Binding("down", "cursor_down", "Down"),
]
```

## Coordinate Usage Audit

### Files with Hardcoded Coordinates
1. **terminal/game_terminal.py**
   - `WIDTH = 85`, `HEIGHT = 30` (Lines 7-8)
   - `PLAYER_INFO_Y = 0` (Line 12)
   - `COW_INFO_X = 50` (Line 14)
   - `TITLE_Y = 2` (Line 15)
   - `SEPARATOR_Y = 4` (Line 16)
   - `ART_Y_START = 5`, `ART_Y_END = 19` (Lines 19-20)
   - `DIALOG_Y_START = 20` (Line 22)
   - `MENU_Y_START = 25` (Line 30)

2. **main_menu.py**
   - `start_y = 2` (Line 60)
   - `menu_start_y = start_y + len(title_lines) + 2` (Line 69)
   - Dynamic centering calculations (Lines 58, 75)

3. **terminal/pause_menu.py**
   - Similar coordinate-based positioning

**Migration Strategy:**
- Replace ALL with CSS layout
- Use containers (Vertical, Horizontal, Grid)
- Define heights as `auto`, `fr`, or percentage
- Use alignment properties instead of math

## CSS Layout Strategy

### Grid-Based Layout
```css
GameScreen {
    layout: grid;
    grid-size: 1 3;  /* 1 column, 3 rows */
    grid-rows: auto 1fr auto;  /* header, content, footer */
}

#stats-header {
    height: 5;
    border-bottom: solid $primary;
}

#game-viewport {
    /* Fills remaining space */
    overflow-y: auto;
}

#action-bar {
    dock: bottom;
    height: 3;
    border-top: solid $primary;
}
```

### Responsive Considerations
```css
/* Minimum terminal size */
Screen {
    min-width: 80;
    min-height: 24;
}

/* Adaptive based on terminal size */
@media (max-width: 100) {
    #stats-header {
        layout: vertical;  /* Stack instead of side-by-side */
    }
}
```

## Event System Design

### Game → UI Events
```python
# In game logic:
await self.ui_bridge.emit_event("damage_dealt", {
    'attacker': 'Player',
    'target': 'Cow',
    'amount': 15,
    'attack_type': 'critical'
})

# In UI adapter:
async def on_game_event(self, event_type: str, data: Dict):
    if event_type == "damage_dealt":
        combat_widget = self.screen.query_one(CombatDisplay)
        await combat_widget.animate_damage(
            target=data['target'],
            amount=data['amount']
        )
```

### UI → Game Events
```python
# In UI:
async def on_button_pressed(self, event: Button.Pressed):
    if event.button.id == "attack":
        # Notify game of player action
        await self.app.game.player_attack()
```

## Migration Path

### Phase 1: Foundation
1. Create base UI interface (abstraction)
2. Implement curses adapter (preserve current UI)
3. Create Textual app skeleton

### Phase 2: Core Screens
1. MainMenuScreen (simple, good starting point)
2. GameScreen structure (without game integration)
3. Widgets (HPBar, CombatLog, etc.)

### Phase 3: Integration
1. UI adapter for Textual
2. Event bridge
3. Replace game.py references

### Phase 4: Polish
1. Animations
2. Color themes
3. Responsive design
4. Accessibility

## Testing Strategy

### Component Tests
```python
@pytest.mark.asyncio
async def test_hp_bar_updates():
    widget = HPBar()
    widget.hp = (50, 100)
    assert widget.percentage == 50
    assert widget.color == "yellow"  # Health below 50%
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_combat_flow():
    async with GameScreen().run_test() as pilot:
        # Simulate combat
        await pilot.press("1")  # Attack
        # Verify UI updated
        combat_log = pilot.app.query_one(CombatLog)
        assert "dealt 15 damage" in combat_log.text
```

## Accessibility Considerations

1. **Screen Readers:** Use proper ARIA-like labels
2. **Color Blindness:** Don't rely solely on color
3. **Keyboard Navigation:** All features accessible via keyboard
4. **High Contrast:** Theme option for visibility

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Startup time | < 2s | Time to MainMenuScreen visible |
| Menu response | < 16ms | Keypress to visual feedback |
| Combat frame | < 33ms | Full combat update (30 FPS) |
| Memory usage | < 100MB | RSS during active gameplay |
| Scroll performance | 60 FPS | Combat log scrolling |

## Open Questions

1. ❓ Should we support terminal resize during gameplay?
   - **Decision:** Yes, Textual handles this automatically

2. ❓ Typewriter effect speed - configurable?
   - **Decision:** Add to settings, default 0.03s/char

3. ❓ ASCII art - show by default or toggle?
   - **Decision:** Toggle in settings, default ON

4. ❓ Mouse support - full or limited?
   - **Decision:** Full support where it makes sense (menus, shop)

---

**Next Steps:**
1. ✅ Complete this architecture document
2. → Create component mapping CSV for easy reference
3. → Design state flow diagram
4. → Begin Task 3: UI abstraction interface
