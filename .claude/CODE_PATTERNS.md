# Code Patterns & Best Practices

**Purpose**: Show Claude how to code correctly in this project
**Rule**: Follow these patterns, don't invent new ones

---

## UI Patterns (CRITICAL)

### Show Continuation Prompt
```python
# ✅ ALWAYS use this
self.pause_with_prompt("[Continue...]")

# In game.py class methods:
self._pause_with_prompt("[Continue...]")

# ❌ NEVER do this
prompt_y = self.game_terminal.PROMPT_INPUT_Y
self.game_terminal.stdscr.addstr(prompt_y, 2, "[Continue...]")
self.game_terminal.stdscr.refresh()
self.game_terminal.stdscr.getch()
```

### Show Message with Pause
```python
# ✅ Correct pattern
self.game_terminal.draw_dialog(message)
self.pause_with_prompt("[Continue...]")

# ❌ Never mix stdout with curses
print(message)  # Wrong!
safe_print(message)  # Wrong in curses mode!
```

### Menu Visibility Rules
```python
# ✅ Show menu: User choosing action
menu = ["1. Attack", "2. Flee", "3. Inventory"]
choice = self.game_terminal.get_menu_choice(menu)

# ✅ Hide menu: User just acknowledging
self.pause_with_prompt("[Press ENTER...]")  # Menu hidden automatically
```

---

## Screen State Preservation Pattern

### Save and Restore Dialogue State
```python
# ✅ When showing temporary screens (inventory, help, etc.)
def check_inventory(self):
    # Save current dialogue before showing inventory
    saved_dialog = self.game_terminal.save_dialog_state()

    # Show inventory screen
    self.game_terminal.draw_dialog(inventory_msg)
    # ... user interaction ...

    # Restore previous dialogue when done
    self.game_terminal.restore_dialog_state(saved_dialog)
```

**Use Cases**:
- Inventory viewing (preserves encounter intro)
- Help screens (preserves current context)
- Any temporary overlay that should return to previous state

**Don't Use**:
- When transitioning to new content (combat → shop)
- When dialogue should change (attack → damage message)

---

## Data Flow Patterns

### Return Values, Not Side Effects
```python
# ✅ CORRECT - Return data
def deal_damage(self, cow) -> tuple[int, Optional[str]]:
    damage = calculate_damage()
    flavor_text = get_flavor()
    cow.hp -= damage
    return (damage, flavor_text)

# ❌ WRONG - Side effects
def deal_damage(self, cow):
    damage = calculate_damage()
    safe_print(f"Dealt {damage}!")  # Don't print!
    cow.hp -= damage
```

### Using Returned Values
```python
# ✅ Use returned values
damage, flavor_text = player.deal_damage(cow)
if flavor_text:
    message = flavor_text
else:
    message = f"{player.name} attacks!"
self.game_terminal.draw_dialog(message)
```

---

## Encounter & Progression

### Encounter Tracking
```python
# ✅ Automatic via destroy_cow()
self.game_instance.destroy_cow()  # Increments counter, checks floor

# ❌ Don't manually track
self.encounters_this_floor += 1  # destroy_cow() does this
```

### Floor Advancement
```python
# ✅ Automatic
# destroy_cow() checks if encounters >= 10, calls advance_floor()

# ❌ Don't manually advance
self.current_floor += 1  # advance_floor() does this
```

---

## Configuration & Constants

### Use game_config.py
```python
# ✅ Import constants
from game_config import (
    PROMPT_CONTINUE,
    DICE_WIN_THRESHOLD,
    PLAYER_MAX_HP
)

# ❌ Don't hard-code
prompt = "[Continue...]"  # Use PROMPT_CONTINUE
win_threshold = 7  # Use DICE_WIN_THRESHOLD
max_hp = 100  # Use PLAYER_MAX_HP
```

### Add New Constants
```python
# Always add to game_config.py with clear comment
NEW_FEATURE_MULTIPLIER = 1.5  # Used for X calculation in Y

# Group related constants under section headers
# ============================================================================
# FEATURE NAME - Description
# ============================================================================
```

---

## Helper Usage

### UI Helpers
```python
from game_helpers import UIHelpers

# Show message and pause
UIHelpers.show_message_with_pause(
    game_terminal,
    "Victory!",
    prompt="[Continue...]"
)
```

### Combat Message Formatting
```python
from game_helpers import CombatMessageFormatter

# Format victory message
msg = CombatMessageFormatter.format_victory(
    cow_name="Bessie",
    cash_reward=60,
    item_drop="Steel Sword"
)
```

### Inventory Helpers
```python
from game_helpers import InventoryHelpers

# Find item by type
bucket = InventoryHelpers.find_item_by_type(inventory, Bucket)
```

---

## Common Anti-Patterns to AVOID

### ❌ Anti-Pattern 1: Direct Terminal Output
```python
# WRONG
print("Message")
safe_print("Message")

# CORRECT
self.game_terminal.draw_dialog("Message")
```

### ❌ Anti-Pattern 2: Not Hiding Menu
```python
# WRONG - Menu still visible
self.stdscr.addstr(y, x, "[Continue...]")
self.stdscr.getch()

# CORRECT - Menu hidden
self.pause_with_prompt("[Continue...]")
```

### ❌ Anti-Pattern 3: Clearing Dialogue Too Often
```python
# WRONG - Erases what user needs to read
self.clear_area(DIALOG_Y_START, DIALOG_Y_END)
self.draw_dialog(msg)

# CORRECT - Only clear when showing NEW flow
# Combat messages persist between turns
```

### ❌ Anti-Pattern 4: Magic Numbers
```python
# WRONG
if roll >= 7:  # What's 7?

# CORRECT
from game_config import DICE_WIN_THRESHOLD
if roll >= DICE_WIN_THRESHOLD:
```

---

## File Locations

### Where Code Goes
- **Core logic**: game.py, player.py, cow*.py
- **Constants**: game_config.py (ALWAYS)
- **Helpers**: game_helpers.py (shared utilities)
- **UI**: terminal/game_terminal.py (rendering only)
- **Systems**: dialogue_manager.py, item*.py, save_manager.py

### Where Documentation Goes
- **User-facing**: CHANGELOG.md (root)
- **Claude context**: .claude/ (these 3 files)
- **Detailed work**: .archive/sessions/DATE-topic.md
- **NEVER**: Root directory (except README/CHANGELOG)

---

## Quick Reference

### Starting a Session
1. Read .claude/RULES.md (documentation rules)
2. Read .claude/PROJECT_CONTEXT.md (project state)
3. Read .claude/FIXES_APPLIED.md (what's been fixed)
4. Read .claude/CODE_PATTERNS.md (this file - how to code)

### Ending a Session
1. Update CHANGELOG.md with summary
2. Add one-liner to FIXES_APPLIED.md (if fix applied)
3. Create .archive/sessions/DATE-work.md for details
4. NEVER leave new .md files in root

---

**Last Updated**: 2025-11-05
**Pattern Count**: 4 UI patterns, 2 data patterns documented
**Anti-Patterns**: 4 documented to avoid
