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

### Step 1: Nuke the zombies
- [ ] Delete entire `ui/` directory (11 files — dead Textual UI)
- [ ] Delete orphan entry points: `main_textual.py`, `main_ui.py`, `game_textual_integration.py`
- [ ] Delete root-level test debris (10 files)
- [ ] Delete verification/profiling scripts: `verify_textual_app.py`, `verify_ui_structure.py`, `profile_baseline.py`, `run_tests.py`
- [ ] Delete stale docs: `docs/` (Textual migration architecture), `.archive/` session logs if they exist outside git history
- [ ] Clean `.gitignore` of Textual-specific entries no longer needed

### Step 2: Implement legendary cow abilities
- [ ] **Moodini** — `cannot_defeat`: If cow HP reaches 0, cow "escapes" instead. Player gets partial rewards but no kill credit.
- [ ] **Bovine Einstein** — `shop_has_legendary`: Force at least one legendary-rarity item in shop inventory.
- [ ] **Elvis Parcowly** — `mini_game_multiplier`: Apply 2x payout multiplier to mini-game wins.
- [ ] **Notorious C.O.W.** — `guaranteed_legendary_drop`: Override drop chance to 100% on defeat.
- [ ] **All 5** — Display `dialogue_intro` on encounter and `dialogue_victory`/`dialogue_escape` on resolution.

### Step 3: Wire orphaned easter eggs
- [ ] `get_philosopher_cow_dialogue()` — Trigger during neutral cow encounters (low % chance)
- [ ] `check_developer_name()` — Call from `main.py` name input, apply developer bonus

### Step 4: Test and verify
- [ ] Run full 45-test suite, add tests for legendary abilities
- [ ] Verify all imports clean (no orphan references)
- [ ] Final `git status` — clean working tree

---

**Priority:** Step 1 first — you can't assess what's left until the noise is gone. Steps 2-3 are the feature work. Step 4 locks it.
