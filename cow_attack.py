from typing import Optional, Literal, TYPE_CHECKING
import random
from utils import safe_print

if TYPE_CHECKING:
    from player import Player
    from cow import Cow

CowAttackEffect = Literal["stun", "heal", "power_up"]

class CowAttack:
    """Represents a cow's attack with damage, effects, and accuracy."""

    def __init__(self, name: str, damage: Optional[int] = None,
                 effect: Optional[CowAttackEffect] = None,
                 duration: Optional[int] = None,
                 healing: Optional[int] = None,
                 accuracy: int = 100):
        self.name = name
        self.damage = damage
        self.effect = effect
        self.duration = duration
        self.healing = healing
        self.accuracy = accuracy

    @classmethod
    def generate_cow_combat_styles(cls, cow_strength: int) -> list['CowAttack']:
        return [
            cls("headbutt", damage=random.randint(3, 2 + cow_strength), accuracy=85),
            cls("hoof kick", damage=random.randint(5, 4 + cow_strength), accuracy=60),
            cls("tail whip", damage=random.randint(1, 1 + cow_strength // 2), accuracy=95),

            cls("stunning bellow", effect="stun", duration=1, accuracy=75),
            cls("paralyzing stare", effect="stun", duration=random.randint(1, 3), accuracy=60),
            cls("milk rejuvenation", effect="heal", healing=random.randint(3, 3 + int(cow_strength * 0.5)), accuracy=100),
            cls("power-up snort", effect="power_up", accuracy=100),

            cls("moo of doom", damage=random.randint(4, 4 + int(cow_strength * 1.5)), accuracy=65),
            cls("haymaker", damage=random.randint(6, 5 + int(cow_strength * 1.7)), accuracy=75),
            cls("bull rush", damage=random.randint(5, 5 + int(cow_strength * 2)), accuracy=80),
        ]

    @classmethod
    def cow_attack(cls, player: 'Player', cow: 'Cow') -> str:
        """Execute a cow's attack against the player. Returns attack message."""
        cow_combat_styles = cls.generate_cow_combat_styles(cow.strength)
        attack_weights = [25, 15, 18, 9, 9, 9, 9, 3, 2, 1]
        chosen_attack = random.choices(cow_combat_styles, weights=attack_weights, k=1)[0]

        hit_chance = random.randint(0, 100)
        attack_msg = ""

        if hit_chance <= chosen_attack.accuracy:
            if chosen_attack.damage:
                raw_damage = chosen_attack.damage
                blocked = 0
                if player.shield:
                    blocked = random.randint(player.shield.min_defence, player.shield.max_defence)
                    blocked = min(blocked, raw_damage)
                actual_damage = max(0, raw_damage - blocked)
                player.hp -= actual_damage
                if blocked > 0 and actual_damage > 0:
                    attack_msg = f"{cow.name} uses {chosen_attack.name}! Your shield deflects the blow! {actual_damage} damage taken."
                elif blocked > 0:
                    attack_msg = f"{cow.name} uses {chosen_attack.name}! Your shield absorbs the hit completely!"
                else:
                    attack_msg = f"{cow.name} uses {chosen_attack.name}! {raw_damage} damage taken."

            if chosen_attack.effect:
                if chosen_attack.effect == "stun":
                    player.stunned_turns = chosen_attack.duration
                    # Add stun info to attack message
                    attack_msg += f"\n{player.name} is stunned for {chosen_attack.duration} turns!"
                elif chosen_attack.effect == "heal":
                    cow.hp += chosen_attack.healing
                    cow.hp = min(cow.hp, cow.max_hp)
                    # Add heal info to attack message
                    attack_msg += f"\n{cow.name} heals for {chosen_attack.healing} HP!"
                elif chosen_attack.effect == "power_up":
                    cow.strength += 1
                    attack_msg += f"\n{cow.name} powers up! Strength increased!"
        else:
            attack_msg = f"{cow.name} misses!"

        return attack_msg
