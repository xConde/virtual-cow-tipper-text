# Virtual Cow Tipper - Project Overview

## Project Summary
A terminal-based roguelike RPG with absurdist humor where players tip cows, engage in turn-based combat, and navigate existential cow dialogues. Built with Python using curses for terminal UI.

## Current Architecture

### Core Game Systems

#### 1. Game Loop (`game.py`)
- Main game state management
- Turn-based gameplay flow
- Floor progression system (10 encounters per floor)
- Victory/defeat conditions
- Integration with all subsystems

#### 2. Combat System (`cow_interaction.py`, `cow_attack.py`)
- Turn-based combat with 10 attack types
- Special effects: stun, increased damage, damage over time
- Pack reputation system affecting cow behavior
- Combat rewards: cash and item drops

#### 3. Entity System
- **Player** (`player.py`): HP, cash, inventory, equipped items
- **Cows** (`cow.py`): Randomized properties, personalities, pack affiliation
- **Items** (`item.py`, `item_factory.py`): 5 rarity tiers, weapons, shields, consumables

#### 4. Progression Systems
- **Meta-progression** (`career_stats.py`): Unlock system across runs
- **Save System** (`save_manager.py`): Complete game state persistence
- **Difficulty Scaling**: Based on player level and floor

### Current UI Implementation (Curses)

#### Terminal Layout (85x30 fixed)
```
┌─────────────────────────────────────────────────┐
│ Player Stats            |        Cow Stats      │ Line 0-2
├─────────────────────────────────────────────────┤
│                  Game Title                     │ Line 2-4
├─────────────────────────────────────────────────┤
│                                                  │
│               ASCII Art Area                    │ Line 5-19
│                  (Combat/Cows)                  │
│                                                  │
├─────────────────────────────────────────────────┤
│ Dialogue Text (word-wrapped, 2 lines max)       │ Line 20-21
├─────────────────────────────────────────────────┤
│ Instructions/Prompts                            │ Line 22-23
├─────────────────────────────────────────────────┤
│ Input Prompt                                    │ Line 24
├─────────────────────────────────────────────────┤
│ > Menu Item 1 <                                 │
│   Menu Item 2                                   │ Line 25-28
│   Menu Item 3                                   │
└─────────────────────────────────────────────────┘
```

#### UI Components
- **GameTerminal** (`terminal/game_terminal.py`): Main display manager
- **MainMenu** (`main_menu.py`): Game start menu with ASCII art
- **PauseMenu** (`terminal/pause_menu.py`): In-game pause functionality
- **DialogHistory** (`terminal/dialog_history.py`): Dialogue tracking

### Key Features

#### Gameplay Features
- 4 encounter types: Combat, Shop, Random Event, Escape
- Mini-games for special encounters
- Pack reputation affecting future encounters
- Floor-based progression with scaling difficulty

#### Content Systems
- **Dialogue Manager** (`dialogue_manager.py`): Contextual dialogue with personality types
- **Easter Eggs** (`easter_eggs.py`): Hidden content and developer mode
- **Tutorial** (`tutorial.py`): New player onboarding

#### Technical Features
- Cross-platform support (Windows/Mac/Linux)
- Comprehensive test suite (28 tests)
- Configuration centralized in `game_config.py`
- Type hints throughout codebase

## Recent Updates (Current Branch: refactor/architecture-optimization)

### Major Improvements
1. **UI Fixes**: Safe margins, word wrapping, fixed menu navigation
2. **Combat Display**: HP bars, combat log, better visual feedback
3. **Balance Overhaul**: Game is now actually winnable
4. **Save/Load System**: Full persistence implementation
5. **Meta-progression**: Career stats and unlocks for replay value
6. **Test Suite**: 28 comprehensive tests including crash scenarios
7. **Dialogue System**: Mature, existential humor with contextual responses

### Bug Fixes
- Fixed menu rendering and alignment issues
- Resolved ASCII art display problems
- Fixed duplicate cow dialogue
- Corrected floor tracking initialization
- Fixed safe_print import errors

## Project Statistics
- **Total Files**: 37+ Python modules
- **Lines of Code**: ~5,000+ lines
- **Test Coverage**: 8 test suites, 28 test cases
- **Recent Changes**: +5,084 additions, -483 deletions

## Dependencies
- Python 3.8+
- curses (built-in)
- Additional packages in `requirements.txt`

## File Organization
```
virtual-cow-tipper-text/
├── Core Game Logic
│   ├── game.py              # Main game loop
│   ├── player.py            # Player class
│   ├── cow.py               # Cow entities
│   └── game_config.py       # Configuration
├── Systems
│   ├── cow_interaction.py   # Combat system
│   ├── item_factory.py      # Item generation
│   ├── dialogue_manager.py  # Dialogue system
│   └── save_manager.py      # Save/load
├── UI Components
│   ├── terminal/            # Curses UI
│   ├── main_menu.py         # Start menu
│   └── help_screen.py       # Help system
├── Content
│   ├── assets/              # Game content
│   ├── easter_eggs.py       # Hidden content
│   └── tutorial.py          # Tutorial
└── Testing
    └── tests/               # Test suite
```

## Known Limitations
- Fixed terminal size (85x30)
- Manual coordinate positioning
- Limited visual flexibility with curses
- No mouse support in game (only menus)
- ASCII art only, no colors or styling