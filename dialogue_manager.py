"""
DialogueManager - Centralized dialogue system for the game.
Wraps existing assets/context.py dialogue with better organization.
"""
from typing import Dict, List, Optional
import random

from assets.context import cow_sayings, approaches, interruptions, cow_names
from assets.mature_dialogue import mature_cow_sayings, mature_cow_names, mature_approaches
import random


class DialogueManager:
    """
    Manages all game dialogue with context-aware responses.

    This is a WRAPPER around your existing dialogue from assets/context.py
    All your writing is preserved - just organized better.
    """

    @staticmethod
    def get_cow_saying(mood: str, response_type: str, use_mature: bool = True, **context) -> str:
        """
        Get a cow's dialogue response based on mood and situation.

        Args:
            mood: 'friendly', 'neutral', or 'upset'
            response_type: 'intro', 'counter', 'graceful', 'dairy_bucket', etc.
            use_mature: If True, 70% chance for mature dialogue (less punny)
            **context: Optional context variables (player_name, tip_amount, etc.)

        Returns:
            Dialogue string (may include formatting if context provided)
        """
        try:
            # 70% chance to use mature dialogue (adult humor)
            # 30% chance to use original dialogue (puns)
            if use_mature and random.random() < 0.70:
                # Try mature dialogue first
                if mood in mature_cow_sayings and response_type in mature_cow_sayings[mood]:
                    responses = mature_cow_sayings[mood][response_type]
                    response = random.choice(responses)
                else:
                    # Fall back to original if mature version doesn't exist
                    responses = cow_sayings[mood][response_type]
                    response = random.choice(responses)
            else:
                # Use original punny dialogue
                responses = cow_sayings[mood][response_type]
                response = random.choice(responses)

            # Apply context variables if provided and response is a template
            if context and '{' in response:
                return response.format(**context)

            return response
        except (KeyError, IndexError) as e:
            # Fallback if dialogue missing
            return f"Moo. ({mood} {response_type})"

    @staticmethod
    def get_approach(mature_chance: float = 0.30) -> str:
        """
        Get a random cow approach scenario.

        Args:
            mature_chance: Probability of sophisticated/dark humor approach

        Returns:
            Approach text
        """
        if random.random() < mature_chance and mature_approaches:
            return random.choice(mature_approaches)
        return random.choice(approaches)

    @staticmethod
    def get_interruption() -> str:
        """Get a random interruption event."""
        return random.choice(interruptions)

    @staticmethod
    def get_cow_name(mature_chance: float = 0.20) -> str:
        """
        Get a random cow name.

        Args:
            mature_chance: Probability of sophisticated literary name

        Returns:
            Cow name
        """
        if random.random() < mature_chance and mature_cow_names:
            return random.choice(mature_cow_names)
        return random.choice(cow_names)

    # Context-aware helpers for future enhancements

    @staticmethod
    def get_context_aware_intro(mood: str, player_name: str, player_cash: int) -> str:
        """
        Get intro with optional context enhancement.
        Falls back to standard intro if no context-aware version exists.
        """
        # For now, just use standard intro
        # Can add context-aware variations later
        return DialogueManager.get_cow_saying(mood, 'intro',
                                              player_name=player_name,
                                              player_cash=player_cash)

    @staticmethod
    def get_combat_reaction(situation: str) -> Optional[str]:
        """
        Get combat-specific reactions (future enhancement).

        Situations: 'player_low_hp', 'cow_low_hp', 'critical_hit', 'miss'
        """
        # Placeholder for future combat dialogue variety
        combat_reactions = {
            'player_low_hp': [
                "You're looking wobbly!",
                "One more hit should do it!",
            ],
            'cow_low_hp': [
                "I'm... not... done!",
                "You'll pay for this!",
            ],
        }

        if situation in combat_reactions:
            return random.choice(combat_reactions[situation])
        return None
