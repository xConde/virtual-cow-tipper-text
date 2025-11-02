# State Flow Diagram: Game Logic ↔ UI

## Overview

This document illustrates how data flows between game logic and UI components in the Textual architecture.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Application Layer                         │
│                                                                   │
│  ┌───────────────┐                          ┌─────────────────┐ │
│  │               │                          │                 │ │
│  │  CowTipperApp │◄────── manages ─────────►│  Screen Stack   │ │
│  │   (Textual)   │                          │  (Navigation)   │ │
│  │               │                          │                 │ │
│  └───────┬───────┘                          └─────────────────┘ │
│          │                                                       │
│          │ owns                                                  │
│          ▼                                                       │
│  ┌───────────────┐                                              │
│  │               │                                              │
│  │  UI Adapter   │                                              │
│  │  (Textual)    │                                              │
│  │               │                                              │
│  └───────┬───────┘                                              │
└──────────┼───────────────────────────────────────────────────────┘
           │
           │ delegates to
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Bridge Layer                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    GameUIBridge                           │  │
│  │                                                            │  │
│  │  ┌────────────┐        ┌────────────┐                    │  │
│  │  │Event Queue │───────►│  Processor │                    │  │
│  │  │  (deque)   │        │  (async)   │                    │  │
│  │  └────────────┘        └────────────┘                    │  │
│  │                                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│           ▲                                    │                 │
│           │                                    │                 │
│     emit_event()                        on_game_event()          │
│           │                                    │                 │
└───────────┼────────────────────────────────────┼─────────────────┘
            │                                    │
            │                                    ▼
┌───────────┼────────────────────────────────────────────────────┐
│           │                 Game Logic Layer                    │
│           │                                                     │
│  ┌────────┴────────┐                                           │
│  │                 │                                           │
│  │ VirtualCowTipper│                                           │
│  │      Game       │                                           │
│  │                 │                                           │
│  └────────┬────────┘                                           │
│           │                                                     │
│           │ manages                                             │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                  Game State                              │  │
│  │  ┌───────────┐  ┌────────┐  ┌──────────┐  ┌─────────┐  │  │
│  │  │  Player   │  │  Cow   │  │ Inventory│  │  Floor  │  │  │
│  │  │   Data    │  │  Data  │  │   Data   │  │  Data   │  │  │
│  │  └───────────┘  └────────┘  └──────────┘  └─────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow Patterns

### Pattern 1: Game Event → UI Update

```
Step 1: Game Logic Change
┌──────────────────────┐
│   game.py            │
│                      │
│  player.take_damage()│
│    ↓                 │
│  player.hp = 50      │
└──────────┬───────────┘
           │
           │ Step 2: Emit Event
           ▼
┌──────────────────────────────┐
│   ui_bridge.py               │
│                              │
│  emit_event("damage_taken", {│
│    'target': 'player',       │
│    'amount': 15,             │
│    'new_hp': (50, 100)       │
│  })                          │
└───────────┬──────────────────┘
            │
            │ Step 3: Queue Event
            ▼
┌──────────────────────────────┐
│   Event Queue                │
│   [event1, event2, ...]      │
└───────────┬──────────────────┘
            │
            │ Step 4: Process Event
            ▼
┌──────────────────────────────┐
│   textual_adapter.py         │
│                              │
│  on_game_event(              │
│    "damage_taken",           │
│    data                      │
│  )                           │
└───────────┬──────────────────┘
            │
            │ Step 5: Update UI
            ▼
┌──────────────────────────────┐
│   PlayerStatsPanel           │
│                              │
│  self.hp = (50, 100)  ◄──────── Reactive property
│    ↓                         │
│  watch_hp() called           │
│    ↓                         │
│  update_hp_bar()             │
│    ↓                         │
│  Visual update to screen     │
└──────────────────────────────┘
```

### Pattern 2: User Input → Game Action

```
Step 1: User Presses Key
┌──────────────────────┐
│   User Input         │
│   [Press "1"]        │
└──────────┬───────────┘
           │
           │ Step 2: Textual Event
           ▼
┌──────────────────────────────┐
│   ActionMenu                 │
│                              │
│  async on_key(event):        │
│    if event.key == "1":      │
│      await self.attack()     │
└───────────┬──────────────────┘
            │
            │ Step 3: Notify Game
            ▼
┌──────────────────────────────┐
│   textual_adapter.py         │
│                              │
│  async handle_attack():      │
│    result = await            │
│      game.player_attack()    │
└───────────┬──────────────────┘
            │
            │ Step 4: Execute Game Logic
            ▼
┌──────────────────────────────┐
│   game.py / combat.py        │
│                              │
│  calculate_damage()          │
│  apply_damage()              │
│  emit_event("damage_dealt")  │
└───────────┬──────────────────┘
            │
            │ Step 5: Loop back to Pattern 1
            └─────────► [Emit Event]
```

### Pattern 3: Reactive State Synchronization

```
Game State Update
┌─────────────────────┐
│   game.py           │
│                     │
│  player.cash += 50  │
└──────────┬──────────┘
           │
           │ Periodic Sync (every frame or on change)
           ▼
┌──────────────────────────────┐
│   textual_adapter.py         │
│                              │
│  async update_stats():       │
│    player_stats = {          │
│      'cash': player.cash,    │
│      'hp': (hp, max_hp),     │
│      ...                     │
│    }                         │
│    await ui.update_stats()   │
└───────────┬──────────────────┘
            │
            │ Assign to reactive property
            ▼
┌──────────────────────────────┐
│   PlayerStatsPanel           │
│                              │
│  self.cash = 100  ◄──────────── Assignment
│    ↓                         │
│  watch_cash() ◄──────────────── Auto-called
│    ↓                         │
│  update_cash_display()       │
│    ↓                         │
│  "$100" rendered on screen   │
└──────────────────────────────┘
```

## State Lifecycle

### Application Lifecycle

```
[App Start]
    ↓
┌────────────────────┐
│ App.__init__()     │  • Create game instance
│                    │  • Setup UI adapter
│                    │  • Initialize bridge
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ App.on_mount()     │  • Register screens
│                    │  • Push MainMenuScreen
│                    │  • Start event loop
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Event Loop Running │  • Process user input
│ (async)            │  • Handle game events
│                    │  • Update displays
└─────────┬──────────┘
          │
          │ (game continues)
          │
          ▼
┌────────────────────┐
│ App.exit()         │  • Save state
│                    │  • Cleanup resources
│                    │  • Return to terminal
└────────────────────┘
    ↓
[App End]
```

### Screen Lifecycle

```
[Screen Created]
    ↓
┌────────────────────┐
│ Screen.__init__()  │  • Setup widgets
│                    │  • Initialize state
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Screen.compose()   │  • Define widget tree
│                    │  • Return widgets
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Screen.on_mount()  │  • Setup bindings
│                    │  • Load data
│                    │  • Start animations
└─────────┬──────────┘
          │
          │ (screen active)
          │
          ▼
┌────────────────────┐
│ Screen.on_unmount()│  • Cleanup
│                    │  • Stop timers
└─────────┬──────────┘
          │
          ▼
[Screen Destroyed]
```

### Widget State Updates

```
[Property Changed]
    ↓
┌──────────────────────┐
│ widget.property = x  │  • Assignment
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ watch_property()     │  • Auto-called by Textual
│                      │  • Receives old, new values
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ Update internal      │  • Modify appearance
│ state                │  • Calculate derived values
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ self.refresh()       │  • Mark dirty
│                      │  • Textual queues redraw
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ render()             │  • Generate visual output
│                      │  • Return Rich renderable
└─────────┬────────────┘
          │
          ▼
[Screen Updated]
```

## Combat Flow Example

```
[Player selects "Attack"]
    ↓
┌────────────────────────────┐
│ GameScreen.on_key("1")     │
└─────────┬──────────────────┘
          │
          ▼
┌────────────────────────────┐
│ game.player_attack()       │  Game Logic
│   • Calculate damage       │
│   • Apply to cow.hp        │
│   • Determine hit/miss     │
└─────────┬──────────────────┘
          │
          ▼
┌────────────────────────────┐
│ ui_bridge.emit_event(      │  Event Bridge
│   "attack_executed", {     │
│     attacker: "Player",    │
│     damage: 15,            │
│     hit: true              │
│   }                        │
│ )                          │
└─────────┬──────────────────┘
          │
          ▼
┌────────────────────────────┐
│ CombatDisplay              │  UI Update
│   • Animate attack         │
│   • Flash screen           │
│   • Add log entry          │
│   • Update HP bar          │
└─────────┬──────────────────┘
          │
          ▼
┌────────────────────────────┐
│ game.cow_turn()            │  Game Logic
│   • AI selects action      │
│   • Calculate counter      │
│   • Apply to player.hp     │
└─────────┬──────────────────┘
          │
          ▼
┌────────────────────────────┐
│ ui_bridge.emit_event(      │  Event Bridge
│   "attack_executed", {     │
│     attacker: "Cow",       │
│     damage: 8,             │
│     hit: true              │
│   }                        │
│ )                          │
└─────────┬──────────────────┘
          │
          ▼
┌────────────────────────────┐
│ CombatDisplay              │  UI Update
│   • Animate counter        │
│   • Screen shake           │
│   • Add log entry          │
│   • Update player HP       │
└─────────┬──────────────────┘
          │
          ▼
┌────────────────────────────┐
│ Check combat end           │  Game Logic
│   • Victory?               │
│   • Defeat?                │
│   • Continue?              │
└─────────┬──────────────────┘
          │
          ├──► [Victory] → emit_event("combat_won")
          ├──► [Defeat]  → emit_event("player_died")
          └──► [Continue] → wait for player input
```

## State Ownership

### Game Logic Owns:
- ✅ Player HP, cash, inventory
- ✅ Cow properties, AI state
- ✅ Combat calculations
- ✅ Item effects
- ✅ Floor progression
- ✅ Save/load data

### UI Owns:
- ✅ Currently active screen
- ✅ Selected menu index
- ✅ Animation states (in-progress)
- ✅ Scroll positions
- ✅ Widget visibility
- ✅ User preference (themes, speeds)

### Shared (Synchronized):
- 🔄 Current display mode (combat vs shop vs dialogue)
- 🔄 Available actions (dynamic menu)
- 🔄 Dialogue state (current text, choices)

## Event Types

### Game → UI Events

| Event Type | Data | Triggered By | UI Response |
|------------|------|--------------|-------------|
| `combat_start` | player, cow | combat.py | Show CombatDisplay |
| `damage_dealt` | attacker, target, amount | combat.py | Animate, update HP bar |
| `damage_taken` | target, amount, new_hp | combat.py | Flash, shake, update HP |
| `item_obtained` | item, source | game.py | Show notification popup |
| `item_used` | item, effect | player.py | Show effect animation |
| `floor_complete` | new_floor, stats | game.py | Show transition screen |
| `combat_won` | rewards | combat.py | Show victory screen |
| `player_died` | stats | game.py | Show defeat screen |
| `dialogue_start` | speaker, text | interaction.py | Show DialogueWidget |
| `shop_entered` | inventory | interaction.py | Show ShopDisplay |
| `game_saved` | filename | save_manager.py | Show confirmation |

### UI → Game Events

| Event Type | Data | Triggered By | Game Response |
|------------|------|--------------|---------------|
| `action_attack` | None | User input | Execute player attack |
| `action_defend` | None | User input | Player defends |
| `action_item` | item_id | User input | Use item |
| `action_run` | None | User input | Attempt escape |
| `shop_buy` | item_id | Shop widget | Process purchase |
| `shop_sell` | item_id | Shop widget | Process sale |
| `dialogue_choice` | choice_index | Dialogue widget | Process choice |
| `save_requested` | None | Pause menu | Save game |
| `load_requested` | None | Main menu | Load game |

## Synchronization Strategy

### Push (Event-Driven) - Preferred
```python
# Game pushes changes to UI via events
await ui_bridge.emit_event("hp_changed", {'hp': (50, 100)})
```

### Pull (Polling) - Fallback
```python
# UI polls game state periodically
async def update_loop(self):
    while self.running:
        player_stats = self.game.get_player_stats()
        self.update_display(player_stats)
        await asyncio.sleep(0.016)  # 60 Hz
```

**Decision:** Use Push for most events, Poll for continuous updates (combat)

## Thread Safety

### Async-Safe Pattern
```python
# Game runs in same async loop as UI
async def player_turn(self):
    choice = await self.ui.show_menu(actions)
    result = await self.execute_action(choice)
    await self.ui_bridge.emit_event("action_complete", result)
```

### No Threading Needed
- Everything runs in single async event loop
- No locks or mutexes required
- Simpler debugging and testing

---

**Status:** Complete
**Last Updated:** 2025-11-01
