# Enhanced Mini-Game System - Feature Specification

**Status**: Ready for implementation
**Estimated Time**: 30-45 minutes
**Complexity**: Medium
**Impact**: High (significantly expands gameplay depth)

---

## Overview

Transform the simple dice game into a dynamic betting system with personality-driven variations and rematch mechanics.

**Current**: Fixed bet, roll once, done
**Enhanced**: Choose bet amount, cow personality affects odds, rematch option after loss

---

## Feature Components

### 1. Bet Selection System

**Before Mini-Game Starts**:
```
Dice Rolling Game!

Annie challenges you to a game of chance.

Choose your bet:
  > 1. Cautious ($2) - Play it safe <
    2. Normal ($4) - Standard bet
    3. Bold ($8) - Risk it all!
    4. Cancel

Roll two dice - get 7 or higher to win!
```

**Bet Tiers**:
- **Cautious**: 50% of cow.req_amount (lower risk, lower reward)
- **Normal**: 100% of cow.req_amount (current behavior)
- **Bold**: 200% of cow.req_amount (high risk, high reward)

**Edge Cases**:
- If player cash < bold bet: Show bold option as "(Not enough cash)"
- If player cash < normal bet: Only show cautious option
- If player cash < cautious bet: Show "insufficient funds" message, back to menu

---

### 2. Personality-Based Variations

**Cow Mood Affects Odds and Bets**:

**Friendly Cow**:
- Base bet reduced by 20%: `req_amount * 0.8`
- Win threshold lowered: Need 6+ instead of 7+ (easier to win)
- Dialogue: "I'll go easy on you!" / "Just having fun!"

**Neutral Cow**:
- Base bet normal: `req_amount * 1.0`
- Win threshold standard: 7+
- Dialogue: "Standard rules!" / "May the odds be ever..."

**Upset Cow**:
- Base bet increased by 30%: `req_amount * 1.3`
- Win threshold standard: 7+ (no advantage)
- Dialogue: "You better have cash!" / "High stakes, human!"

---

### 3. Rematch System (After Loss Only)

**Loss Flow**:
```
🎲 You Rolled: 2 + 3 = 5 🎲

You Lose

Not lucky this time.
Lost: $4

Annie seems frustrated with your luck...

Rematch Options:
  > 1. Double-or-nothing (bet $4 again) <
    2. Walk away (accept loss)
```

**Rematch Mechanics**:
- **Only offered after LOSS** (not after win)
- **Cow mood shifts**: Becomes "upset" (if wasn't already)
- **Same bet amount**: Can't change bet during rematch
- **One rematch only**: If lose again, no third chance
- **Win rematch**: Get original bet back (break even, no profit)
- **Lose rematch**: Lose both bets (double loss)

**Rematch Dialogue Examples**:
- Friendly → Upset: "That's not how this goes! One more round!"
- Neutral → Upset: "I don't like losing. Play again!"
- Already Upset: "You're going to lose again!" (stays upset)

---

### 4. Complete Flow Examples

#### Example 1: Bold Bet, Win First Try
```
1. Choose bet: "Bold ($8)"
2. Roll: 7 + 5 = 12
3. WIN!
4. Profit: +$8
5. Cow happy (+1.5 reputation)
6. Done (no rematch offered)
```

#### Example 2: Normal Bet, Lose, Win Rematch
```
1. Choose bet: "Normal ($4)"
2. Roll: 2 + 3 = 5
3. LOSE (down $4)
4. Rematch offered
5. Choose: "Double-or-nothing"
6. Cow mood → upset
7. Roll: 8 + 4 = 12
8. WIN rematch!
9. Get $4 back (break even)
10. Cow neutral reputation (0)
```

#### Example 3: Cautious Bet, Lose, Lose Rematch
```
1. Choose bet: "Cautious ($2)"
2. Roll: 3 + 2 = 5
3. LOSE (down $2)
4. Rematch offered
5. Choose: "Double-or-nothing"
6. Roll: 4 + 1 = 5
7. LOSE rematch!
8. Total loss: $4 (both bets)
9. Cow angry (-1.5 reputation)
10. Done (no third chance)
```

#### Example 4: Insufficient Cash
```
1. Player has $3
2. Cautious: $2 ✅
3. Normal: $4 ❌ (grayed out)
4. Bold: $8 ❌ (grayed out)
5. Can only bet cautious or cancel
```

---

## Implementation Details

### Code Changes Required

#### File: cow_interaction.py

**New Method: `_select_bet_amount()`**:
```python
def _select_bet_amount(self, base_amount: int) -> Optional[int]:
    """
    Let player choose bet amount.

    Returns:
        Bet amount, or None if cancelled
    """
    # Adjust base for personality
    if self.cow.mood == 'friendly':
        base_amount = int(base_amount * 0.8)
    elif self.cow.mood == 'upset':
        base_amount = int(base_amount * 1.3)

    cautious = int(base_amount * 0.5)
    normal = base_amount
    bold = int(base_amount * 2.0)

    # Build menu with affordability check
    bet_msg = f"Choose Your Bet\n\n{self.cow.name} is ready to play.\n"

    menu_items = []
    if self.player.cash >= cautious:
        menu_items.append(f"1. Cautious (${cautious}) - Play it safe")

    if self.player.cash >= normal:
        menu_items.append(f"2. Normal (${normal}) - Standard bet")
    else:
        menu_items.append(f"2. Normal (${normal}) - Not enough cash")

    if self.player.cash >= bold:
        menu_items.append(f"3. Bold (${bold}) - Risk it all!")
    else:
        menu_items.append(f"3. Bold (${bold}) - Not enough cash")

    menu_items.append(f"4. Cancel")

    self.game_terminal.draw_dialog(bet_msg)
    choice = self.game_terminal.get_menu_choice(menu_items, "Select bet amount:")

    # Map choice to bet amount
    bets = [cautious, normal, bold]
    if choice <= 3:
        bet_amount = bets[choice - 1]
        if self.player.cash >= bet_amount:
            return bet_amount
        else:
            # Show error, try again
            error_msg = f"Insufficient Funds\n\nNeed ${bet_amount}, have ${self.player.cash}"
            self.game_terminal.draw_dialog(error_msg)
            self.pause_with_prompt("[Press any key...]")
            return None
    else:
        return None  # Cancelled
```

**New Method: `_offer_rematch()`**:
```python
def _offer_rematch(self, bet_amount: int, original_mood: str) -> bool:
    """
    Offer rematch after loss.

    Returns:
        True if player wants rematch, False otherwise
    """
    # Cow mood shifts to upset
    mood_shift_msg = ""
    if original_mood == 'friendly':
        mood_shift_msg = f"\n{self.cow.name} doesn't look so friendly anymore..."
    elif original_mood == 'neutral':
        mood_shift_msg = f"\n{self.cow.name} is getting upset..."

    rematch_msg = (
        f"Rematch Offer{mood_shift_msg}\n\n"
        f"{self.cow.name}: 'Want to win it back?'\n\n"
        f"Double-or-nothing for ${bet_amount}!"
    )

    self.game_terminal.draw_dialog(rematch_msg)

    menu_items = [
        f"1. Rematch (bet ${bet_amount} again)",
        "2. Walk away (accept loss)"
    ]

    choice = self.game_terminal.get_menu_choice(menu_items, "Your decision:")

    # Shift cow mood for rematch
    if choice == 1:
        self.cow.mood = 'upset'
        self.game_terminal.set_cow_stats(f"{self.cow.name} | upset (angry)")
        return True

    return False
```

**Modified Method: `handle_tip_or_leave()`**:
```python
if choice == 1:
    original_mood = self.cow.mood

    # Step 1: Select bet amount
    bet_amount = self._select_bet_amount(self.cow.req_amount)
    if bet_amount is None:
        # Cancelled, return to menu
        return

    # Adjust win threshold for friendly cows
    win_threshold = 6 if self.cow.mood == 'friendly' else 7

    # Step 2: Explain game with personality
    if self.cow.mood == 'friendly':
        flavor = "I'll go easy on you!"
    elif self.cow.mood == 'upset':
        flavor = "You better not lose my time!"
    else:
        flavor = "May the odds be with you!"

    game_msg = (
        f"Dice Rolling Game!\n\n"
        f"{self.cow.name}: \"{flavor}\"\n"
        f"Bet: ${bet_amount}\n\n"
        f"Roll two dice - get {win_threshold} or higher to win!\n"
        f"({win_threshold}-12 wins, 2-{win_threshold-1} loses)"
    )
    self.game_terminal.draw_dialog(game_msg)
    self.pause_with_prompt("[Press ENTER to roll the dice...]")

    # Step 3: Roll dice
    rolling_msg = (
        f"Rolling the dice...\n\n"
        f"🎲 🎲\n\n"
        f"The dice tumble..."
    )
    self.game_terminal.draw_dialog(rolling_msg)
    self.pause_with_prompt("[Press ENTER to see result...]")

    self.player.update_cash(-bet_amount)
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    total = die1 + die2
    won = total >= win_threshold

    # Step 4: Show result
    if won:
        # WIN - Pay out
        profit = bet_amount
        self.player.update_cash(bet_amount * 2)

        win_msg = (
            f"🎲 You Rolled: {die1} + {die2} = {total} 🎲\n\n"
            f"YOU WIN!\n\n"
            f"The dice favor you!\n"
            f"Profit: +${profit}"
        )
        self.game_terminal.draw_dialog(win_msg)

        # Higher score for bigger bets
        score = 0.5 + (bet_amount / self.cow.req_amount)  # 1.0 to 2.5
        self.cow.likeliness += score
        self.game_instance.update_cow_scores(self.cow, score)

        self.pause_with_prompt("[Press any key to continue...]")

    else:
        # LOSS - Offer rematch
        loss_msg = (
            f"🎲 You Rolled: {die1} + {die2} = {total} 🎲\n\n"
            f"You Lose\n\n"
            f"Not lucky this time.\n"
            f"Lost: ${bet_amount}"
        )
        self.game_terminal.draw_dialog(loss_msg)
        self.pause_with_prompt("[Press any key...]")

        # Offer rematch
        wants_rematch = self._offer_rematch(bet_amount, original_mood)

        if wants_rematch:
            # REMATCH
            rematch_msg = (
                f"Rematch!\n\n"
                f"{self.cow.name} deals the dice again.\n"
                f"Bet: ${bet_amount}\n\n"
                f"You need {win_threshold}+ to win it back!"
            )
            self.game_terminal.draw_dialog(rematch_msg)
            self.pause_with_prompt("[Press ENTER to roll...]")

            # Roll again
            self.player.update_cash(-bet_amount)
            die1 = random.randint(1, 6)
            die2 = random.randint(1, 6)
            total = die1 + die2
            rematch_won = total >= win_threshold

            if rematch_won:
                # WIN REMATCH - Break even
                self.player.update_cash(bet_amount * 2)

                rematch_win_msg = (
                    f"🎲 Rematch Roll: {die1} + {die2} = {total} 🎲\n\n"
                    f"REMATCH WIN!\n\n"
                    f"You got your ${bet_amount} back!\n"
                    f"Total: Break even (±$0)"
                )
                self.game_terminal.draw_dialog(rematch_win_msg)

                # Neutral score (no gain/loss)
                self.game_instance.update_cow_scores(self.cow, 0)

                self.pause_with_prompt("[Press any key to continue...]")

            else:
                # LOSE REMATCH - Double loss
                rematch_loss_msg = (
                    f"🎲 Rematch Roll: {die1} + {die2} = {total} 🎲\n\n"
                    f"REMATCH LOST!\n\n"
                    f"{self.cow.name} takes your money.\n"
                    f"Total Lost: ${bet_amount * 2}"
                )
                self.game_terminal.draw_dialog(rematch_loss_msg)

                # Heavy penalty
                score = -1.5
                self.cow.likeliness += score
                self.game_instance.update_cow_scores(self.cow, score)

                self.pause_with_prompt("[Press any key to continue...]")

        else:
            # Declined rematch
            score = -0.5
            self.cow.likeliness += score
            self.game_instance.update_cow_scores(self.cow, score)
```

---

## Configuration Constants

**Add to game_config.py**:
```python
# ============================================================================
# ENHANCED MINI-GAME - Betting and Rematch System
# ============================================================================

# Bet Multipliers
MINI_GAME_CAUTIOUS_MULTIPLIER = 0.5   # 50% of base
MINI_GAME_NORMAL_MULTIPLIER = 1.0     # 100% of base
MINI_GAME_BOLD_MULTIPLIER = 2.0       # 200% of base

# Personality Adjustments
MINI_GAME_FRIENDLY_BET_REDUCTION = 0.8   # 20% cheaper
MINI_GAME_FRIENDLY_WIN_THRESHOLD = 6      # Easier (6+ instead of 7+)
MINI_GAME_UPSET_BET_INCREASE = 1.3        # 30% more expensive
MINI_GAME_NEUTRAL_WIN_THRESHOLD = 7       # Standard

# Scoring Adjustments
MINI_GAME_WIN_SCORE_BASE = 0.5
MINI_GAME_WIN_SCORE_PER_BET_MULTIPLIER = 1.0  # +score based on bet size
MINI_GAME_LOSS_SCORE = -0.5
MINI_GAME_REMATCH_WIN_SCORE = 0.0     # Break even
MINI_GAME_REMATCH_LOSS_SCORE = -1.5   # Heavy penalty
```

---

## Edge Cases Handled

### Financial Edge Cases
1. **Insufficient for all bets**: Only show cautious (if affordable) or error
2. **Insufficient for cautious**: Show "not enough cash" message, back to menu
3. **Lose first game, can't afford rematch**: Don't offer rematch
4. **After rematch, bankrupt**: Game continues (might have $0)

### Gameplay Edge Cases
1. **Win first try**: No rematch offered (only after loss)
2. **Decline rematch**: Accept loss, continue normally
3. **Rematch win**: Break even (±$0), neutral reputation
4. **Rematch loss**: Double loss, heavy reputation penalty
5. **Friendly cow rematch**: Shifts to upset, but win threshold stays easy (6+)

### Mood Edge Cases
1. **Already upset cow**: Stays upset during rematch (can't get more upset)
2. **Friendly rematch**: Becomes upset but might say "I'm disappointed in you"
3. **Neutral rematch**: Becomes upset, standard reaction

---

## Score Balancing

**Win Scores** (scaled by bet risk):
- Cautious win: +1.0 score (0.5 base + 0.5 for bet)
- Normal win: +1.5 score (0.5 base + 1.0 for bet)
- Bold win: +2.5 score (0.5 base + 2.0 for bet)

**Loss Scores**:
- First loss: -0.5 score
- Decline rematch: -0.5 score (same as first loss)
- Rematch win: 0.0 score (neutral, broke even)
- Rematch loss: -1.5 score (heavy penalty)

**Rationale**: Bigger risks earn bigger reputation gains

---

## UI/UX Flow

### Happy Path (Win)
```
Screen 1: Bet Selection
  - Shows 3-4 options based on cash
  - Clear bet amounts and rewards

Screen 2: Game Rules
  - Shows bet amount, win threshold
  - Personality dialogue

Screen 3: Rolling
  - Animation/anticipation

Screen 4: Win Result
  - Shows roll, profit
  - Encouraging message
  - Done
```

### Rematch Path (Loss → Rematch → Win)
```
Screen 1-3: Same as above

Screen 4: Loss Result
  - Shows roll, loss amount
  - "Not lucky this time"

Screen 5: Rematch Offer
  - Cow mood shift message
  - Double-or-nothing option

Screen 6: Rematch Roll
  - Same dice game
  - Tension: "Get it back or lose double"

Screen 7: Rematch Win
  - Shows roll, break even
  - Relief message
```

---

## Testing Checklist

### Bet Selection
- [ ] Cautious bet shows correct amount (50% of base)
- [ ] Normal bet shows correct amount (100% of base)
- [ ] Bold bet shows correct amount (200% of base)
- [ ] Friendly cow: bets reduced by 20%
- [ ] Upset cow: bets increased by 30%
- [ ] Unaffordable bets grayed out/disabled
- [ ] Cancel returns to main menu

### First Game
- [ ] Friendly cow: wins on 6+ (easier)
- [ ] Neutral/Upset: wins on 7+ (standard)
- [ ] Win: Correct profit calculation
- [ ] Win: No rematch offered
- [ ] Loss: Rematch offered
- [ ] Loss: Correct loss amount

### Rematch System
- [ ] Only offered after loss (not win)
- [ ] Cow mood shifts to upset
- [ ] Same bet amount (can't change)
- [ ] Win rematch: Get original bet back (±$0)
- [ ] Lose rematch: Lose both bets (double)
- [ ] Decline rematch: Accept loss, continue
- [ ] No third chance (only one rematch)

### Reputation
- [ ] Win first try: Positive score (scaled by bet)
- [ ] Lose once: -0.5 score
- [ ] Decline rematch: -0.5 score
- [ ] Win rematch: 0.0 score (neutral)
- [ ] Lose rematch: -1.5 score (heavy penalty)

### Financial
- [ ] Player cash updates correctly
- [ ] Can't bet more than player has
- [ ] Rematch requires cash for second bet
- [ ] If bankrupt after loss, no rematch offered

---

## Files to Modify

1. **game_config.py** (+15 lines)
   - Add betting multipliers
   - Add personality adjustments
   - Add score values

2. **cow_interaction.py** (+120 lines estimated)
   - Add `_select_bet_amount()` method (~40 lines)
   - Add `_offer_rematch()` method (~30 lines)
   - Modify `handle_tip_or_leave()` choice == 1 block (~50 lines)
   - Update to use new constants

3. **.claude/FIXES_APPLIED.md** (update)
   - Add entry for enhanced mini-game system

4. **CHANGELOG.md** (update when done)
   - Document new feature in "Added" section

---

## Personality Dialogue Variations (Optional Enhancement)

### Win Reactions
- **Friendly**: "Well played! You're pretty good at this!"
- **Neutral**: "Fair and square. Well done."
- **Upset**: "Hmph. Beginner's luck."

### Loss Reactions
- **Friendly**: "Aw, better luck next time!"
- **Neutral**: "The house wins this round."
- **Upset**: "Hah! I knew it!"

### Rematch Offers
- **Friendly → Upset**: "That's not how this was supposed to go! One more!"
- **Neutral → Upset**: "I want a chance to win more. Play again!"
- **Already Upset**: "Double or nothing! You're going down!"

---

## Implementation Order

**Phase 1: Bet Selection** (15 min)
1. Add constants to game_config.py
2. Implement `_select_bet_amount()` method
3. Test bet selection works with cash checking

**Phase 2: Personality Integration** (10 min)
1. Adjust bet amounts based on mood
2. Adjust win threshold for friendly cows
3. Add personality dialogue to game intro

**Phase 3: Rematch System** (20 min)
1. Implement `_offer_rematch()` method
2. Integrate rematch into loss flow
3. Handle mood shifts
4. Test rematch win/loss paths

**Phase 4: Testing & Polish** (10 min)
1. Test all bet tiers
2. Test all personality variations
3. Test rematch scenarios
4. Test edge cases (bankrupt, etc.)

**Total**: ~55 minutes (estimated)

---

## Success Criteria

**Feature is complete when**:
- [ ] Player can choose bet amount (3 tiers)
- [ ] Friendly cows have easier games (6+ to win)
- [ ] Upset cows have higher bets
- [ ] Loss offers rematch (one time only)
- [ ] Rematch works correctly (win = break even, loss = double)
- [ ] All edge cases handled (insufficient cash, etc.)
- [ ] No crashes or bugs
- [ ] UX is clear and intuitive

---

## Risk Assessment

**Low Risk**:
- Self-contained feature (only affects mini-game)
- Doesn't touch combat, shop, or core systems
- Can be tested independently

**Medium Complexity**:
- Multiple branching paths (bet selection, win/loss, rematch)
- State management (mood shifts, bet tracking)
- Edge cases to handle

**High Value**:
- Significantly increases mini-game depth
- Adds strategic decisions
- Personality system more impactful
- Rematch creates dramatic moments

---

**Status**: Fully specified, ready for implementation
**Next Session**: Implement this feature following this spec
**Documentation**: This file serves as complete implementation guide
