# Changelog

Recent changes to Virtual Cow Tipper.

---

## 2025-11-05 - Quality & Organization Improvements

### Documentation Consolidation ✅
- Reduced 21 .md files → 2 in root (README.md + CHANGELOG.md)
- Created `.claude/` directory (4 context files for AI sessions)
- Archived all detailed docs to `.archive/` (organized by type)
- Implemented self-enforcing documentation rules
- Result: Clean root directory, no future .md sprawl

---

## 2025-11-05 - Quality & Organization Improvements

### Fixed
- Encounter counter now increments correctly (#1 → #2 → #3...)
- Floor progression system working (advances every 10 encounters)
- Floor/encounter progress now saves and loads correctly
- Interactive inventory system (view, select, equip, use items)
- Screen state preservation (inventory returns to previous screen)
- Menu hiding during continuation prompts (28 instances fixed)
- Flavor text now appears in dialogue area (not terminal output)
- Combat dialogue persists between turns (no more blank screens)
- Prompt text overlap eliminated ("[Continue...]cow's turn...]" bug)
- Removed redundant menu options (inventory handles everything)
- Potion.use() no longer prints to stdout, uses PLAYER_MAX_HP constant
- Load game screen now uses curses (was using print/input)
- Load game intro customized for loaded games (shows current status, not "Starting")
- Rest with full HP now preserves screen state (like empty inventory)
- Save and quit screen now uses curses with proper menu (was using print/input)
- Shop now allows multiple purchases (was exiting after first purchase)
- Shop menu now uses dynamic indexing (handles 4-5 items correctly)
- Shop restores greeting after each action (proper state management)
- Sell items menu now works correctly (was broken due to indexing)
- equip() now updates header display immediately

### Added
- `game_helpers.py` - 6 utility classes for code reuse
- 68 new constants to `game_config.py` (cow attacks, items, prompts)
- `advance_floor()` method - automatic floor progression
- Interactive inventory with item actions menu
- Screen state preservation system (save/restore dialogue)
- `.claude/` directory - documentation system for AI context
- Dev save file system (`saves/dev_save.example.json`) for testing
- Active dev save (`saves/game_save.json`) ready with 4 items
- Clearer dice game instructions ("two dice" instead of "2d6")

### Changed
- `player.deal_damage()` now returns `(damage, flavor_text)` tuple
- `check_inventory()` fully refactored for curses compatibility
- All continuation prompts now use `pause_with_prompt()` pattern
- `destroy_cow()` handles encounter tracking automatically
- Combat menu simplified (4 → 3 options)
- Encounter menu simplified (5 → 4 options)
- Main menu simplified (5 → 4 options, removed Career Progress)
- Tip menu simplified (3 → 2 options, removed legacy quick tip)
- Menu option renamed: "save and quit" → "quit"

### Technical
- Removed stdout/curses mixing (all text via draw_dialog)
- Standardized pause behavior across 31 locations
- Created self-enforcing documentation rules (.claude/RULES.md)
- Consolidated 21 .md files into organized structure

---

## 2025-11-04 - UI Polish & QA Testing

### Fixed
- Screen layout improvements
- Menu refresh timing
- Dialogue area rendering
- Welcome screen cleanup

---

## 2025-11-01 - Textual UI Migration Complete

### Added
- Textual UI as alternative to Curses
- Dual UI support (switch with --textual flag)
- UI abstraction layer
- 14 Textual screens implemented

### Status
- Migration 100% complete
- Both UIs fully functional

---

**For detailed session notes**: See `.archive/sessions/YYYY-MM-DD-topic.md`
**For code patterns**: See `.claude/CODE_PATTERNS.md`
