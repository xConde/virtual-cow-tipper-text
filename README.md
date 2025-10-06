# Virtual Cow Tipper

```
      \   ^__^
       \  (oo)\_______
          (__)\       )\/\
              ||----w |
              ||     ||
```

> *"What's your beef? Let's talk tips."*

## What is this?

Ever wondered what would happen if cows ran shops, hosted game shows, and occasionally tried to trample you? Wonder no more.

This is a text-based RPG where you wander fields tipping cows. Some cows are friendly and will play mini-games with you. Some run shops (yes, really). Some are **very** upset and want to fight. Your actions build reputation with different cow packs, making future encounters easier... or harder.

It's absurd, it's punny (but not *too* punny), and it's oddly engaging.

**The short version:**
- Tip cows, fight cows, buy stuff from cows
- Unlock permanent bonuses across runs
- Try not to get trampled
- See if you can find the legendary cow named "The Cowculator"

## Getting Started

**Requirements:** Python 3.10+, a terminal

**Running it:**
```bash
python3 main.py
```

That's it. No dependencies, no setup. Just cows.

---

## Why would I play this?

Good question! Here's what makes it fun:

**Strategic Depth:** The pack reputation system means your choices matter. Anger Pack 3? Future Pack 3 cows will be hostile. Befriend Pack 5? They'll help you out.

**Meta-Progression:** Every run counts. Defeat 25 cows total (across all runs) and unlock +10 starting HP forever. Losses aren't wasted - they're progress toward unlocks.

**Actual Balance:** This game was unwinnable in 2023 (no healing = death spiral). Now it's actually beatable with potions, rest mechanics, and fair combat.

**Decent Writing:** 100+ absurd cow scenarios (cow attempting stand-up comedy, cow building time machine, cow giving TED talks). Plus dry humor that doesn't rely on puns every sentence.

---

## The Technical Stuff

## How to Play

### Goal
Survive by earning cash and maintaining your HP. Encounter various cows, each with unique personalities and challenges. Build your reputation with different cow packs to influence future encounters.

### Controls

**Menu Navigation:**
- Arrow keys (↑/↓) - Navigate menus
- Number keys (1-4) - Quick select options
- Enter - Confirm selection
- ESC - Pause menu

### Game Mechanics

#### Cow Encounters
Each cow belongs to one of 6 packs and has a mood (upset/neutral/friendly):

- **Aggressive Cows** - Fight or flee. Victory earns cash and improves pack reputation
- **Shop Cows** - Buy weapons, shields, and tools. Mood affects prices
- **Dairy Cows** - Milk with a bucket to obtain valuable Liquid Gold
- **Regular Cows** - Tip to play mini-games for rewards

#### Pack Reputation System
- **Win against a pack** - Future cows from that pack are friendlier
- **Lose to a pack** - Future cows from that pack are more hostile
- **Strategic depth** - Choose which packs to befriend

#### Combat
- **Base damage** - Scales with your cash (2-8 + cash/25)
- **Weapon damage** - Scaled by rarity (common → legendairy)
- **Shield defense** - Reduces incoming damage
- **Stun effects** - Some cow attacks stun you for multiple turns

#### Items & Rarity
- **5 Rarity Tiers:** Common, Uncommon, Magic, Rare, Legendairy
- **10 Weapon Types:** Dagger → Godsword
- **10 Shield Types:** Buckler → Aegis
- **Special Tools:** Cow Bell (attract dairy cows), Bucket (milk cows)

#### Shop Mechanics
- **Buy items** - Prices scale with your wealth
- **Sell items** - Get 50-70% value (mood-dependent)
- **Mood matters** - Upset cows charge 2x, Friendly cows pay more

#### Mini-Games
- **Tipping Bar** - Timing challenge, stop arrow at target
- **Cow Race** - Pick a cow and watch them race
- **Guessing Game** - Guess the cow's favorite number (hot/cold hints)

### Win/Lose Conditions

**Game Over:**
- HP reaches 0
- Cash reaches 0

**Victory:** (To be implemented)
- Defeat 50 cows
- Earn $5000
- Collect a full legendairy set

### Features

**The Game Loop:**
- Encounter random cows (some friendly, some... not)
- Fight aggressive cows for cash and items
- Buy healing potions and equipment at cow-run shops
- Play mini-games (or skip them if you're grinding)
- Every 10 encounters = floor complete → choose a reward

**The Hook:**
- Pack reputation system (strategic depth)
- Meta-progression (11 unlocks to earn)
- 3 ways to win (combat, economy, or collection)
- Save/load your progress
- Easter eggs (0.1% chance for legendary named cows!)

**The Vibe:**
- Absurdist humor (cows doing human things)
- Dry wit with occasional sharp puns
- Self-aware comedy
- Text-based but polished

## Game Stats

- **1,911 lines of gameplay code**
- **28 unit tests** - All passing
- **6 cow packs** to befriend or anger
- **92 cow names**
- **26 random interruption events**
- **3 mini-games**
- **20 weapon/shield types**
- **Infinite replay value**

## Development

### Run Tests
```bash
python3 run_tests.py
```

All 28 tests should pass.

### Project Structure
```
virtual-cow-tipper-text/
├── main.py              # Entry point
├── game.py              # Game loop and state
├── player.py            # Player stats and actions
├── cow.py               # Cow generation and behavior
├── cow_interaction.py   # Interaction handlers (combat, shop, dairy, tip)
├── cow_attack.py        # Combat system
├── cow_games.py         # Mini-games
├── item.py              # Item classes
├── item_factory.py      # Item generation
├── models.py            # Dataclasses
├── game_config.py       # All game balance constants
├── dialogue_manager.py  # Centralized dialogue system
├── terminal/            # Curses UI
│   ├── game_terminal.py
│   ├── pause_menu.py
│   └── dialog_history.py
├── assets/
│   └── context.py       # All dialogue text
└── tests/               # Unit tests
```

## Credits

Built in 2023, finished in 2025.
All 558 lines of cow dialogue lovingly handcrafted.

## License

Personal project - Play it, don't sell it.

---

*"I'm feeling legen-dairy today. Want to share the good mood?"* - Friendly Cow, probably

---

**Start your bovine adventure:** `python3 main.py`
