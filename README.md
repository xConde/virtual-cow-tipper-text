# Virtual Cow Tipper

*Moo!*

Text-based roguelike. Climb the Cow Towers. Survive encounters. Build your reputation.

---

## Quick Start

```bash
python3 main.py
```

**Requires**: Python 3.7+

---

## Gameplay

**Encounter Types**:
- **Combat** - Fight or flee aggressive cows
- **Shop** - Buy weapons, sell loot, get stronger
- **Dairy** - Milk cows for valuable resources (need bucket)
- **Mini-Game** - Bet on dice, choose your stakes, win cash

**Progression**:
- 10 encounters per floor
- Advance floors automatically
- Build reputation with 6 cow packs
- Interactive inventory (equip gear, use potions)

**Strategy**:
- Friendly packs = easier encounters
- Upset packs = harder enemies
- Choose which packs to befriend

---

## Controls

- **Navigate**: Arrows or Numbers
- **Select**: SPACE or ENTER
- **Pause**: ESC

---

## New Features (2025-11-08)

**Enhanced Mini-Games**:
- Choose your bet: Cautious / Normal / Bold
- Friendly cows: Cheaper bets, easier odds (6+ to win)
- Rematch system: Double-or-nothing after losses
- Bets scale with floor, cash, and encounter progress

**Balance**:
- Multi-factor bet scaling (floor 40%, cash 40%, encounter 20%)
- Smooth progression throughout game
- Personality affects difficulty and rewards

---

## Development

**Test Scenarios** (5 pre-configured game states):
```bash
# New player
cp saves/scenarios/early_game.json saves/game_save.json

# Equipped warrior
cp saves/scenarios/mid_game_equipped.json saves/game_save.json

# End-game tycoon
cp saves/scenarios/late_game_rich.json saves/game_save.json

# Then: python3 main.py → Continue
```

**Dev Save Auto-Replenishes**:
- Delete `saves/game_save.json` anytime
- Game auto-restores from template on startup
- Reliable testing workflow

**Documentation**:
- `CHANGELOG.md` - Recent changes
- `.claude/` - Code patterns and project context
- `.archive/` - Detailed session notes

---

## Project Structure

**Core**:
- `game.py` - Main loop, encounters, floor system
- `cow_interaction.py` - Combat, shop, mini-games, dairy
- `player.py` - Inventory, stats, equipment
- `game_config.py` - All balance constants

**Systems**:
- `item.py` / `item_factory.py` - Items and generation
- `dialogue_manager.py` - Centralized dialogue
- `save_manager.py` - Save/load functionality
- `terminal/` - Curses UI wrapper

**Alternative UI**: `main_textual.py` for modern Textual UI (optional)

---

*Virtual Cow Tipper - Climb the tower. Survive. Moo.*
