# Manual QA Checklist - Virtual Cow Tipper

## Automated Tests: ✅ 12/12 PASSED (100%)

All automated tests pass. Now perform manual gameplay testing to verify user experience.

---

## 🎮 GAME START & WELCOME FLOW

### Test 1.1: First Time Player
- [ ] Run `python3 main.py`
- [ ] Select "New Game"
- [ ] Answer "n" to tutorial
- [ ] Enter player name
- [ ] **VERIFY**: Welcome screen appears in dialogue area with game explanation
- [ ] **VERIFY**: Shows starting stats (HP, Cash)
- [ ] **VERIFY**: Prompt says "[Press any key to begin...]"
- [ ] Press key
- [ ] **VERIFY**: Welcome screen clears (no duplicate showing)

### Test 1.2: Developer Easter Egg
- [ ] Start new game with name "ed" (or other developer name)
- [ ] **VERIFY**: Developer cow easter egg shows
- [ ] Press Enter
- [ ] **VERIFY**: Welcome screen appears (not skipped)
- [ ] **VERIFY**: Welcome clears properly after key press

---

## 🐮 ENCOUNTER INTRODUCTION SYSTEM

### Test 2.1: First Encounter - Aggressive Cow
- [ ] After welcome, wait for first encounter
- [ ] **VERIFY**: Screen shows in dialogue area (lines 6-18):
  ```
  === FLOOR 1 - FIRST ENCOUNTER ===

  [Cow Name] (Aggressive Cow - AGGRESSIVE)
  HP: [X] | STR: [Y]

  [Cow's approach/personality text]

  [Cow Name] looks hostile and ready to fight!

  Controls: Arrow keys/Numbers | SPACE/ENTER to select
  ```
- [ ] **VERIFY**: Cow's stats show in top-right header
- [ ] **VERIFY**: Prompt says "[Press any key to continue...]"
- [ ] Press key
- [ ] **VERIFY**: Introduction STAYS VISIBLE in dialogue area
- [ ] **VERIFY**: Menu appears below (lines 22-27)
- [ ] **VERIFY**: Can see cow name and stats while choosing action

### Test 2.2: First Encounter - Shop Keeper
- [ ] Restart game if first cow is aggressive
- [ ] Wait for shop keeper encounter
- [ ] **VERIFY**: Shows "Shop Keeper - SHOP KEEPER"
- [ ] **VERIFY**: Shows cow's mood
- [ ] **VERIFY**: Personality text visible
- [ ] **VERIFY**: Menu appears with intro visible

### Test 2.3: First Encounter - Neutral Cow
- [ ] Find neutral cow encounter
- [ ] **VERIFY**: Shows "Peaceful Cow - NEUTRAL"
- [ ] **VERIFY**: Shows mood
- [ ] **VERIFY**: Personality/approach text visible
- [ ] **VERIFY**: Behavior description present

### Test 2.4: Subsequent Encounters
- [ ] Complete first encounter
- [ ] Wait for second encounter
- [ ] **VERIFY**: Shows "=== FLOOR X - ENCOUNTER #2 ==="
- [ ] **VERIFY**: Shows cow profile (concise, no control tips)
- [ ] **VERIFY**: Personality text visible
- [ ] **VERIFY**: Menu works same as first

---

## ⚔️ COMBAT SYSTEM

### Test 3.1: Combat Start
- [ ] Encounter aggressive cow
- [ ] See cow profile introduction
- [ ] Select "1. approach the cow"
- [ ] **VERIFY**: Shows "=== COMBAT BEGINS ==="
- [ ] **VERIFY**: Combat message in dialogue area
- [ ] **VERIFY**: Combat menu appears immediately

### Test 3.2: Combat Actions - Attack
- [ ] Select "1. Attack"
- [ ] **VERIFY**: Damage message shows
- [ ] **VERIFY**: Cow HP decreases (check top-right)
- [ ] **VERIFY**: Cow attacks back
- [ ] **VERIFY**: Damage message shows
- [ ] **VERIFY**: Player HP decreases (check top-left)
- [ ] **VERIFY**: Pause "[Press any key to continue...]"
- [ ] **VERIFY**: Screen refreshes, menu appears again

### Test 3.3: Combat Actions - Check Inventory
- [ ] Select "2. Check inventory"
- [ ] **VERIFY**: Inventory displays
- [ ] **VERIFY**: Can return to combat menu

### Test 3.4: Combat Actions - Use Item
- [ ] Have health potion in inventory
- [ ] Select "3. Use an item from inventory"
- [ ] **VERIFY**: Item menu shows
- [ ] Select health potion
- [ ] **VERIFY**: HP restored
- [ ] **VERIFY**: Potion removed from inventory

### Test 3.5: Combat Actions - Flee
- [ ] Select "4. Flee"
- [ ] **VERIFY**: Shows "=== FLED FROM COMBAT ==="
- [ ] **VERIFY**: Message: "You escaped safely, but gained no rewards"
- [ ] **VERIFY**: Pause for acknowledgment
- [ ] **VERIFY**: Returns to main game loop (new encounter)

### Test 3.6: Combat Victory
- [ ] Defeat a cow (reduce HP to 0)
- [ ] **VERIFY**: Shows "=== VICTORY ==="
- [ ] **VERIFY**: Shows cash reward amount
- [ ] **VERIFY**: Shows item drop (if any)
- [ ] **VERIFY**: Cow's defeat dialogue shows
- [ ] **VERIFY**: Pause for acknowledgment
- [ ] **VERIFY**: Screen refreshes cleanly

### Test 3.7: Combat Death
- [ ] Let cow reduce player HP to 0
- [ ] **VERIFY**: Game over screen shows
- [ ] **VERIFY**: Shows final stats
- [ ] **VERIFY**: Career stats updated
- [ ] **VERIFY**: Asks if want to restart

### Test 3.8: Stun Mechanic
- [ ] Get stunned by cow's special attack
- [ ] **VERIFY**: Shows "ed is stunned and cannot act!"
- [ ] **VERIFY**: Shows turns remaining
- [ ] **VERIFY**: Cow attacks automatically
- [ ] **VERIFY**: Pause before next turn
- [ ] **VERIFY**: Screen refreshes cleanly

---

## 🛒 SHOP SYSTEM

### Test 4.1: Shop Discovery
- [ ] Encounter shop keeper
- [ ] **VERIFY**: Introduction shows shop keeper info
- [ ] Select "1. approach the cow"
- [ ] **VERIFY**: Shopkeeper greeting shows
- [ ] **VERIFY**: Shop menu appears with items

### Test 4.2: Purchase Item
- [ ] Select item to purchase (with enough cash)
- [ ] **VERIFY**: Shows "=== PURCHASE COMPLETE ==="
- [ ] **VERIFY**: Shows item purchased and price
- [ ] **VERIFY**: Shows cash before and after
- [ ] **VERIFY**: Shows "Total Purchases This Visit: 1 item(s)"
- [ ] **VERIFY**: Shows "Total Spent So Far: $[amount]"
- [ ] **VERIFY**: Pause "[Press any key to continue shopping...]"
- [ ] **VERIFY**: Returns to shop menu

### Test 4.3: Purchase Multiple Items
- [ ] Buy 2-3 items in same shop visit
- [ ] **VERIFY**: Each shows running total
- [ ] **VERIFY**: "Total Purchases This Visit" increments
- [ ] **VERIFY**: "Total Spent So Far" accumulates

### Test 4.4: Insufficient Funds
- [ ] Try to buy item you can't afford
- [ ] **VERIFY**: Shows "You don't have enough cash"
- [ ] **VERIFY**: Pause to read error
- [ ] **VERIFY**: Returns to shop menu

### Test 4.5: Sell Item
- [ ] Select "4. Sell items" (with items in inventory)
- [ ] **VERIFY**: Shows "=== Sell Items ==="
- [ ] **VERIFY**: Lists sellable items with prices
- [ ] Select item to sell
- [ ] **VERIFY**: Shows "=== SALE COMPLETE ==="
- [ ] **VERIFY**: Shows item sold and price
- [ ] **VERIFY**: Shows cash before and after
- [ ] **VERIFY**: Shows "Total Sales This Visit"
- [ ] **VERIFY**: Pause to review

### Test 4.6: Sell No Items
- [ ] Try to sell with empty inventory
- [ ] **VERIFY**: Shows "You have no items to sell"
- [ ] **VERIFY**: Pause to read
- [ ] **VERIFY**: Returns to shop menu

### Test 4.7: Leave Shop (After Transactions)
- [ ] Buy and/or sell items
- [ ] Select "5. Leave the shop"
- [ ] **VERIFY**: Shows "=== LEAVING [SHOP NAME]'S SHOP ==="
- [ ] **VERIFY**: Shows "Shop Visit Summary:"
- [ ] **VERIFY**: Lists all purchases with prices
- [ ] **VERIFY**: Shows "Total Spent: $[amount]"
- [ ] **VERIFY**: Lists all sales (if any)
- [ ] **VERIFY**: Shows "Total Earned: $[amount]"
- [ ] **VERIFY**: Shows starting vs ending cash
- [ ] **VERIFY**: Shows net profit or net spent
- [ ] **VERIFY**: Shopkeeper farewell message
- [ ] **VERIFY**: "You leave the shop and continue your journey"
- [ ] **VERIFY**: Pause "[Press any key to continue your adventure...]"

### Test 4.8: Leave Shop (Just Browsing)
- [ ] Enter shop
- [ ] Don't buy or sell anything
- [ ] Select "5. Leave the shop"
- [ ] **VERIFY**: Shows "You browsed the shop but didn't buy or sell anything"
- [ ] **VERIFY**: No transaction lists shown
- [ ] **VERIFY**: Shopkeeper farewell
- [ ] **VERIFY**: Pause before continuing

---

## 🥛 DAIRY COW SYSTEM

### Test 5.1: Dairy Cow with Bucket
- [ ] Get bucket from shop
- [ ] Encounter dairy cow
- [ ] **VERIFY**: Introduction shows "Dairy Cow" type
- [ ] **VERIFY**: Personality text shows
- [ ] Interaction happens (auto or via approach)
- [ ] **VERIFY**: Shows "=== Dairy Cow Milked ==="
- [ ] **VERIFY**: Shows HP restored amount
- [ ] **VERIFY**: Shows current HP
- [ ] **VERIFY**: Pause to read HP gain
- [ ] **VERIFY**: Screen refreshes

### Test 5.2: Dairy Cow without Bucket
- [ ] Encounter dairy cow without bucket
- [ ] **VERIFY**: Introduction shows dairy cow info
- [ ] **VERIFY**: Shows "=== DAIRY COW ENCOUNTERED ==="
- [ ] **VERIFY**: Shows "you don't have a bucket"
- [ ] **VERIFY**: Cow's dialogue shows
- [ ] **VERIFY**: Pause to read
- [ ] **VERIFY**: Returns to game loop

---

## 🎲 TIP/MINI-GAME SYSTEM

### Test 6.1: Play Mini-Game
- [ ] Encounter neutral cow
- [ ] Select "1. Tip [name] (play mini-game)"
- [ ] Choose bet amount
- [ ] **VERIFY**: Mini-game plays
- [ ] **VERIFY**: Result shows (win or loss)
- [ ] **VERIFY**: Cash updates appropriately

### Test 6.2: Quick Tip (Success)
- [ ] Have enough cash
- [ ] Select "2. Quick tip $[amount]"
- [ ] **VERIFY**: Shows "=== Quick Tip Given ==="
- [ ] **VERIFY**: Shows amount tipped
- [ ] **VERIFY**: Shows profit gained
- [ ] **VERIFY**: Pause to review
- [ ] **VERIFY**: Screen refreshes

### Test 6.3: Quick Tip (Insufficient Funds)
- [ ] Try quick tip without enough cash
- [ ] **VERIFY**: Shows error message
- [ ] **VERIFY**: Shows "Come back when you have more cash!"
- [ ] **VERIFY**: Pause to read
- [ ] **VERIFY**: Returns to game

### Test 6.4: Leave Neutral Cow
- [ ] Select "3. Leave"
- [ ] **VERIFY**: Shows leave message
- [ ] **VERIFY**: Shows "The cow seems disappointed but understanding"
- [ ] **VERIFY**: Pause for acknowledgment
- [ ] **VERIFY**: Returns to game loop

---

## 📦 INVENTORY & ITEMS

### Test 7.1: Check Inventory (Empty)
- [ ] Start fresh game
- [ ] Select "3. check inventory"
- [ ] **VERIFY**: Shows inventory (should have starting potions)
- [ ] **VERIFY**: Returns to menu

### Test 7.2: Check Inventory (With Items)
- [ ] Acquire some items
- [ ] Check inventory
- [ ] **VERIFY**: All items listed
- [ ] **VERIFY**: Returns to menu

### Test 7.3: Use Item from Main Menu
- [ ] Have consumable item
- [ ] Select "4. use an item from inventory"
- [ ] **VERIFY**: Item list shows
- [ ] Use item
- [ ] **VERIFY**: Effect applies (HP restored, etc.)
- [ ] **VERIFY**: Item removed from inventory

### Test 7.4: Equip Weapon
- [ ] Acquire weapon
- [ ] **VERIFY**: Prompted to equip
- [ ] Equip weapon
- [ ] **VERIFY**: "Weapon: [name]" shows in top-left
- [ ] **VERIFY**: Attack damage increases

### Test 7.5: Equip Shield
- [ ] Acquire shield
- [ ] Equip shield
- [ ] **VERIFY**: "Shield: [name]" shows in top-left
- [ ] **VERIFY**: Damage taken decreases

---

## 💾 SAVE/LOAD SYSTEM

### Test 8.1: Save Game
- [ ] Play for a few encounters
- [ ] Select "5. save and quit"
- [ ] **VERIFY**: Save confirmation
- [ ] **VERIFY**: Game exits cleanly

### Test 8.2: Load Game
- [ ] Run `python3 main.py`
- [ ] Select "Continue"
- [ ] **VERIFY**: Save file found
- [ ] **VERIFY**: Game loads with correct stats
- [ ] **VERIFY**: Player name restored
- [ ] **VERIFY**: HP and cash restored
- [ ] **VERIFY**: Inventory restored
- [ ] **VERIFY**: Floor number restored

### Test 8.3: No Save File
- [ ] Delete save file
- [ ] Try to continue
- [ ] **VERIFY**: Shows "No save file found"
- [ ] **VERIFY**: Returns to main menu

---

## 🎯 NAVIGATION & CONTROLS

### Test 9.1: Arrow Key Navigation
- [ ] Use UP arrow to move menu selection
- [ ] **VERIFY**: Selection highlights move
- [ ] Use DOWN arrow
- [ ] **VERIFY**: Selection wraps around

### Test 9.2: Number Key Selection
- [ ] Press "1" key
- [ ] **VERIFY**: Immediately selects option 1
- [ ] Try other numbers
- [ ] **VERIFY**: All number keys work

### Test 9.3: ENTER Key
- [ ] Navigate to an option with arrows
- [ ] Press ENTER
- [ ] **VERIFY**: Option selects

### Test 9.4: SPACE Bar
- [ ] Navigate to an option
- [ ] Press SPACE
- [ ] **VERIFY**: Option selects

### Test 9.5: ESC Key (Pause Menu)
- [ ] Press ESC during game
- [ ] **VERIFY**: Pause menu appears
- [ ] **VERIFY**: Can continue, view help, or quit

---

## 🎨 SCREEN RENDERING

### Test 10.1: No Bleed-Through
- [ ] Play game in terminal with prior text/content
- [ ] **VERIFY**: No Claude Code interface visible
- [ ] **VERIFY**: No previous terminal text showing
- [ ] **VERIFY**: Clean game screen

### Test 10.2: Separator Line
- [ ] Check any game screen
- [ ] **VERIFY**: Separator shows as clean line (not `---...`)
- [ ] **VERIFY**: Spans full width properly

### Test 10.3: Dialogue Area
- [ ] Check encounter screen
- [ ] **VERIFY**: Dialogue shows in lines 6-18 area
- [ ] **VERIFY**: Full messages visible (not truncated)
- [ ] **VERIFY**: Left-aligned layout

### Test 10.4: Menu Area
- [ ] Check any menu
- [ ] **VERIFY**: Menu shows in lines 22-27 area
- [ ] **VERIFY**: All options visible
- [ ] **VERIFY**: Selection highlighting works

### Test 10.5: Screen Transitions
- [ ] Move through several encounters
- [ ] **VERIFY**: Clean transitions (no artifacts)
- [ ] **VERIFY**: No old text remaining
- [ ] **VERIFY**: Each screen clear and readable

---

## 🔄 COMPLETE GAMEPLAY FLOWS

### Test 11.1: Combat Victory Chain
- [ ] Defeat 3 cows in a row
- [ ] **VERIFY**: Each victory shows proper message
- [ ] **VERIFY**: Cash accumulates
- [ ] **VERIFY**: Stats update
- [ ] **VERIFY**: New encounters show correct encounter number

### Test 11.2: Shop → Combat → Shop
- [ ] Visit shop, buy item
- [ ] Encounter aggressive cow
- [ ] Defeat cow
- [ ] Visit another shop
- [ ] **VERIFY**: Each flow works correctly
- [ ] **VERIFY**: Stats stay consistent
- [ ] **VERIFY**: No message bleed between flows

### Test 11.3: Multiple Actions in One Encounter
- [ ] Encounter cow
- [ ] Check inventory
- [ ] Rest (skip cow)
- [ ] **VERIFY**: Both actions work
- [ ] **VERIFY**: Cow wanders off after rest
- [ ] **VERIFY**: New encounter starts

### Test 11.4: Inventory → Combat → Victory
- [ ] Check inventory before combat
- [ ] Approach aggressive cow
- [ ] Defeat cow
- [ ] **VERIFY**: Smooth flow between all actions
- [ ] **VERIFY**: Inventory still accessible after

---

## 🎪 EDGE CASES

### Test 12.1: Zero Cash
- [ ] Spend all cash
- [ ] Try to buy item
- [ ] **VERIFY**: "Insufficient funds" works
- [ ] Try to quick tip
- [ ] **VERIFY**: Error message shows
- [ ] **VERIFY**: Game doesn't crash

### Test 12.2: Full Inventory
- [ ] Fill inventory to capacity (20 items)
- [ ] Try to acquire more items
- [ ] **VERIFY**: Handles gracefully

### Test 12.3: Low HP Combat
- [ ] Enter combat with low HP (< 5)
- [ ] **VERIFY**: Can still attack
- [ ] **VERIFY**: Can flee
- [ ] **VERIFY**: Death handling works if HP reaches 0

### Test 12.4: Rapid Key Presses
- [ ] Rapidly press keys in menus
- [ ] **VERIFY**: No crashes
- [ ] **VERIFY**: Selections work correctly
- [ ] **VERIFY**: No duplicate actions

### Test 12.5: Long Play Session
- [ ] Play for 10+ encounters
- [ ] **VERIFY**: No performance degradation
- [ ] **VERIFY**: No memory issues
- [ ] **VERIFY**: Screen clearing still works
- [ ] **VERIFY**: All messages still display correctly

---

## 📊 CAREER & PROGRESSION

### Test 13.1: Career Stats
- [ ] From main menu, select "Career Progress"
- [ ] **VERIFY**: Shows total runs
- [ ] **VERIFY**: Shows cows defeated
- [ ] **VERIFY**: Shows high score
- [ ] **VERIFY**: Can return to menu

### Test 13.2: Floor Advancement
- [ ] Complete enough encounters to advance floor
- [ ] **VERIFY**: Floor number increases (check top display)
- [ ] **VERIFY**: Encounter counter resets
- [ ] **VERIFY**: Difficulty increases appropriately

---

## 🐛 REGRESSION TESTS

### Test 14.1: Shop Leave Bug (Original Issue)
- [ ] Visit shop
- [ ] Buy one item
- [ ] Press key to continue shopping
- [ ] Select "5. Leave the shop"
- [ ] **VERIFY**: Does NOT show previous purchase message
- [ ] **VERIFY**: Shows proper exit summary instead

### Test 14.2: Combat Log Bug
- [ ] Engage in combat
- [ ] Get hit by cow
- [ ] **VERIFY**: No error "name 'combat_log' is not defined"
- [ ] **VERIFY**: Attack message displays

### Test 14.3: Welcome Screen Duplicate
- [ ] Start new game
- [ ] **VERIFY**: Welcome shows ONCE
- [ ] **VERIFY**: After pressing key, does NOT show again
- [ ] **VERIFY**: Next screen is encounter intro, not duplicate welcome

### Test 14.4: Encounter Intro Visibility
- [ ] Start game, get to first encounter
- [ ] **VERIFY**: Encounter intro appears with cow profile
- [ ] Press key
- [ ] **VERIFY**: Intro STAYS VISIBLE (not erased)
- [ ] **VERIFY**: Menu appears below intro
- [ ] **VERIFY**: Can read cow stats while choosing

---

## 📝 QA SIGN-OFF

**Tester**: _____________
**Date**: _____________
**Game Version**: Virtual Cow Tipper - Post Session Fixes
**Branch**: feature/textual-ui

### Critical Issues Found:
_____________________________________________
_____________________________________________

### Non-Critical Issues:
_____________________________________________
_____________________________________________

### Overall Assessment:
- [ ] Ready for play
- [ ] Needs minor fixes
- [ ] Needs major fixes

### Sign-Off:
- [ ] All critical systems working
- [ ] No crashes during testing
- [ ] UX is clear and understandable
- [ ] Game is enjoyable to play

---

**AUTOMATED TEST RESULTS**: ✅ 12/12 PASSED (100%)
**MANUAL TESTING**: [ ] Complete [ ] In Progress [ ] Not Started

---

## Quick Test (5 minutes)

For rapid verification, test this minimal flow:

1. ✅ Start game → Welcome shows → Clears properly
2. ✅ First encounter → Cow profile shows → Stays visible
3. ✅ Menu appears → Can select option → Intro still visible
4. ✅ Approach cow → Combat or shop works
5. ✅ Complete action → Next encounter works
6. ✅ No crashes, all text visible, controls work

If all 6 pass → Game is working!