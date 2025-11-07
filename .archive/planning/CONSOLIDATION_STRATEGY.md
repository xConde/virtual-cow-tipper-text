# Documentation Consolidation Strategy - Minimal & Practical

**Goal**: Essential docs for humans + knowledge base for Claude sessions
**Principle**: Maximum usefulness, minimum burden

---

## The Problem

**Current**: 21 .md files - overwhelming, redundant, hard to maintain
**User needs**: Quick reference, not essay reading
**Claude needs**: Context about the project, what's been fixed, what works

---

## The Solution: 3-Tier Documentation System

### Tier 1: FOR HUMANS (Root Directory)

**Keep only what you actually read**:

```
├── README.md                 # Quick start guide (< 50 lines)
│   - What is this project?
│   - How to run it: python3 main.py
│   - Basic controls
│   - Where to find more info
│
└── CHANGELOG.md              # What changed recently (< 100 lines)
    - Latest session changes
    - Bug fixes applied
    - New features added
    - Breaking changes (if any)
```

**That's it.** Just 2 files you might actually look at.

---

### Tier 2: FOR CLAUDE (/.claude/ directory)

**Context files Claude reads when starting a session**:

```
.claude/
├── PROJECT_CONTEXT.md        # "Read this first" for Claude
│   - Project overview (3 paragraphs)
│   - Current state: "Migration complete, curses working"
│   - Key files and their purpose
│   - Known issues (if any)
│   - Architecture patterns to follow
│
├── FIXES_APPLIED.md          # What's been fixed (reference)
│   - Condensed list of all fixes with dates
│   - Line numbers for key changes
│   - Patterns to follow (pause_with_prompt, etc.)
│
└── CODE_PATTERNS.md          # Best practices to follow
    - UI patterns: when to hide menu
    - Helper usage: pause_with_prompt()
    - Configuration: use game_config.py constants
    - Examples of correct patterns
```

**Size**: 3 files, ~300 lines total (vs 21 files, ~1500+ lines)

---

### Tier 3: FOR REFERENCE (/.archive/ directory)

**Everything else - queryable but not visible**:

```
.archive/
├── sessions/
│   ├── 2025-11-05-quality-fixes.md     # Today's detailed work
│   ├── 2025-11-04-qa-testing.md
│   ├── 2025-11-02-migration.md
│   └── ...
│
├── reviews/
│   ├── CODE_REVIEW.md
│   ├── MANUAL_QA_CHECKLIST.md
│   └── ...
│
└── planning/
    ├── ROLLBACK_PLAN.md
    ├── CONSOLIDATION_ROADMAP.md
    └── ...
```

**Purpose**: Historical record, detailed notes, searchable when needed
**Visibility**: Out of sight, but can grep/search if needed

---

## What Each Tier Contains

### README.md (Human - Quick Start)
```markdown
# Virtual Cow Tipper

Text-based roguelike cow tipping game.

## Quick Start
python3 main.py

## Controls
- Arrows/Numbers: Navigate menus
- SPACE/ENTER: Select
- ESC: Pause

## Current Status
✅ Fully functional
✅ Curses UI working
✅ Textual UI migration complete

## For Developers
See `.claude/PROJECT_CONTEXT.md` for architecture overview.
```

**Length**: ~30 lines

---

### CHANGELOG.md (Human - Recent Changes)
```markdown
# Changelog

## 2025-11-05 - Quality & Organization Improvements

### Fixed
- Encounter counter now increments correctly
- Inventory system fully interactive (view/equip/use items)
- Menu hiding during continuation prompts
- Flavor text appears in correct dialogue area
- Floor progression system working

### Added
- game_helpers.py - Utility functions
- 68 new constants to game_config.py
- Interactive inventory with item actions

### Technical
- Refactored player.deal_damage() to return values
- Created pause_with_prompt() pattern (used 31x)
- Floor advancement every 10 encounters

---

## 2025-11-04 - Previous Session
(Brief summary of previous work)
```

**Length**: ~50-100 lines, recent changes only

---

### .claude/PROJECT_CONTEXT.md (Claude - Essential Knowledge)
```markdown
# Virtual Cow Tipper - Project Context

**Last Updated**: 2025-11-05
**Status**: Fully functional, recent quality improvements

## What This Is
Text-based roguelike game. Player encounters cows, fights/trades/tips them,
climbs floors, builds reputation with cow packs.

## Current State
- ✅ Core game loop working (game.py)
- ✅ Curses UI fully functional
- ✅ Textual UI migration complete (alternative UI)
- ✅ Save/load system working
- ✅ Career progression working

## Key Files & Purpose
- game.py (461 lines) - Main game loop, encounter system
- player.py (277 lines) - Player actions, inventory, combat
- cow_interaction.py (574 lines) - Combat, shop, dairy, mini-games
- game_config.py (271 lines) - ALL constants and balance values
- game_helpers.py (342 lines) - Utility functions (NEW)
- terminal/game_terminal.py - Curses terminal wrapper

## Architecture Patterns

### UI Best Practices
1. Always use pause_with_prompt() for continuation prompts (hides menu)
2. Clear prompt area before writing new prompts
3. Use draw_dialog() for all user-facing text (not safe_print!)
4. Menu only visible during choices, hidden during pauses

### Code Organization
- Use game_config.py for all constants (68 added recently)
- Use game_helpers.py for shared utilities (6 helper classes)
- No magic numbers in code
- No stdout mixing with curses

### Encounter System
- encounters_this_floor counter increments on destroy_cow()
- Floor advances every 10 encounters
- All interaction types (combat/shop/dairy/rest) count as encounters

## Recent Fixes (2025-11-05)
- Fixed encounter counter not incrementing
- Fixed blank dialogue in combat
- Fixed inventory system (now interactive)
- Fixed flavor text appearing in wrong location
- Implemented menu hiding system (31 instances)

## Known Working Patterns
- pause_with_prompt() - Used 31x across codebase
- destroy_cow() - Properly increments encounter counter
- deal_damage() - Returns (damage, flavor_text) tuple
- check_inventory() - Interactive selection menu

## If User Reports Issues
- Check CHANGELOG.md for recent changes
- See .archive/sessions/YYYY-MM-DD-*.md for detailed session work
- All fixes documented with file:line_number references
```

**Length**: ~100 lines, essential context only

---

### .claude/FIXES_APPLIED.md (Claude - Quick Reference)
```markdown
# Fixes Applied - Quick Reference

## 2025-11-05 Session (9 fixes)

1. **Menu hiding** - pause_with_prompt() pattern (31 instances)
   - cow_interaction.py, game.py

2. **Encounter counter** - destroy_cow() increments (game.py:128)

3. **Floor progression** - advance_floor() every 10 encounters (game.py:134)

4. **Flavor text** - deal_damage() returns tuple (player.py:71)

5. **Interactive inventory** - check_inventory() with selection (player.py:152)

6. **Combat dialogue** - Messages persist between turns

7. **Blank dialogue fix** - Combat draws intro (cow_interaction.py:116)

8. **Prompt overlap** - Always clear before writing

9. **Organizational** - game_helpers.py, 68 config constants

## 2025-11-04 Session
(Previous fixes - condensed)

## Patterns to Follow

### UI Pattern
```python
# ✅ Correct
self.pause_with_prompt("[Continue...]")

# ❌ Wrong
self.stdscr.addstr(y, x, "[Continue...]")
self.stdscr.getch()
```

### Data Pattern
```python
# ✅ Correct - Return values
damage, flavor = player.deal_damage(cow)

# ❌ Wrong - Side effects
player.deal_damage(cow)  # prints to stdout
```
```

**Length**: ~80 lines, quick reference format

---

### .claude/CODE_PATTERNS.md (Claude - How to Code)
```markdown
# Code Patterns & Best Practices

## UI Patterns

### Show Continuation Prompt
```python
# Always use helper - hides menu, clears prompt area
self.pause_with_prompt("[Continue...]")
```

### Show Message with Pause
```python
self.game_terminal.draw_dialog(message)
self.pause_with_prompt("[Continue...]")
```

### Menu Visibility Rules
- ✅ Show menu: User needs to choose (Attack/Flee)
- ❌ Hide menu: User just acknowledges (Press ENTER)

## Configuration

### Add New Constant
```python
# Add to game_config.py with clear comment
NEW_CONSTANT = 42  # Purpose and usage
```

### Use Helpers
```python
# Use game_helpers.py for shared utilities
from game_helpers import UIHelpers, CombatMessageFormatter
```

## Combat Patterns

### Deal Damage (Returns Values)
```python
damage, flavor = player.deal_damage(cow)
if flavor:
    msg = flavor  # Use flavor text
else:
    msg = f"{player.name} attacks!"
```

### Track Encounters
```python
# destroy_cow() handles this automatically
self.game_instance.destroy_cow()  # Increments counter, checks floor
```

## File Locations
- Constants → game_config.py
- Helpers → game_helpers.py
- User text → draw_dialog() not print()
- Prompts → pause_with_prompt()
```

**Length**: ~50 lines, practical examples

---

## Benefits of This System

### For You (Human)
- **2 files to care about**: README.md + CHANGELOG.md
- **Quick answers**: CHANGELOG tells you what changed
- **No overwhelm**: Everything else hidden away
- **Still searchable**: Can grep .archive/ if needed

### For Claude (AI Sessions)
- **Fast onboarding**: 3 small files in .claude/
- **Context aware**: Knows project state, recent fixes
- **Consistent code**: Follows documented patterns
- **No duplication**: Single source of truth

### For Both
- **Organized**: Clear tier structure
- **Maintainable**: Update CHANGELOG.md after each session
- **Searchable**: Detailed history in .archive/
- **Clean**: Root directory not cluttered

---

## Migration Commands

### Execute This (Safe, 2 minutes)

```bash
# Create structure
mkdir -p .claude .archive/sessions .archive/reviews .archive/planning docs

# Tier 1: Human docs (root)
# Keep: README.md
# Create CHANGELOG.md from recent changes

# Tier 2: Claude docs
cat > .claude/PROJECT_CONTEXT.md << 'EOF'
(paste essential context from above)
EOF

# Consolidate today's work
cat FINAL_QA_FIXES.md > .archive/sessions/2025-11-05-quality-fixes.md
cat MAGIC_NUMBERS_AUDIT.md >> .archive/sessions/2025-11-05-quality-fixes.md

# Tier 3: Archive everything else
mv CODE_REVIEW.md .archive/reviews/
mv MANUAL_QA_CHECKLIST.md .archive/reviews/
mv COMPLETE_SESSION_FIXES.md .archive/sessions/
mv SCREEN_FLOW_FIXES.md .archive/sessions/
mv QA_FIXES_APPLIED.md .archive/sessions/
mv FINAL_SESSION_DOCUMENTATION.md .archive/sessions/
mv FINAL_IMPLEMENTATION_STATUS.md .archive/sessions/
mv migration_log.md .archive/sessions/
mv ROLLBACK_PLAN.md .archive/planning/
mv CONSOLIDATION_ROADMAP.md .archive/planning/
mv UI_MIGRATION_TASKS.md .archive/planning/
mv TEXTUAL_UI_OVERVIEW.md .archive/planning/
mv PROJECT_OVERVIEW.md .archive/planning/
mv REVIEW_INDEX.md .archive/reviews/
mv ISSUES_CHECKLIST.md .archive/reviews/
mv FINAL_STATUS.md .archive/sessions/
mv DOCUMENTATION_INDEX.md .archive/planning/
mv TERMINAL_REQUIREMENTS.md .archive/planning/
mv TESTING.md .archive/planning/
mv TEXTUAL_INSTALL_NOTES.md .archive/planning/

# Clean up source files
rm FINAL_QA_FIXES.md MAGIC_NUMBERS_AUDIT.md

# Test
python3 main.py
```

---

## What You'll Have

**Root directory**:
```
virtual-cow-tipper-text/
├── README.md          ← Quick start (you might read)
├── CHANGELOG.md       ← Recent changes (you might read)
├── main.py
├── (other .py files)
├── .claude/           ← Claude reads on startup
│   ├── PROJECT_CONTEXT.md
│   ├── FIXES_APPLIED.md
│   └── CODE_PATTERNS.md
└── .archive/          ← Searchable history (hidden)
    ├── sessions/      ← Detailed session work
    ├── reviews/       ← Code reviews, testing docs
    └── planning/      ← Planning, migration, rollback
```

**For you**: 2 files that matter
**For Claude**: 3 small context files
**For reference**: Everything archived, searchable

Does this approach work for you? I can execute it right now if you approve!