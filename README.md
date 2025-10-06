# Virtual Cow Tipper

```
     ____________________
    < No bull, just code >
     --------------------
      \   ^__^
       \  (oo)\_______
          (__)\       )\/\
              ||----w |
              ||     ||
```

A terminal-based roguelike RPG with strategic depth and absurdist humor.

## Overview

Virtual Cow Tipper is a Python-based roguelike featuring a unique pack reputation system, meta-progression mechanics, and procedural encounters. Players navigate a world where cows run shops, engage in combat, and participate in mini-games.

**Core Features:**
- Pack reputation system affecting future encounters
- Meta-progression with persistent unlocks
- Turn-based combat with strategic choices
- Dynamic difficulty scaling
- Save/load functionality

## Installation

### Requirements
- Python 3.10 or higher
- Terminal with curses support (included in standard library)

### Setup
```bash
git clone <repository-url>
cd virtual-cow-tipper-text
python3 main.py
```

No external dependencies required.

---

## Game Mechanics

## How to Play

### Goal
Survive by earning cash and maintaining your HP. Encounter various cows, each with unique personalities and challenges. Build your reputation with different cow packs to influence future encounters.

### Controls

**Menu Navigation:**
- Arrow keys (↑/↓) - Navigate menus
- Number keys (1-4) - Quick select options
- Enter - Confirm selection
- ESC - Pause menu

### Game Mechanics

#### Cow Encounters
Each cow belongs to one of 6 packs and has a mood (upset/neutral/friendly):

- **Aggressive Cows** - Fight or flee. Victory earns cash and improves pack reputation
- **Shop Cows** - Buy weapons, shields, and tools. Mood affects prices
- **Dairy Cows** - Milk with a bucket to obtain valuable Liquid Gold
- **Regular Cows** - Tip to play mini-games for rewards

#### Pack Reputation System
- **Win against a pack** - Future cows from that pack are friendlier
- **Lose to a pack** - Future cows from that pack are more hostile
- **Strategic depth** - Choose which packs to befriend

#### Combat
- **Base damage** - Scales with your cash (2-8 + cash/25)
- **Weapon damage** - Scaled by rarity (common → legendairy)
- **Shield defense** - Reduces incoming damage
- **Stun effects** - Some cow attacks stun you for multiple turns

#### Items & Rarity
- **5 Rarity Tiers:** Common, Uncommon, Magic, Rare, Legendairy
- **10 Weapon Types:** Dagger → Godsword
- **10 Shield Types:** Buckler → Aegis
- **Special Tools:** Cow Bell (attract dairy cows), Bucket (milk cows)

#### Shop Mechanics
- **Buy items** - Prices scale with your wealth
- **Sell items** - Get 50-70% value (mood-dependent)
- **Mood matters** - Upset cows charge 2x, Friendly cows pay more

#### Mini-Games
- **Tipping Bar** - Timing challenge, stop arrow at target
- **Cow Race** - Pick a cow and watch them race
- **Guessing Game** - Guess the cow's favorite number (hot/cold hints)

### Win/Lose Conditions

**Game Over:**
- HP reaches 0
- Cash reaches 0

**Victory:** (To be implemented)
- Defeat 50 cows
- Earn $5000
- Collect a full legendairy set

### Core Systems

**Pack Reputation:**
Each cow belongs to one of 6 packs. Your interactions affect future encounters:
- Defeating or befriending a pack improves relations
- Fleeing or angering a pack increases hostility
- Strategic choice: which packs to cultivate relationships with

**Meta-Progression:**
Career statistics persist across runs, unlocking permanent bonuses:
- 11 unlockable upgrades (increased HP, starting cash, equipment, etc.)
- Defeats contribute to long-term progress
- Encourages multiple playthroughs

**Encounter Types:**
- Combat encounters (aggressive cows)
- Shop encounters (buy/sell equipment)
- Dairy encounters (resource gathering)
- Mini-game encounters (optional gambling)

**Progression:**
- Floor-based structure (10 encounters per floor)
- Choice of rewards between floors
- Dynamic difficulty scaling
- Multiple victory conditions


## Development

### Run Tests
```bash
python3 run_tests.py
```

All 28 tests should pass.

### Project Structure
```
virtual-cow-tipper-text/
├── main.py              # Entry point
├── game.py              # Game loop and state
├── player.py            # Player stats and actions
├── cow.py               # Cow generation and behavior
├── cow_interaction.py   # Interaction handlers (combat, shop, dairy, tip)
├── cow_attack.py        # Combat system
├── cow_games.py         # Mini-games
├── item.py              # Item classes
├── item_factory.py      # Item generation
├── models.py            # Dataclasses
├── game_config.py       # All game balance constants
├── dialogue_manager.py  # Centralized dialogue system
├── terminal/            # Curses UI
│   ├── game_terminal.py
│   ├── pause_menu.py
│   └── dialog_history.py
├── assets/
│   └── context.py       # All dialogue text
└── tests/               # Unit tests
```

## Technical Details

- **Language:** Python 3.10+
- **UI:** curses (terminal-based)
- **Architecture:** Object-oriented, factory pattern, dataclasses
- **Testing:** 44 unit tests
- **Lines of Code:** ~5,600

## Development

### Running Tests
```bash
python3 run_tests.py
```

### Project Structure
Clean separation of concerns with dedicated modules for game logic, dialogue management, item generation, and save/load functionality.

---

## Credits

Created by Ed Conde

## License

Personal project - Educational use only

---

*Run the game:* `python3 main.py`
