# Virtual Cow Tipper - Project Context

**DOCUMENTATION RULE**: Only README.md and CHANGELOG.md belong in root. All other docs go in .archive/sessions/DATE-topic.md. Read .claude/RULES.md for details.

**Last Updated**: 2025-11-05
**Status**: Fully functional, production-ready

---

## What This Is

Text-based roguelike game where you climb a tower by encountering cows, fighting aggressive ones, trading at shops, milking dairy cows, and playing mini-games. Build reputation with 6 different cow packs that affects future encounters.

**Tech Stack**: Python, Curses (primary UI), Textual (alternative modern UI)

---

## Current State

- ✅ Core game loop fully functional
- ✅ Curses UI working perfectly
- ✅ Textual UI migration complete (alternative)
- ✅ Save/load system working
- ✅ Career progression with unlocks
- ✅ Interactive inventory system
- ✅ Floor progression (10 encounters per floor)
- ✅ All major bugs fixed (see FIXES_APPLIED.md)

**How to Run**: `python3 main.py`

---

## Key Files & Architecture

### Core Game Logic
- **game.py** (461 lines) - Main game loop, encounter tracking, floor progression
- **player.py** (277 lines) - Player stats, inventory, combat actions, item usage
- **cow_interaction.py** (574 lines) - Handles combat, shop, dairy, mini-games
- **cow.py** - Cow generation, properties, mood system
- **cow_attack.py** - Cow attack mechanics (10 attack types)

### Configuration & Helpers
- **game_config.py** (271 lines) - ALL constants, balance values, prompts (68 constants)
- **game_helpers.py** (342 lines) - Utility classes (UIHelpers, CombatMessageFormatter, etc.)

### Systems
- **dialogue_manager.py** - Dialogue and flavor text
- **item.py** / **item_factory.py** - Items, weapons, shields, tools
- **save_manager.py** - Save/load game state
- **career_stats.py** - Career progression, unlocks
- **easter_eggs.py** - Easter eggs and special events

### UI (Curses)
- **terminal/game_terminal.py** - Curses terminal wrapper
- **terminal/pause_menu.py** - Pause menu system
- **main_menu.py** - Main menu

### UI (Textual - Alternative)
- **main_textual.py** - Textual entry point
- **ui/textual_app.py** - Textual application
- **ui/adapters/textual_adapter.py** - Textual adapter

---

## Critical Architecture Patterns

### UI Best Practices (MUST FOLLOW)

**1. Menu Visibility**:
- Show menu: When user makes a choice (Attack/Flee, Buy/Sell)
- Hide menu: When user just acknowledges (Press ENTER, Continue)

**2. Pause Pattern**:
```python
# ✅ ALWAYS use this pattern
self.pause_with_prompt("[Continue...]")

# ❌ NEVER do this
self.stdscr.addstr(y, x, "[Continue...]")
self.stdscr.getch()
```

**3. Dialogue Display**:
```python
# ✅ Use curses dialogue area
self.game_terminal.draw_dialog(message)

# ❌ Never use stdout in curses mode
print(message)  # Wrong!
safe_print(message)  # Wrong!
```

**4. Prompt Area Clearing**:
- ALWAYS clear prompt area before writing new prompt
- Prevents text overlap like "[Continue...]cow's turn...]"

### Data Flow Patterns

**1. Return Values, Not Side Effects**:
```python
# ✅ Correct
damage, flavor_text = player.deal_damage(cow)

# ❌ Wrong (old pattern)
player.deal_damage(cow)  # prints to stdout
```

**2. Encounter Tracking**:
```python
# Automatic - destroy_cow() handles it
self.game_instance.destroy_cow()  # Increments counter, advances floors
```

### Configuration

**1. Use game_config.py**:
- ALL constants and balance values belong here
- No magic numbers in code

**2. Use game_helpers.py**:
- Shared utilities (UIHelpers, CombatMessageFormatter, etc.)
- Don't duplicate code - use helpers

---

## Recent Major Fixes (2025-11-05)

1. **Encounter counter** - Now increments correctly, floors advance every 10
2. **Interactive inventory** - Can view, select, equip, use items in combat
3. **Menu hiding** - 31 instances now hide menu during continuation prompts
4. **Flavor text** - Appears in dialogue area, not terminal output
5. **Combat dialogue** - Messages persist between turns
6. **Floor progression** - Automatic advancement with celebration message
7. **Organizational** - game_helpers.py created, 68 constants added

**See**: FIXES_APPLIED.md for quick reference with line numbers

---

## Known Working Patterns

### Pause with Prompt (Used 31x)
```python
# In cow_interaction.py and game.py
self.pause_with_prompt("[Continue...]")
```

### Interactive Inventory
```python
# player.py:152 - Shows menu, allows selection
player.check_inventory()
# Returns to combat without advancing turn
```

### Deal Damage
```python
# player.py:71 - Returns values
damage, flavor_text = player.deal_damage(cow)
if flavor_text:
    msg = flavor_text  # Use flavor
else:
    msg = f"{player.name} attacks!"
```

---

## If User Reports Issues

1. Check CHANGELOG.md for recent changes
2. Check FIXES_APPLIED.md for what's been fixed
3. Check CODE_PATTERNS.md for correct implementation
4. Search .archive/sessions/ for detailed session work
5. All fixes include file:line_number references

---

## Development Guidelines

### Adding New Features
1. Update CHANGELOG.md with summary
2. Use game_config.py for constants
3. Use game_helpers.py for shared utilities
4. Follow UI patterns (pause_with_prompt, draw_dialog)
5. Document details in .archive/sessions/DATE-feature.md

### Fixing Bugs
1. Update CHANGELOG.md with one-line fix
2. Add to FIXES_APPLIED.md with file:line
3. Full details in .archive/sessions/DATE-bugfix.md

### Documentation
- **User-facing**: CHANGELOG.md
- **Claude context**: .claude/FIXES_APPLIED.md (one-liner)
- **Detailed work**: .archive/sessions/
- **NEVER**: Root directory .md files

---

**Last Updated**: 2025-11-05
**Documentation System**: Self-enforcing via .claude/RULES.md
