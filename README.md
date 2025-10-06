# Virtual Cow Tipper

> A humorous text-based RPG where you tip cows, battle aggressive cattle, and build your fortune through absurd bovine encounters.

## About

Virtual Cow Tipper is a terminal-based roguelike featuring:
- **Pack Reputation System** - Your actions affect future encounters with each cow pack
- **Dynamic Combat** - Face off against aggressive cows with unique attack patterns
- **Cow-Run Shops** - Buy and sell items from entrepreneurial cattle
- **Mini-Games** - Tipping bar, cow races, and guessing games
- **Absurdist Humor** - 100+ ridiculous cow scenarios and endless cow puns

## Quick Start

### Requirements
- Python 3.10 or higher
- Unix-like terminal (macOS, Linux, WSL on Windows)
- Terminal with curses support

### Installation
```bash
git clone <repository-url>
cd virtual-cow-tipper-text
python3 main.py
```

No dependencies needed - uses Python standard library only!

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

## Features

- **100+ Unique Cow Scenarios** - Each encounter has absurd flavor text
- **558 Lines of Dialogue** - Mood-based responses with cow puns
- **Dynamic Difficulty** - Cows scale with your progression
- **Smart Item Generation** - Rarity affects base stats (not just multipliers)
- **Persistent Personality** - Pause menu shows dialog history
- **Cross-Platform** - Runs on Mac, Linux, and Windows

## Game Stats

- **1,911 lines of gameplay code**
- **28 unit tests** - All passing
- **6 cow packs** to befriend or anger
- **92 cow names**
- **26 random interruption events**
- **3 mini-games**
- **20 weapon/shield types**
- **Infinite replay value**

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

## Credits

Created by Ed Conde (2023)
Modernized and completed (2025)

## License

Personal project - Educational use only

---

**Start your bovine adventure:** `python3 main.py`
