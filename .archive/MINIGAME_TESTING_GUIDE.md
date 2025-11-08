# Enhanced Mini-Game - Testing Guide

**Feature**: Bet selection, personality variations, rematch mechanics
**Status**: Ready to test
**Time**: 10-15 minutes for complete testing

---

## How to Test

### Setup

**1. Use dev save** (has $500 cash):
```bash
cp saves/dev_save.example.json saves/game_save.json
python3 main.py
# Select "2. Continue"
```

**2. Find a friendly cow** (for easier testing):
- Keep encountering cows until you find one that's not aggressive/shop
- Friendly cows say things like "Hello friend!" in intro
- Select "1. Play mini-game"

---

## Test Scenarios

### Scenario 1: Bet Selection (Basic)

**Steps**:
1. Encounter friendly cow
2. Select "Play mini-game"
3. **You should see**:
   ```
   Choose Your Bet
   [Cow] seems friendly - lower stakes!

   How much do you want to wager?

   Select bet:
     1. Cautious ($2-3) - Play it safe
     2. Normal ($4-6) - Standard bet
     3. Bold ($8-12) - High risk, high reward!
     4. Cancel
   ```

**✅ Verify**:
- Bet amounts shown in dollars
- Friendly cow has lower bets (~20% less)
- All options visible
- Can select with 1/2/3 or arrows

**4. Try cancelling**:
- Select "4. Cancel"
- Should return to encounter menu
- Cow should still be there
- No money lost

---

### Scenario 2: Friendly Cow (Easier Odds)

**Steps**:
1. Find friendly cow
2. Select "Play mini-game"
3. Choose "Normal" bet
4. **Game intro should say**:
   ```
   Dice Rolling Game!

   [Cow]: "I'll go easy on you!"
   Bet: $4

   Roll two dice - get 6 or higher to win!
   (6-12 wins, 2-5 loses)
   ```

**✅ Verify**:
- Win threshold is **6+** (not 7+)
- Cow says friendly dialogue
- Bet amount shown

**5. Roll the dice** (press ENTER twice)
- Any roll 6-12 = WIN
- Roll 2-5 = LOSE

---

### Scenario 3: Bold Bet - Win

**Steps**:
1. Find any cow
2. Select "Play mini-game"
3. Choose "Bold" bet (highest amount)
4. Roll and **win** (6+ friendly, 7+ others)

**✅ Verify**:
- Deducts bold amount (2x normal)
- Win shows: "Profit: +$[bold amount]"
- Cash increases by profit amount
- Returns to next encounter
- **Check reputation**: Should give +2.5 to pack

---

### Scenario 4: Normal Bet - Lose - Decline Rematch

**Steps**:
1. Play mini-game with normal bet
2. **Lose** (roll under threshold)
3. **You should see**:
   ```
   🎲 You Rolled: 3 + 2 = 5 🎲

   You Lose

   Not lucky this time.
   Lost: $4

   [Press any key...]
   ```

**4. Press key, then see rematch offer**:
   ```
   Rematch Offer
   [Cow] doesn't look so friendly anymore...

   [Cow]: 'Want to win it back?'

   Double-or-nothing: Bet $4 again!
   Win: Get your $4 back (break even)
   Lose: Lose $4 more (double loss)

   Your decision:
     1. Rematch (bet $4 again)
     2. Walk away (accept loss)
   ```

**5. Select "Walk away"**

**✅ Verify**:
- Cash is down by bet amount
- Returns to next encounter
- Cow mood didn't change in header yet (will on next cow)

---

### Scenario 5: Lose - Rematch - Win (Break Even)

**Steps**:
1. Play mini-game
2. Lose first game (down $X)
3. Rematch offered - select "Rematch"
4. **Cow header should change**: "[Cow] | Angry"
5. Roll rematch and **WIN**

**✅ Verify**:
- Cash back to original amount (±$0)
- Shows: "Final result: Break even (±$0)"
- Cow mood showed "Angry" during rematch
- Returns to next encounter

---

### Scenario 6: Lose - Rematch - Lose (Double Loss)

**Steps**:
1. Play mini-game
2. Lose first game (down $4)
3. Select "Rematch"
4. Roll rematch and **LOSE**

**✅ Verify**:
- Shows: "Total lost: $8" (2x bet)
- Cash is down by double the bet
- Message says "[Cow] takes your money"
- Heavy reputation penalty

---

### Scenario 7: Lose But Can't Afford Rematch

**Setup**: Spend money until you have less than bet amount

**Steps**:
1. Play with all your remaining cash
2. Lose
3. **Should see**:
   ```
   Out of Cash!
   [Cow] doesn't look so friendly anymore...

   [Cow] wanted a rematch, but you can't afford it.

   You walk away defeated...
   ```

**✅ Verify**:
- No rematch menu (just message)
- Returns to next encounter
- Reputation penalty applied

---

### Scenario 8: Upset Cow (Higher Bets)

**Steps**:
1. Find upset cow (might need to lose to a pack first)
2. Select "Play mini-game"
3. **Bet selection should show**:
   ```
   Choose Your Bet
   [Cow] wants higher stakes!

   ...bets are 30% higher than friendly cow
   ```

**✅ Verify**:
- Bets ~30% higher
- Cow says: "You better not waste my time!"
- Win threshold still 7+ (no easier)

---

### Scenario 9: Select Unaffordable Bet

**Setup**: Have limited cash (e.g., $5)

**Steps**:
1. Play mini-game
2. Try to select "Bold" (needs $8+)
3. **Should see**:
   ```
   Insufficient Funds

   Need $8, you have $5

   Please choose a different bet or cancel.
   ```

**✅ Verify**:
- Returns to encounter menu (no loop)
- Cow still there
- Can play again with lower bet

---

## Quick Test Checklist

**Basic Functionality**:
- [ ] Bet selection menu appears
- [ ] Can choose cautious/normal/bold
- [ ] Can cancel bet selection
- [ ] Unaffordable bets show error
- [ ] Game plays with selected bet

**Personality System**:
- [ ] Friendly cow: Lower bets, win on 6+
- [ ] Neutral cow: Standard bets, win on 7+
- [ ] Upset cow: Higher bets, win on 7+
- [ ] Personality dialogue shows

**Win Path**:
- [ ] Win first try → Profit shown
- [ ] No rematch offered after win
- [ ] Reputation scales with bet size
- [ ] Cash increases correctly

**Loss Path**:
- [ ] Lose → Rematch offered
- [ ] Can decline rematch
- [ ] Reputation penalty applies

**Rematch Path**:
- [ ] Rematch uses same bet amount
- [ ] Cow mood shifts to "Angry"
- [ ] Win rematch → Break even (±$0)
- [ ] Lose rematch → Double loss shown
- [ ] Can't afford rematch → Handled gracefully

**Screen Layout**:
- [ ] All text in dialogue area (not stdout)
- [ ] Menu hidden during pauses
- [ ] Menu visible during choices
- [ ] Consistent with other game screens

---

## Expected Results

### Cash Examples

**Cautious bet ($2), WIN**:
- Before: $500
- After: $502 (+$2 profit)

**Bold bet ($8), WIN**:
- Before: $500
- After: $508 (+$8 profit)

**Normal bet ($4), LOSE, no rematch**:
- Before: $500
- After: $496 (-$4 loss)

**Normal bet ($4), LOSE, REMATCH WIN**:
- Before: $500
- During: $496 (after first loss)
- During: $492 (after rematch bet)
- After: $500 (break even after rematch win)

**Normal bet ($4), LOSE, REMATCH LOSE**:
- Before: $500
- After: $492 (-$8 total, double loss)

---

## Known Issues to Watch For

**Should NOT happen** (if these occur, it's a bug):
- ❌ print() or safe_print() output visible
- ❌ Menu visible during "Press any key" pauses
- ❌ Infinite loops in bet selection
- ❌ Cash calculation wrong
- ❌ Rematch offered after win
- ❌ Three or more rematches
- ❌ Reputation not updating
- ❌ Cow not ending encounter

---

## Success Criteria

**Feature is working if**:
- ✅ Can select from 3 bet tiers
- ✅ Friendly cows easier (6+ to win)
- ✅ Rematch works after loss
- ✅ Cash flow correct in all paths
- ✅ Screens follow established patterns
- ✅ No bugs or crashes

---

**Estimated Testing Time**: 10-15 minutes to test all scenarios
**Priority**: Test scenarios 1-6 minimum (covers main flows)
**Optional**: Scenarios 7-9 (edge cases)
