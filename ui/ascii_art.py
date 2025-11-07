"""
ASCII art assets for Virtual Cow Tipper Textual UI.
Provides cow art, logos, and other visual elements.
"""

# Cow ASCII art variations
COW_NORMAL = """
        (oo)
  /------\/
 / |    ||
*  ||----||
   ^^    ^^
"""

COW_AGGRESSIVE = """
        (><)
  /------\/
 / |    ||  MOOO!
*  ||----||
   ^^    ^^
"""

COW_DEFENSIVE = """
        (--)
  /------\/
 / |    ||  *defensive stance*
*  ||====||
   ^^    ^^
"""

COW_HAPPY = """
        (^^)
  /------\/
 / |    ||  ♪
*  ||----||
   ^^    ^^
"""

COW_BOSS = """
     (____)
     (o  o)
  /---\  /---\
 /  |  \/  |  \  BOSS COW!
*   ||----||   *
    ^^    ^^
"""

COW_TIPPED = """
         ^^    ^^
         ||----||
        /  |  |  \
       /   ----   \
           (xx)
       *tipped*
"""

# Title art
TITLE_ART = """
╔══════════════════════════════════════════════╗
║                                              ║
║     __   _____ ____ _____ _   _   _   _     ║
║     \ \ / /_ _|  _ \_   _| | | | / \ | |    ║
║      \ V / | || |_) || | | | | |/ _ \| |    ║
║       | |  | ||  _ < | | | |_| / ___ \ |___ ║
║       |_| |___|_| \_\|_|  \___/_/   \_\____|║
║                                              ║
║        ____  _____        __                ║
║       / ___|| _ \ \      / /                ║
║      | |   | | | \ \ /\ / /                 ║
║      | |___| |_| |\ V  V /                  ║
║       \____|____/  \_/\_/                   ║
║                                              ║
║         _____ ___ ____  ____  _____ ____    ║
║        |_   _|_ _|  _ \|  _ \| ____|  _ \   ║
║          | |  | || |_) | |_) |  _| | |_) |  ║
║          | |  | ||  __/|  __/| |___|  _ <   ║
║          |_| |___|_|   |_|   |_____|_| \_\  ║
║                                              ║
║            - Textual Edition -               ║
║                                              ║
╚══════════════════════════════════════════════╝
"""

TITLE_ART_COMPACT = """
╔═══════════════════════════════════════╗
║        VIRTUAL COW TIPPER             ║
║        Text-Based Roguelike           ║
║          Textual Edition              ║
╚═══════════════════════════════════════╝
"""

# Victory art
VICTORY_ART = """
    🎉 VICTORY! 🎉
         \\O/
          |
         / \\
    You did it!
"""

# Game over art
GAME_OVER_ART = """
      GAME OVER
         ___
        /x x\\
       |  _  |
        \\___/
    Better luck next time!
"""

# Shop banner
SHOP_BANNER = """
╔═══════════════════════════════╗
║         YE OLDE SHOP          ║
║   Weapons, Shields & More!    ║
╚═══════════════════════════════╝
"""

# Combat banner
COMBAT_BANNER = """
⚔️ ═══════ COMBAT ═══════ ⚔️
"""

# Floor transition
FLOOR_TRANSITION = """
═══════════════════════════════
      FLOOR {} → FLOOR {}
═══════════════════════════════
"""

# Item icons (for inventory)
ITEM_ICONS = {
    'weapon': '⚔️ ',
    'shield': '🛡️ ',
    'potion': '🧪',
    'special': '✨',
    'consumable': '🍖',
    'default': '📦'
}

# Status icons
STATUS_ICONS = {
    'hp': '❤️ ',
    'cash': '💰',
    'floor': '🏰',
    'attack': '⚔️ ',
    'defense': '🛡️ ',
    'level': '⭐'
}

# Mood indicators
MOOD_INDICATORS = {
    'happy': '😊',
    'angry': '😠',
    'confused': '😕',
    'calm': '😌',
    'aggressive': '👿',
    'defensive': '🛡️',
    'neutral': '😐'
}


def get_cow_art(cow_type: str = "normal", tipped: bool = False) -> str:
    """
    Get ASCII art for a specific cow type.

    Args:
        cow_type: Type of cow (normal, aggressive, defensive, happy, boss)
        tipped: Whether the cow has been tipped

    Returns:
        ASCII art string
    """
    if tipped:
        return COW_TIPPED

    art_map = {
        'normal': COW_NORMAL,
        'aggressive': COW_AGGRESSIVE,
        'defensive': COW_DEFENSIVE,
        'happy': COW_HAPPY,
        'boss': COW_BOSS
    }

    return art_map.get(cow_type.lower(), COW_NORMAL)


def get_floor_transition(current: int, next_floor: int) -> str:
    """
    Get floor transition banner.

    Args:
        current: Current floor number
        next_floor: Next floor number

    Returns:
        Formatted transition banner
    """
    return FLOOR_TRANSITION.format(current, next_floor)


def get_item_icon(item_type: str) -> str:
    """
    Get icon for an item type.

    Args:
        item_type: Type of item

    Returns:
        Icon string
    """
    return ITEM_ICONS.get(item_type, ITEM_ICONS['default'])


def get_status_icon(status_type: str) -> str:
    """
    Get icon for a status type.

    Args:
        status_type: Type of status

    Returns:
        Icon string
    """
    return STATUS_ICONS.get(status_type, '')


def get_mood_indicator(mood: str) -> str:
    """
    Get emoji indicator for a mood.

    Args:
        mood: Mood name

    Returns:
        Emoji string
    """
    return MOOD_INDICATORS.get(mood.lower(), MOOD_INDICATORS['neutral'])


# Loading animation frames
LOADING_FRAMES = [
    "[ ⠋ ] Loading...",
    "[ ⠙ ] Loading...",
    "[ ⠹ ] Loading...",
    "[ ⠸ ] Loading...",
    "[ ⠼ ] Loading...",
    "[ ⠴ ] Loading...",
    "[ ⠦ ] Loading...",
    "[ ⠧ ] Loading...",
    "[ ⠇ ] Loading...",
    "[ ⠏ ] Loading..."
]

# Combat effects
COMBAT_EFFECTS = {
    'hit': """
    💥 SMACK! 💥
    """,
    'miss': """
    ✖ MISS! ✖
    """,
    'critical': """
    ⚡ CRITICAL HIT! ⚡
    """,
    'block': """
    🛡️ BLOCKED! 🛡️
    """
}

# Achievement banners
ACHIEVEMENT_BANNER = """
╔═══════════════════════════════╗
║     🏆 ACHIEVEMENT UNLOCKED!  ║
║         {}
╚═══════════════════════════════╝
"""

def get_achievement_banner(achievement_name: str) -> str:
    """
    Get formatted achievement banner.

    Args:
        achievement_name: Name of achievement

    Returns:
        Formatted banner
    """
    # Center the achievement name (max 27 chars)
    name = achievement_name[:27].center(27)
    return ACHIEVEMENT_BANNER.format(name)