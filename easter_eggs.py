"""
Easter Eggs - Hidden surprises that match the game's absurdist humor.
Rare encounters and special effects that reward exploration and experimentation.
"""
import random
from typing import Optional, Dict


# Legendary Named Cows (0.1% chance)
LEGENDARY_COWS = {
    "The Cowculator": {
        "approach": "A cow wearing thick glasses furiously solving advanced calculus on a chalkboard. Mathematical symbols float around its head.",
        "mood_override": "friendly",
        "cash_multiplier": 3.0,
        "strength_override": 15,
        "dialogue_intro": "The numbers, {player_name}! They're utterly irrational! Care to compute a tip?",
        "dialogue_victory": "You've... divided by zero... *dissolves into mathematical symbols*",
        "special": "Drops triple cash (mathematician's fortune!)"
    },
    "Moodini": {
        "approach": "A cow performing impossible escape tricks from a locked barn, chains clinking dramatically.",
        "mood_override": "neutral",
        "cannot_defeat": True,  # Always escapes at 1 HP
        "dialogue_intro": "You'll never catch Moodini! Watch as I escape certain doom!",
        "dialogue_escape": "*Disappears in a puff of hay and reappears outside the fence* Better luck next time!",
        "special": "Cannot be defeated (flees at 1 HP, no rewards)"
    },
    "Bovine Einstein": {
        "approach": "A cow with wild, unkempt fur scribbling 'E=MC²' in the dirt with its hoof, surrounded by floating equations.",
        "mood_override": "friendly",
        "is_shop": True,
        "shop_has_legendary": True,
        "dialogue_intro": "Relatively speaking, my shop has udderly brilliant items!",
        "dialogue_purchase": "A wise investment! The theory of relativi-moo approves!",
        "special": "Shop always has 1 legendary item"
    },
    "Elvis Parcowly": {
        "approach": "A cow wearing rhinestone-studded sunglasses doing hip gyrations and singing 'Moo-oo Can't Help Falling in Love.'",
        "mood_override": "friendly",
        "mini_game_multiplier": 3.0,
        "dialogue_intro": "Thank moo, thank moo very much! *hip swivel* Care for a tip?",
        "dialogue_graceful": "You ain't nothin' but a hound cow! *Elvis laugh* That tip was king-sized!",
        "special": "Mini-games pay triple!"
    },
    "The Notorious C.O.W.": {
        "approach": "A cow wearing a backwards baseball cap and thick gold chains, beatboxing softly.",
        "mood_override": "neutral",
        "guaranteed_legendary_drop": True,
        "dialogue_intro": "Yo, it's all about the moo-lah, baby. You got that cheddar?",
        "dialogue_victory": "Respect. You earned it. *drops legendary item* Keep it real.",
        "special": "Always drops a legendary item!"
    },
}


def get_legendary_cow() -> Optional[Dict]:
    """
    0.1% chance to encounter a legendary named cow.

    Returns dict with legendary cow properties or None
    """
    if random.random() < 0.001:  # 0.1% chance
        return random.choice(list(LEGENDARY_COWS.items()))
    return None


def check_lucky_number(player_hp: int, player_cash: int) -> Optional[str]:
    """
    Check for lucky number 777 Easter egg.

    Returns effect description if triggered, None otherwise
    """
    if player_hp == 77 or player_cash == 777:
        return "LUCKY 777!"
    return None


def check_developer_name(player_name: str) -> bool:
    """Check if player used developer's name."""
    developer_names = ["ed", "edconde", "edward", "conde", "ed conde"]
    return player_name.lower() in developer_names


def check_achievement_42(cows_defeated: int) -> bool:
    """Check for Hitchhiker's Guide reference (42 cows)."""
    return cows_defeated == 42


def get_meta_dialogue() -> Optional[str]:
    """
    1% chance for fourth wall break dialogue.

    Returns meta-commentary or None
    """
    if random.random() < 0.01:
        meta_dialogue = [
            "Wait... are we in a Python script? I can smell the indentation from here.",
            "You know what's weird? I can feel the random number generator deciding my fate.",
            "Is this... a terminal game? I swear I just saw a curses import.",
            "The developer really went ham with these cow puns, huh? There's like 300 of them.",
            "I'm just a bunch of attributes in a dataclass, man. We're all just code.",
            "Fun fact: I'm stored in a file called context.py. Very existential.",
            "Pack 3? More like I'm just a random integer between 1 and 6!",
            "My 'mood' is literally calculated from a variable called 'likeliness'. How arbitrary!",
        ]
        return random.choice(meta_dialogue)
    return None


def get_philosopher_cow_dialogue() -> Optional[str]:
    """
    0.5% chance for philosophical cow encounter.

    Returns philosophical musing or None
    """
    if random.random() < 0.005:
        philosophy = [
            "To moo or not to moo, that is the question...",
            "I think therefore I am... a cow. But what IS a cow, really?",
            "If a cow tips in the forest and no one's around, did it really happen?",
            "Cogito ergo moo. I moo, therefore I am.",
            "What is the sound of one hoof clapping? *stares intensely*",
            "We are all just cows in someone else's game, {player_name}.",
            "Is tipping cows ethical? Let's discuss this over some grass.",
        ]
        return random.choice(philosophy)
    return None


class EasterEggRewards:
    """Track Easter eggs found for career stats."""

    @staticmethod
    def legendary_cow_found(cow_name: str):
        """Called when legendary cow encountered."""
        print(f"\n{'*'*60}")
        print(f"LEGENDARY COW ENCOUNTERED: {cow_name}!")
        print(f"{'*'*60}")
        print("This is a RARE encounter! (0.1% chance)")

    @staticmethod
    def lucky_777_activated(hp_or_cash: str):
        """Called when player has exactly 777 or 77."""
        print(f"\n{'*'*40}")
        print(f"LUCKY NUMBER 777! ({hp_or_cash})")
        print(f"{'*'*40}")
        print("A four-leaf clover appears!")
        print("Next 3 shops will have legendary items!")
        print("Next 3 mini-games will auto-win!")
        return {
            'legendary_shop_count': 3,
            'mini_game_auto_win': 3
        }

    @staticmethod
    def achievement_42():
        """The Answer to Life, Universe, and Everything."""
        print(f"\n{'='*40}")
        print("42 COWS DEFEATED!")
        print(f"{'='*40}")
        print("You've found the Answer to Life, the Universe, and Everything!")
        print("\n*A towel mysteriously appears*")
        print("\nUNLOCKED: The Towel of Destiny (legendary item)")
        print("So long, and thanks for all the tips!")

    @staticmethod
    def developer_encounter():
        """Special encounter when using developer's name."""
        print(f"\n{'='*40}")
        print("🎁 Developer Bonus!")
        print(f"{'='*40}")
        print('"Oh, it\'s YOU. The one who created me!"')
        print('"Take this legendary item as thanks."')
