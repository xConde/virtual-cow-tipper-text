# Test Scenarios - Quick Game State Setup

**Purpose**: Pre-configured save files for testing specific game situations

---

## Available Scenarios

### 1. early_game.json
**Player**: Newbie
**State**: Brand new game
- HP: 20, Cash: $50
- No equipment, empty inventory
- Floor 1, Encounter #1
- All pack reputations neutral

**Test**: New player experience, basic mechanics

---

### 2. mid_game_equipped.json
**Player**: Warrior
**State**: Moderate progression
- HP: 80, Cash: $300
- Steel Sword + Wooden Shield equipped
- Iron Sword in inventory (can test upgrades)
- Cow Bell + Bucket (test dairy/tools)
- Floor 2, Encounter #6
- Some friendly packs, some upset

**Test**: Equipment system, inventory, mid-game balance

---

### 3. late_game_rich.json
**Player**: Tycoon
**State**: High-level, well-equipped
- HP: 100, Cash: $1500
- Legendary weapon + shield equipped
- Multiple rare items in inventory
- Floor 5, 45 cows defeated
- Strong pack reputations (friendly/upset)

**Test**: Late-game balance, high-tier items, expensive shops

---

### 4. challenge_low_resources.json
**Player**: Struggler
**State**: Difficult situation
- HP: 15, Cash: $10
- No equipment
- Floor 3, but poor performance
- All packs upset (bad reputation)

**Test**: Survival mechanics, low-cash scenarios, difficulty

---

### 5. dev_save.example.json (Default)
**Player**: DevTester
**State**: Balanced testing state
- HP: 90, Cash: $500
- Mix of equipment
- Floor 3, good progression

**Test**: General feature testing

---

## How to Use

**Quick Switch**:
```bash
# Copy scenario to active save
cp saves/scenarios/early_game.json saves/game_save.json

# Run game
python3 main.py
# Select "2. Continue"
```

**Test Specific Features**:
- **Mini-game betting**: Use early_game (low cash) vs late_game (high cash)
- **Equipment system**: Use mid_game_equipped (has items to swap)
- **Shop system**: Use late_game_rich (can afford everything)
- **Survival**: Use challenge_low_resources (difficult mode)

---

## Scenario Organization

```
saves/
├── game_save.json              ← Active save (gitignored)
├── dev_save.example.json       ← Default dev template
└── scenarios/                  ← Test scenarios (committed)
    ├── README.md               ← This file
    ├── early_game.json         ← New player
    ├── mid_game_equipped.json  ← Moderate progress
    ├── late_game_rich.json     ← End game
    └── challenge_low_resources.json ← Hard mode
```

**Committed to git**: All scenario files (templates)
**Gitignored**: game_save.json (active save)

---

## Testing Workflows

### Test Mini-Game Scaling
```bash
# Test early game bets ($3-6 range)
cp saves/scenarios/early_game.json saves/game_save.json
python3 main.py → Continue → Find friendly cow → Test betting

# Test late game bets ($15-30 range)
cp saves/scenarios/late_game_rich.json saves/game_save.json
python3 main.py → Continue → Find friendly cow → Test betting
```

### Test Inventory System
```bash
# Has multiple items to swap
cp saves/scenarios/mid_game_equipped.json saves/game_save.json
python3 main.py → Continue → Inventory → Equip/view items
```

### Test Low-Cash Scenarios
```bash
# Can't afford much
cp saves/scenarios/challenge_low_resources.json saves/game_save.json
python3 main.py → Continue → Try to bet (cautious only)
```

---

**Status**: Organized seed system for comprehensive testing
**Usage**: Copy scenario → Run → Test specific feature
