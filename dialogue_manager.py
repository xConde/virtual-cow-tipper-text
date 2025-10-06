"""
DialogueManager - Centralized dialogue system for the game.
Wraps existing assets/context.py dialogue with better organization.
"""
from typing import Dict, List, Optional
import random

from assets.context import cow_sayings, approaches, interruptions, cow_names


class DialogueManager:
    """
    Manages all game dialogue with context-aware responses.

    This is a WRAPPER around your existing dialogue from assets/context.py
    All your writing is preserved - just organized better.
    """

    @staticmethod
    def get_cow_saying(mood: str, response_type: str, **context) -> str:
        """
        Get a cow's dialogue response based on mood and situation.

        Args:
            mood: 'friendly', 'neutral', or 'upset'
            response_type: 'intro', 'counter', 'graceful', 'dairy_bucket', etc.
            **context: Optional context variables (player_name, tip_amount, etc.)

        Returns:
            Dialogue string (may include formatting if context provided)
        """
        try:
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
    def get_approach() -> str:
        """Get a random cow approach scenario."""
        return random.choice(approaches)

    @staticmethod
    def get_interruption() -> str:
        """Get a random interruption event."""
        return random.choice(interruptions)

    @staticmethod
    def get_cow_name() -> str:
        """Get a random cow name."""
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
