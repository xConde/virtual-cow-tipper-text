"""
Tutorial system for first-time players.
"""


def show_tutorial():
    """Display tutorial for new players."""
    print("\n" + "="*60)
    print("WELCOME TO VIRTUAL COW TIPPER!")
    print("="*60)

    print("""
This game is about tipping cows, but it's not that simple...

THE BASICS:
-----------
• You encounter random cows in a field
• Each cow has a MOOD (upset/neutral/friendly)
• Each cow belongs to a PACK (1-6)

YOUR ACTIONS MATTER:
-------------------
• Win against a pack → Future cows from that pack like you more
• Lose to a pack → Future cows from that pack become hostile
• This creates STRATEGY - which packs will you befriend?

COW TYPES:
----------
• AGGRESSIVE (15% chance) - Fight or flee!
• SHOP KEEPER (15% chance) - Buy and sell items
• DAIRY COW (5% chance) - Milk them if you have a bucket
• REGULAR COW (default) - Tip them to play mini-games

PROGRESSION:
-----------
• Earn cash by defeating cows and winning mini-games
• Buy better weapons and shields at shops
• Cows get stronger as YOU get stronger
• The game adapts to your progression!

TIPS FOR SUCCESS:
----------------
• Don't anger all the packs - you'll face only hostile cows!
• Buy a Cow Bell early - helps find dairy cows
• Sell old equipment when you find better gear
• Friendly shop cows pay 70% for items, upset only pay 50%
• Watch your HP - there's no healing (yet!)

Ready to start your bovine adventure?
""")

    input("Press Enter to begin...")


def show_first_encounter_tip():
    """Show tip before first cow encounter."""
    print("\n" + "-"*60)
    print("FIRST ENCOUNTER!")
    print("-"*60)
    print("""
You're about to meet your first cow!

REMEMBER:
• Arrow keys to navigate menus
• Numbers for quick selection
• ESC anytime to pause and see controls

Good luck, and don't get trampled!
""")
    input("Press Enter to continue...")
