# Fixes Applied - Quick Reference

**Purpose**: Quick lookup of what's been fixed and where
**Format**: Date, issue, location (file:line)

---

## 2025-11-05 Session (9 major fixes)

1. **Menu hiding during continuation prompts** (31 instances)
   - cow_interaction.py:540 - pause_with_prompt() helper
   - game.py:394 - _pause_with_prompt() helper
   - Pattern: Always hide menu when showing "[Continue...]" style prompts

2. **Encounter counter not incrementing**
   - game.py:128 - destroy_cow() increments encounters_this_floor
   - Result: Encounters now count #1, #2, #3... correctly

3. **Floor progression system non-functional**
   - game.py:134 - advance_floor() method created
   - game.py:131 - Triggers every 10 encounters automatically

4. **Flavor text in wrong location**
   - player.py:71 - deal_damage() returns (damage, flavor_text) tuple
   - player.py:52 - get_damage_context() generates flavor
   - cow_interaction.py:152 - Uses returned flavor in dialogue

5. **Blank dialogue in combat**
   - cow_interaction.py:116 - Combat draws intro (cow.approach)
   - cow_interaction.py:142 - Don't clear dialogue between turns

6. **Interactive inventory broken**
   - player.py:152 - check_inventory() fully interactive
   - player.py:93 - _show_item_actions() for equip/use
   - Result: Can view, select, equip, use items in combat

7. **Overlapping prompt text** ("[Continue...]cow's turn...]")
   - Fixed by always clearing prompt area first
   - pause_with_prompt() pattern enforces this

8. **Organizational improvements**
   - game_helpers.py created (6 utility classes)
   - game_config.py +68 constants added

9. **"Prepare to fight!" removed** (user feedback)
   - cow_interaction.py:116 - Just shows cow.approach

---

## Earlier Sessions

### 2025-11-04 - QA Testing
- Screen layout fixes
- Menu refresh improvements
- Dialogue rendering fixes

### 2025-11-01 - Migration Complete
- Textual UI migration finished
- Dual UI support (Curses + Textual)
- 13 tasks completed

**Full history**: See .archive/sessions/ for detailed work

---

## Patterns to Follow

### UI Pattern
```python
# ✅ Correct - Hide menu during pauses
self.pause_with_prompt("[Continue...]")

# ❌ Wrong - Menu stays visible
self.stdscr.addstr(y, x, "[Continue...]")
self.stdscr.getch()
```

### Data Pattern
```python
# ✅ Correct - Return values
damage, flavor = player.deal_damage(cow)

# ❌ Wrong - Side effects
player.deal_damage(cow)  # Prints to stdout
```

### Configuration Pattern
```python
# ✅ Correct - Use constants
from game_config import PROMPT_CONTINUE
self.pause_with_prompt(PROMPT_CONTINUE)

# ❌ Wrong - Hard-coded strings
self.pause_with_prompt("[Continue...]")
```

---

**Last Updated**: 2025-11-05
**Total Fixes Tracked**: 9 major fixes this session
**See Also**: CODE_PATTERNS.md for implementation examples
