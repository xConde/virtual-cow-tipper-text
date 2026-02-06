# STRATEGIC AUDIT — Pass #2
**Date:** 2026-02-06 | **Auditor:** Sovereign Lead Engineer | **Classification:** Entertainment/Utility (no revenue layer)

**Context:** Pass #1 fixed the stats pipeline, shield defense, career bonuses, combat loop, save/load, and dead code. This pass addresses the remaining architectural debt.

---

## 1. MOMENTUM & ZOMBIES

### Codebase Vital Signs

| Metric | Value |
|--------|-------|
| Runtime Python files | 20 files, ~4,900 lines |
| Zombie Python files | 26 files (UI module, orphan entry points, root-level test debris) |
| Documentation/archive | ~18,700 lines (3.8x larger than runtime code) |
| Test files (organized, in `tests/`) | 9 files — these are HEALTHY |
| Test files (scattered in root) | 10+ files — these are DEBRIS from Textual UI migration |

### Zombie Inventory

| Category | Files | Lines (est.) | Status |
|----------|-------|-------------|--------|
| **Textual UI module** | `ui/` (11 files: textual_app.py, adapters/, interfaces/, game_ui_bridge.py, ui_factory.py, ascii_art.py, performance_config.py) | ~3,400 | "100% complete" per commit history. Never wired to `main.py`. Dead on arrival. |
| **Orphan entry points** | `main_textual.py`, `main_ui.py`, `game_textual_integration.py` | ~1,000 | Alternate launchers for the dead Textual UI. |
| **Root test debris** | `test_async.py`, `test_complete_game.py`, `test_comprehensive.py`, `test_game_connections.py`, `test_integration.py`, `test_textual_app.py`, `test_textual_game.py`, `test_ui_abstraction.py`, `test_ui_modes.py`, `comprehensive_qa_test.py` | ~2,800 | All test the dead Textual UI or were one-off verification scripts. |
| **Verification scripts** | `verify_textual_app.py`, `verify_ui_structure.py`, `profile_baseline.py`, `run_tests.py` | ~500 | Migration-era scaffolding, never used again. |
| **Legendary cow abilities** | Data in `easter_eggs.py` | 0 (code never written) | 5 legendary cows with special abilities defined as data. Zero game logic reads them: `cannot_defeat`, `guaranteed_legendary_drop`, `mini_game_multiplier`, `shop_has_legendary`, all `dialogue_*` fields. |
| **Philosopher cow dialogue** | `easter_eggs.py:get_philosopher_cow_dialogue()` | ~18 | Function defined, never called by any runtime code. |
| **Developer name easter egg** | `easter_eggs.py:check_developer_name()` | ~15 | Only called from orphaned `main_textual.py` — not from `main.py`. |

---

## 2. THE GAP

### The repo is 60% dead weight, and the rarest encounters in the game are cosmetic shells.

**Gap A: Repository hygiene blocks "shippable."** You cannot ship a project where the root directory has 10 orphaned test files, an 11-file UI module that was never connected, 3 alternate entry points that go nowhere, and 18,700 lines of docs for 4,900 lines of code. A contributor opening this repo sees chaos, not a game.

**Gap B: Legendary cows are the game's crown jewels — and they're hollow.** Legendary cows are a 0.1% encounter. They should be the most memorable moment in a run. Instead, they spawn with basic stats and a custom approach message. That's it. The data defines:
- **Moodini** — "cannot be defeated" (can be defeated like any other cow)
- **Bovine Einstein** — "shop has legendary items" (shop generates standard items)
- **Elvis Parcowly** — "mini-game multiplier" (mini-games pay standard rates)
- **The Notorious C.O.W.** — "guaranteed legendary drop" (uses standard 15% drop chance)
- **All 5** — custom `dialogue_intro`/`dialogue_victory` text (never displayed)

**Gap C: Two easter eggs defined but not wired.** `get_philosopher_cow_dialogue()` and `check_developer_name()` exist in code but are never called from the active `main.py` path.

---

## 3. THE BATTLE PLAN

### Step 1: Nuke the zombies — DONE
- [x] Delete entire `ui/` directory (11 files — dead Textual UI)
- [x] Delete orphan entry points: `main_textual.py`, `main_ui.py`, `game_textual_integration.py`
- [x] Delete root-level test debris (10 files)
- [x] Delete verification/profiling scripts: `verify_textual_app.py`, `verify_ui_structure.py`, `profile_baseline.py`, `run_tests.py`
- [x] Delete stale docs: `docs/` (Textual migration architecture)
- [x] Clean `.gitignore` of Textual-specific entries no longer needed
- **Result:** 33 files deleted, -9,728 lines

### Step 2: Implement legendary cow abilities — DONE
- [x] **Moodini** — `cannot_defeat`: Escapes at 0 HP with partial cash, no kill credit. Fixed `is_aggro: True`.
- [x] **Bovine Einstein** — `shop_has_legendary`: Forces legendairy weapon in shop inventory.
- [x] **Elvis Parcowly** — `mini_game_multiplier`: 3x payout on mini-game wins + `dialogue_graceful` on win.
- [x] **Notorious C.O.W.** — `guaranteed_legendary_drop`: 100% drop, forced legendairy rarity. Fixed `is_aggro: True`.
- [x] **The Cowculator** — Triple cash via `cash_multiplier` (already wired in `_create_legendary_cow`).
- [x] **All 5** — `dialogue_intro` on encounter, `dialogue_victory`/`dialogue_escape` on resolution. `{player_name}` formatted.
- [x] Removed broken `print()` from `EasterEggRewards.legendary_cow_found()` (bypassed curses).
- [x] Added `legendary_data` field to `CowProperties` dataclass, threaded through `Cow.__init__` and `_create_legendary_cow`.

### Step 3: Wire orphaned easter eggs — DONE
- [x] `get_philosopher_cow_dialogue()` — Triggers in `game.py:player_turn()` for neutral encounters (0.5% chance).
- [x] `check_developer_name()` — Called from `main.py` name input. Gives legendary starting weapon + developer encounter message.

### Step 4: Test and verify — DONE
- [x] 53/53 tests pass (up from 45 — 8 new mechanic tests from Pass #1)
- [x] All 18 runtime modules import cleanly (no orphan references)
- [x] Clean working tree after commit

---

**All steps complete. Pass #2 is closed.**
