"""
Save/Load system for game persistence.
"""
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime

from models import PlayerState, GameStats


SAVE_DIR = "saves"
SAVE_FILE = "game_save.json"


class SaveManager:
    """Manages game state persistence."""

    @staticmethod
    def get_save_path() -> str:
        """Get full path to save file."""
        os.makedirs(SAVE_DIR, exist_ok=True)
        return os.path.join(SAVE_DIR, SAVE_FILE)

    @staticmethod
    def save_exists() -> bool:
        """Check if a save file exists."""
        return os.path.exists(SaveManager.get_save_path())

    @staticmethod
    def save_game(player, game_stats, cow_packs: Dict[int, float]) -> bool:
        """
        Save current game state to disk.

        Args:
            player: Player instance
            game_stats: GameStats instance
            cow_packs: Dict of pack scores

        Returns:
            True if save successful, False otherwise
        """
        try:
            # Serialize player state
            player_data = {
                'name': player.name,
                'hp': player.hp,
                'cash': player.cash,
                'stunned_turns': player.stunned_turns,
                'inventory': [
                    {
                        'type': item.type,
                        'name': item.name,
                        # Store weapon/shield stats
                        'min_damage': getattr(item, 'min_damage', None),
                        'max_damage': getattr(item, 'max_damage', None),
                        'min_defence': getattr(item, 'min_defence', None),
                        'max_defence': getattr(item, 'max_defence', None),
                        'rarity': getattr(item, 'rarity', None),
                        'scale': getattr(item, 'scale', None),
                    }
                    for item in player.inventory
                ],
                'weapon': {
                    'name': player.weapon.name,
                    'min_damage': player.weapon.min_damage,
                    'max_damage': player.weapon.max_damage,
                    'rarity': player.weapon.rarity,
                    'scale': player.weapon.scale,
                } if player.weapon else None,
                'shield': {
                    'name': player.shield.name,
                    'min_defence': player.shield.min_defence,
                    'max_defence': player.shield.max_defence,
                    'rarity': player.shield.rarity,
                    'scale': player.shield.scale,
                } if player.shield else None,
            }

            # Serialize game stats
            stats_data = {
                'cows_defeated': game_stats.cows_defeated,
                'cows_fled_from': game_stats.cows_fled_from,
                'total_damage_dealt': game_stats.total_damage_dealt,
                'total_damage_taken': game_stats.total_damage_taken,
                'cash_earned': game_stats.cash_earned,
                'cash_spent': game_stats.cash_spent,
                'items_purchased': game_stats.items_purchased,
                'items_sold': game_stats.items_sold,
                'mini_games_won': game_stats.mini_games_won,
                'mini_games_lost': game_stats.mini_games_lost,
                'legendary_items_found': game_stats.legendary_items_found,
                'dairy_cows_milked': game_stats.dairy_cows_milked,
                'shops_visited': game_stats.shops_visited,
            }

            # Complete save data
            save_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'player': player_data,
                'stats': stats_data,
                'cow_packs': {str(k): v for k, v in cow_packs.items()},  # JSON needs string keys
            }

            # Write to file
            save_path = SaveManager.get_save_path()
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            print(f"\nGame saved to {save_path}")
            return True

        except Exception as e:
            print(f"\nError saving game: {e}")
            return False

    @staticmethod
    def load_game() -> Optional[Dict[str, Any]]:
        """
        Load game state from disk.

        Returns:
            Dict with 'player', 'stats', 'cow_packs' or None if load failed
        """
        try:
            save_path = SaveManager.get_save_path()
            if not os.path.exists(save_path):
                return None

            with open(save_path, 'r') as f:
                save_data = json.load(f)

            # Convert pack scores back to int keys
            cow_packs = {int(k): v for k, v in save_data['cow_packs'].items()}

            return {
                'player': save_data['player'],
                'stats': save_data['stats'],
                'cow_packs': cow_packs,
                'timestamp': save_data.get('timestamp', 'Unknown'),
            }

        except Exception as e:
            print(f"\nError loading game: {e}")
            return None

    @staticmethod
    def delete_save() -> bool:
        """Delete existing save file."""
        try:
            save_path = SaveManager.get_save_path()
            if os.path.exists(save_path):
                os.remove(save_path)
            return True
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False

    @staticmethod
    def restore_player(player, save_data: Dict) -> None:
        """Restore player state from save data."""
        from item import Weapon, Shield, CowBell, Bucket, LiquidGold

        player_data = save_data['player']

        # Restore basic stats
        player.hp = player_data['hp']
        player.cash = player_data['cash']
        player.stunned_turns = player_data.get('stunned_turns', 0)

        # Restore weapon
        if player_data['weapon']:
            w = player_data['weapon']
            player.weapon = Weapon(w['name'], w['min_damage'], w['max_damage'],
                                  w['rarity'], w['scale'])

        # Restore shield
        if player_data['shield']:
            s = player_data['shield']
            player.shield = Shield(s['name'], s['min_defence'], s['max_defence'],
                                  s['rarity'], s['scale'])

        # Restore inventory
        player.inventory.clear()
        for item_data in player_data['inventory']:
            if item_data['type'] == 'weapon':
                item = Weapon(item_data['name'], item_data['min_damage'],
                            item_data['max_damage'], item_data['rarity'],
                            item_data['scale'])
            elif item_data['type'] == 'shield':
                item = Shield(item_data['name'], item_data['min_defence'],
                            item_data['max_defence'], item_data['rarity'],
                            item_data['scale'])
            elif item_data['name'] == 'Cow Bell':
                item = CowBell()
            elif item_data['name'] == 'Bucket':
                item = Bucket()
            elif item_data['name'] == 'Liquid Gold':
                item = LiquidGold()
            else:
                continue  # Skip unknown items

            player.inventory.append(item)

    @staticmethod
    def restore_stats(game_stats, save_data: Dict) -> None:
        """Restore game statistics from save data."""
        stats_data = save_data['stats']

        game_stats.cows_defeated = stats_data['cows_defeated']
        game_stats.cows_fled_from = stats_data['cows_fled_from']
        game_stats.total_damage_dealt = stats_data['total_damage_dealt']
        game_stats.total_damage_taken = stats_data['total_damage_taken']
        game_stats.cash_earned = stats_data['cash_earned']
        game_stats.cash_spent = stats_data['cash_spent']
        game_stats.items_purchased = stats_data['items_purchased']
        game_stats.items_sold = stats_data['items_sold']
        game_stats.mini_games_won = stats_data['mini_games_won']
        game_stats.mini_games_lost = stats_data['mini_games_lost']
        game_stats.legendary_items_found = stats_data['legendary_items_found']
        game_stats.dairy_cows_milked = stats_data['dairy_cows_milked']
        game_stats.shops_visited = stats_data['shops_visited']
