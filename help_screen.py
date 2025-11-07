"""
In-game help and controls screen.
"""

HELP_TEXT = """
╔══════════════════════════════════════════════════════════════════════╗
║                    VIRTUAL COW TIPPER - HELP                         ║
╠══════════════════════════════════════════════════════════════════════╣

CONTROLS
--------
  ↑/↓ or W/S    - Navigate menus
  1-9           - Quick select menu options
  Enter/Space   - Confirm selection
  ESC           - Pause menu


GOAL
----
Survive by maintaining your HP and Cash. Encounter cows, earn money,
buy better equipment, and build your reputation with different cow packs.


COW TYPES
---------
  Aggressive    - Combat! Fight or flee. Victory earns cash.
  Shop Keeper   - Buy items (weapons, shields, tools). Sell your loot!
  Dairy Cow     - Requires bucket to milk. Produces valuable Liquid Gold.
  Regular Cow   - Tip to play mini-games for cash rewards.


PACK REPUTATION (Important!)
-----------------------------
Each cow belongs to one of 6 packs. Your actions affect future encounters:
  • Win/befriend pack  → Future cows from that pack are friendlier
  • Lose/anger pack    → Future cows from that pack are more hostile

Strategy: Choose which packs to befriend!


COMBAT
------
  Your Damage: 2-8 base + weapon damage + (cash ÷ 25)
  Cow Attacks: 10 different attack types
  Effects: Some attacks can stun you for multiple turns!

  Actions:
    1. Attack       - Deal damage to cow
    2. Inventory    - View, equip weapons/shields, use potions
    3. Flee         - Escape (damages pack reputation)


ITEMS
-----
  Weapons: Dagger → Godsword (10 types)
  Shields: Buckler → Aegis (10 types)
  Rarity: Common → Uncommon → Magic → Rare → Legendairy

  Special Tools:
    Cow Bell  - Increases dairy cow encounter chance (5% → 15%)
    Bucket    - Required to milk dairy cows


SHOP
----
  Buy: Prices scale with your wealth. Upset cows charge 2x!
  Sell: Get 50-70% of item value (mood-dependent)
    • Friendly: 70%
    • Neutral:  60%
    • Upset:    50%


MINI-GAMES
----------
  Tipping Bar   - Stop arrow at target (timing challenge)
  Cow Race      - Pick a racing cow (50% win chance)
  Guessing Game - Guess cow's number (hot/cold hints)


TIPS
----
  • Befriend at least one pack early (easier encounters)
  • Buy cow bell for easy dairy farming
  • Sell excess weapons/shields for cash
  • Friendly shop cows give best deals
  • Use 'rest' to heal +10 HP between encounters
  • Open inventory anytime to equip better gear


Press any key to return...
╚══════════════════════════════════════════════════════════════════════╝
"""


def show_help(game_terminal):
    """Display help screen in game terminal."""
    game_terminal.stdscr.clear()
    lines = HELP_TEXT.split('\n')

    for i, line in enumerate(lines[:game_terminal.HEIGHT - 1]):
        try:
            game_terminal.stdscr.addstr(i, 0, line[:game_terminal.WIDTH - 1])
        except:
            pass  # Ignore if line too long

    game_terminal.stdscr.refresh()
    game_terminal.stdscr.getch()  # Wait for keypress
    game_terminal.stdscr.clear()
