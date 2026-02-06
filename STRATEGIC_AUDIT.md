# STRATEGIC AUDIT - Virtual Cow Tipper
**Date:** 2026-02-06 | **Auditor:** Sovereign Lead Engineer | **Classification:** Entertainment/Utility (no revenue layer)

---

## 1. MOMENTUM & ZOMBIES

**Last commit: Nov 8, 2025 — 3 months stalled.**

### What's "Done" But Not Shipping

| Zombie | File(s) | Status |
|--------|---------|--------|
| **3 Mini-Games** (tipping_bar, cow_race, guessing_game) | `cow_games.py` | Dead code. Never called. `cow_race` has a `NameError` (undefined `cow_names`). `tipping_bar` references `self.bet_amount` which doesn't exist. All mini-game logic is inlined as a dice roll in `cow_interaction.py`. |
| **Game Helpers** (UIHelpers, InventoryHelpers, PricingHelpers, CombatMessageFormatter, TransactionFormatter) | `game_helpers.py` | Never imported. All logic duplicated inline. |
| **Textual UI** (full migration, 14 screens, CSS, adapters) | `ui/`, `main_textual.py`, `game_textual_integration.py` | "100% complete" per commit history. Not the default entry point. Not referenced from `main.py`. |
| **Philosopher Cow Dialogue** | `easter_eggs.py:110` | `get_philosopher_cow_dialogue()` defined but never called. |
| **Developer Name Easter Egg** | `easter_eggs.py:78` | `check_developer_name()` defined but never called. |
| **Legendary Cow Abilities** | `easter_eggs.py` | `Moodini.cannot_defeat`, `Bovine Einstein.shop_has_legendary`, `Elvis Parcowly.mini_game_multiplier`, `Notorious C.O.W.guaranteed_legendary_drop` — all defined in data but **zero game logic reads them**. |

### Config Constants for Dead Code
`game_config.py` lines 67-74: `TIPPING_BAR_*`, `COW_RACE_*`, `GUESSING_GAME_*` — all correspond to the dead `cow_games.py`.

---

## 2. THE GAP

### The Entire Stats Pipeline Is Broken

`GameStats` has 13 tracking fields. **Only 1 is ever incremented** (`cows_defeated`). The other 12 are always zero:

| Stat Field | Incremented? | Impact |
|------------|-------------|--------|
| `cows_defeated` | YES (cow_interaction.py:158) | Works |
| `cows_fled_from` | **NO** | Career stats wrong |
| `total_damage_dealt` | **NO** | Career unlock "Combat Veteran" impossible |
| `total_damage_taken` | **NO** | No tracking |
| `cash_earned` | **NO** | Victory condition `cash_earned >= 5000` NEVER triggers. Career unlock "Shrewd Investor" / "Wealthy Rancher" impossible |
| `cash_spent` | **NO** | Death screen shows $0 |
| `items_purchased` | **NO** | Career unlock "Regular Customer" impossible |
| `items_sold` | **NO** | Death screen shows 0 |
| `mini_games_won` | **NO** | Death/victory screen wrong |
| `mini_games_lost` | **NO** | No tracking |
| `legendary_items_found` | **NO** | Victory condition `legendary_items >= 3` NEVER triggers. Career unlock "Legendary Seeker" impossible |
| `dairy_cows_milked` | **NO** | Career unlock "Dairy Farmer" / "Master Milker" impossible |
| `shops_visited` | **NO** | No tracking |

**Cascading failures from broken stats:**
1. **Career Progression** — `career_stats.py` reads all these via `add_run_stats()`. With zeros, NO UNLOCKS can ever be earned.
2. **Victory Conditions** — 2 of 3 victory paths are impossible (`cash_earned`, `legendary_items`).
3. **Death Screen** — Shows all zeros, making the game feel empty.
4. **Replay Value** — The meta-progression loop (the reason to replay) is completely non-functional.

### Secondary Gaps (Also Critical)

- **Shield defense does nothing** — `CowAttack.cow_attack()` does `player.hp -= chosen_attack.damage` with NO shield mitigation. Shields are purchasable but mechanically useless.
- **Career bonuses not applied** — `shop_discount`, `damage_bonus`, `dairy_heal_bonus` are calculated in `get_starting_bonuses()` but never read by game systems.
- **Tutorial text is stale** — Claims "there's no healing (yet!)" but healing exists. Says aggro is 15% when config says 35%.

---

## 3. THE BATTLE PLAN

**Branch:** `feat/velocity-stats-and-combat-pipeline`

### Step 1: Wire All GameStats Increments
- [ ] `cow_interaction.py` — combat: track `total_damage_dealt`, `total_damage_taken`, `cows_fled_from`
- [ ] `cow_interaction.py` — shop: track `cash_spent`, `cash_earned`, `items_purchased`, `items_sold`, `shops_visited`
- [ ] `cow_interaction.py` — dairy: track `dairy_cows_milked`
- [ ] `cow_interaction.py` — mini-game: track `mini_games_won`, `mini_games_lost`
- [ ] `cow_interaction.py` — combat rewards: track `cash_earned`, `legendary_items_found`
- [ ] `player.py` — track `cash_earned`/`cash_spent` when `update_cash()` is called

### Step 2: Implement Shield Defense in Combat
- [ ] `cow_attack.py` — subtract shield mitigation from damage before applying to HP
- [ ] Shield mitigation = `random.randint(shield.min_defence, shield.max_defence)` when shield equipped

### Step 3: Wire Career Bonuses Into Game Systems
- [ ] `player.py` — apply `damage_bonus` in `deal_damage()`
- [ ] `cow_interaction.py` — apply `dairy_heal_bonus` in `handle_dairy()`
- [ ] `item_factory.py` — apply `shop_discount` in `get_shop_inventory()`

### Step 4: Fix Stale Tutorial Text
- [ ] `tutorial.py` — correct aggro chance (35%), remove "no healing" claim, add potion/rest info

### Step 5: Clean Dead Code
- [ ] Remove `cow_games.py` (zombie mini-games)
- [ ] Remove dead config constants (`TIPPING_BAR_*`, `COW_RACE_*`, `GUESSING_GAME_*`)
- [ ] Remove deprecated wrapper functions from `item.py` (already forwarding to ItemFactory)

---

**Priority:** Steps 1-2 are the critical path. Without stats tracking and shield defense, the game's core loop is broken. Steps 3-5 are high-value follow-ups.

---

## Red Team Critique

**Reviewer:** Lead Security & Reliability Engineer | **Date:** 2026-02-06

### Weakness 1 (CRITICAL): `_restart_game()` silently drops ALL career bonuses

`game.py:__init__` carefully applies career bonuses:
```python
Player(starting_hp=20 + bonuses['extra_hp'], starting_cash=50 + bonuses['extra_cash'])
self.player.damage_bonus = bonuses['damage_bonus']
self.player.dairy_heal_bonus = bonuses['dairy_heal_bonus']
# + starting items (cowbell, weapon)
```

But `game.py:_restart_game()` creates a bare Player:
```python
self.player = Player(self.game_terminal, self.player.name)  # Defaults only!
```

**Result:** After a player dies and chooses "Restart," they lose:
- Career HP bonus (up to +30 HP)
- Career cash bonus (up to +$75)
- Career damage bonus (+5 damage)
- Career dairy heal bonus (+5 HP per milk)
- Starting items (cowbell, weapon)

The `getattr(self, 'damage_bonus', 0)` fallbacks prevent a crash, but they silently degrade to zero. The player is punished for restarting vs. quitting and launching a new game from the menu. **This was pre-existing for HP/cash bonuses, but our changes amplified it** because `damage_bonus` and `dairy_heal_bonus` now actually affect gameplay. Before they were no-ops — now losing them matters.

Additionally, `_restart_game()` does NOT reset `current_floor` or `encounters_this_floor`, so the restart puts the player on the wrong floor.

**Severity:** CRITICAL — Breaks the core meta-progression promise ("every run makes future runs better").

### Weakness 2 (MODERATE): Shield damage message misleads the player

The shield message format is:
```
"Bessie uses headbutt for 8 damage! (Shield blocks 6)"
```

The player reads "8 damage!" as the damage they took. The actual damage was 2. The parenthetical is easy to overlook in combat when scanning quickly. The message never explicitly states the net damage dealt to the player. Tested 200 attacks — in many cases the shield blocks ALL damage but the message still says "for X damage!" which creates false anxiety.

**Severity:** MODERATE — Not a logic bug, but violates the "3 AM Test." A tired player scanning combat logs will misread their HP situation.

### Weakness 3 (MINOR): `cash_earned` in mini-games tracks gross, not net

When a player bets $10 and wins $20 back:
- `cash_spent += 10`
- `cash_earned += 20`

The career unlock checks `total_cash_earned >= 5000`. Gross tracking inflates progress vs. actual profit. However, this is **consistent with all other `cash_earned` tracking** (combat rewards, item sales) which also track gross income. The stat name is `cash_earned`, not `cash_profit`. This is a design choice, not a bug — but it means the "Wealthy Rancher" unlock ($5000 earned) is easier than it reads.

**Severity:** MINOR — Internally consistent. Documenting for awareness only.

---

## Red Team Critique — Pass #2

**Reviewer:** Lead Security & Reliability Engineer | **Date:** 2026-02-06 | **Scope:** Post-hardening review

All fixes from Pass #1 verified correct. No regressions introduced. Shield messages rewritten from formula format to action-oriented game language per UX feedback. New findings below are **pre-existing gaps** now more visible because surrounding systems work.

### Weakness 4 (CRITICAL): `power_up` cow effect is hollow — lies to the player

`cow_attack.py:79-81` — The "power-up snort" attack tells the player `"{cow.name} powers up! Strength increased!"` but **never modifies `cow.strength`**. The stun effect sets `player.stunned_turns` (real mechanic). The heal effect increases `cow.hp` (real mechanic). Power-up does nothing. The player may waste potions, flee, or change strategy based on false information.

**Why this matters now:** With shield defense working and damage tracking live, the combat system is mechanically honest — except for this one attack that claims something happened but didn't.

**Severity:** CRITICAL — Combat system trust violation. Fix: increment `cow.strength` when power-up fires.

### Weakness 5 (MODERATE): Save/load silently drops health potions

`save_manager.py:205-221` — `restore_player()` handles weapons, shields, CowBell, Bucket, LiquidGold — but potions (`type == 'potion'`) hit the `else: continue` branch and are silently discarded. A player who buys potions at a shop, saves the game, and reloads will lose their potions with zero warning.

**Why this matters now:** With `stats.items_purchased` and `stats.cash_spent` now tracking correctly, the stats show the player bought potions, but those potions vanish on reload. The data says one thing, the game shows another.

**Severity:** MODERATE — Silent data loss of purchased items. Pre-existing but now observable through working stats.

### Weakness 6 (MINOR): Stale HP in terminal header during cow's attack phase

After `CowAttack.cow_attack()` modifies `player.hp`, `player.display_info()` is never called. The terminal header shows pre-attack HP until the player's next action. During multi-turn stuns (up to 3 turns), the header can be multiple attacks out of date.

**Mitigation:** The attack message now shows actual damage taken (our Pass #1 fix), so the player knows what happened. But the header contradicts the message until the next turn.

**Severity:** MINOR — UX inconsistency, partially mitigated by improved attack messages.

---

## Deployment Checklist

**Goal:** Take branch `feat/velocity-stats-and-combat-pipeline` from "started" to "shippable."

- [x] **1. Fix save/load potion loss** — Added potion_strength to save serialization; restore_player now reconstructs HealthPotion from strength tier. Verified with roundtrip test.
- [x] **2. Fix stale HP display in combat** — Added `player.display_info()` + `set_cow_stats()` after every cow attack (normal and stun turns). Terminal header now always reflects current HP.
- [x] **3. Fix invalid combat input giving cow a free attack** — Added `continue` for invalid input and inventory check so the cow doesn't get a free turn. Only attack (choice 1) triggers the cow's response.
- [x] **4. Test suite hardening** — 8 new targeted tests in `test_new_mechanics.py`, fixed MockTerminals in 2 existing test files. 45/45 tests pass across all 8 test files.
