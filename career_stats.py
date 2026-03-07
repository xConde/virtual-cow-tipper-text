"""
Career Stats - Meta-progression system that persists across all runs.
Every run contributes to long-term unlocks, making losses valuable!
"""
import json
import os
import tempfile
from typing import List, Dict, Optional
from datetime import datetime


CAREER_FILE = "career_stats.json"


class Unlock:
    """Represents a permanent unlock."""

    # Unlock IDs
    STARTING_COWBELL = "starting_cowbell"
    BONUS_HP_10 = "bonus_hp_10"
    BONUS_HP_20 = "bonus_hp_20"
    BONUS_CASH_25 = "bonus_cash_25"
    BONUS_CASH_50 = "bonus_cash_50"
    SHOP_DISCOUNT = "shop_discount_10"
    STARTING_WEAPON = "starting_weapon"
    LEGENDARY_SHOP = "legendary_shop_access"
    DAIRY_BONUS = "dairy_heal_bonus"
    PACK_MASTER = "pack_master_bonus"
    COMBAT_VETERAN = "combat_damage_bonus"

    # Unlock requirements and descriptions
    UNLOCK_DATA = {
        STARTING_COWBELL: {
            'requirement_type': 'dairy_milked',
            'requirement_value': 10,
            'name': 'Dairy Farmer',
            'description': 'Start every run with a Cow Bell equipped',
            'bonus': 'Cow Bell in starting inventory'
        },
        BONUS_HP_10: {
            'requirement_type': 'cows_defeated',
            'requirement_value': 25,
            'name': 'Tough Hide',
            'description': 'Start with +10 max HP',
            'bonus': 'Starting HP: 20 → 30'
        },
        BONUS_HP_20: {
            'requirement_type': 'cows_defeated',
            'requirement_value': 50,
            'name': 'Iron Constitution',
            'description': 'Start with +20 max HP',
            'bonus': 'Starting HP: 30 → 40'
        },
        BONUS_CASH_25: {
            'requirement_type': 'cash_earned',
            'requirement_value': 1000,
            'name': 'Shrewd Investor',
            'description': 'Start with +$25 cash',
            'bonus': 'Starting cash: $50 → $75'
        },
        BONUS_CASH_50: {
            'requirement_type': 'cash_earned',
            'requirement_value': 5000,
            'name': 'Wealthy Rancher',
            'description': 'Start with +$50 cash',
            'bonus': 'Starting cash: $75 → $125'
        },
        SHOP_DISCOUNT: {
            'requirement_type': 'items_purchased',
            'requirement_value': 50,
            'name': 'Regular Customer',
            'description': 'Get 10% discount at all shops',
            'bonus': 'All shop prices reduced by 10%'
        },
        STARTING_WEAPON: {
            'requirement_type': 'cows_defeated',
            'requirement_value': 100,
            'name': 'Weapon Master',
            'description': 'Start with a basic weapon',
            'bonus': 'Start with equipped weapon'
        },
        LEGENDARY_SHOP: {
            'requirement_type': 'legendary_found',
            'requirement_value': 5,
            'name': 'Legendary Seeker',
            'description': 'Shops can sell legendary items',
            'bonus': 'Legendary items in shop rotation'
        },
        DAIRY_BONUS: {
            'requirement_type': 'dairy_milked',
            'requirement_value': 25,
            'name': 'Master Milker',
            'description': 'Dairy cows heal +10 HP instead of +5',
            'bonus': 'Double dairy healing'
        },
        COMBAT_VETERAN: {
            'requirement_type': 'total_damage',
            'requirement_value': 5000,
            'name': 'Combat Veteran',
            'description': 'Deal +5 bonus damage',
            'bonus': '+5 to all damage rolls'
        },
    }


class CareerStats:
    """Persistent stats across all runs - the meta-progression system!"""

    def __init__(self):
        self.total_runs = 0
        self.total_victories = 0
        self.total_cows_defeated = 0
        self.total_cows_fled = 0
        self.total_cash_earned = 0
        self.total_damage_dealt = 0
        self.total_dairy_milked = 0
        self.total_items_purchased = 0
        self.total_legendary_found = 0
        self.unlocks: List[str] = []
        self.best_run_cash = 0
        self.best_run_cows = 0

    def add_run_stats(self, game_stats, victory: bool):
        """Add stats from a completed run."""
        self.total_runs += 1
        if victory:
            self.total_victories += 1

        self.total_cows_defeated += game_stats.cows_defeated
        self.total_cows_fled += game_stats.cows_fled_from
        self.total_cash_earned += game_stats.cash_earned
        self.total_damage_dealt += game_stats.total_damage_dealt
        self.total_dairy_milked += game_stats.dairy_cows_milked
        self.total_items_purchased += game_stats.items_purchased
        self.total_legendary_found += game_stats.legendary_items_found

        # Track best runs
        self.best_run_cash = max(self.best_run_cash, game_stats.cash_earned)
        self.best_run_cows = max(self.best_run_cows, game_stats.cows_defeated)

    def check_unlocks(self) -> List[str]:
        """Check which unlocks player has earned. Returns newly unlocked items."""
        newly_unlocked = []

        for unlock_id, data in Unlock.UNLOCK_DATA.items():
            # Skip if already unlocked
            if unlock_id in self.unlocks:
                continue

            # Check requirement
            req_type = data['requirement_type']
            req_value = data['requirement_value']

            earned = False
            if req_type == 'cows_defeated':
                earned = self.total_cows_defeated >= req_value
            elif req_type == 'cash_earned':
                earned = self.total_cash_earned >= req_value
            elif req_type == 'dairy_milked':
                earned = self.total_dairy_milked >= req_value
            elif req_type == 'items_purchased':
                earned = self.total_items_purchased >= req_value
            elif req_type == 'legendary_found':
                earned = self.total_legendary_found >= req_value
            elif req_type == 'total_damage':
                earned = self.total_damage_dealt >= req_value

            if earned:
                self.unlocks.append(unlock_id)
                newly_unlocked.append(unlock_id)

        return newly_unlocked

    def has_unlock(self, unlock_id: str) -> bool:
        """Check if player has specific unlock."""
        return unlock_id in self.unlocks

    def get_starting_bonuses(self) -> Dict[str, any]:
        """Get bonuses to apply at game start."""
        bonuses = {
            'extra_hp': 0,
            'extra_cash': 0,
            'starting_items': [],
            'shop_discount': 0.0,
            'damage_bonus': 0,
            'dairy_heal_bonus': 0,
        }

        if self.has_unlock(Unlock.STARTING_COWBELL):
            bonuses['starting_items'].append('cowbell')

        if self.has_unlock(Unlock.BONUS_HP_10):
            bonuses['extra_hp'] += 10

        if self.has_unlock(Unlock.BONUS_HP_20):
            bonuses['extra_hp'] += 20

        if self.has_unlock(Unlock.BONUS_CASH_25):
            bonuses['extra_cash'] += 25

        if self.has_unlock(Unlock.BONUS_CASH_50):
            bonuses['extra_cash'] += 50

        if self.has_unlock(Unlock.SHOP_DISCOUNT):
            bonuses['shop_discount'] = 0.10

        if self.has_unlock(Unlock.STARTING_WEAPON):
            bonuses['starting_items'].append('basic_weapon')

        if self.has_unlock(Unlock.DAIRY_BONUS):
            bonuses['dairy_heal_bonus'] = 5  # +5 to dairy healing

        if self.has_unlock(Unlock.COMBAT_VETERAN):
            bonuses['damage_bonus'] = 5

        return bonuses

    def save(self):
        """Save career stats to disk."""
        data = {
            'version': 1,
            'total_runs': self.total_runs,
            'total_victories': self.total_victories,
            'total_cows_defeated': self.total_cows_defeated,
            'total_cows_fled': self.total_cows_fled,
            'total_cash_earned': self.total_cash_earned,
            'total_damage_dealt': self.total_damage_dealt,
            'total_dairy_milked': self.total_dairy_milked,
            'total_items_purchased': self.total_items_purchased,
            'total_legendary_found': self.total_legendary_found,
            'unlocks': self.unlocks,
            'best_run_cash': self.best_run_cash,
            'best_run_cows': self.best_run_cows,
            'last_updated': datetime.now().isoformat(),
        }

        fd, tmp_path = tempfile.mkstemp(dir='.', suffix='.tmp')
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, CAREER_FILE)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    @staticmethod
    def load() -> 'CareerStats':
        """Load career stats from disk or create new."""
        if not os.path.exists(CAREER_FILE):
            return CareerStats()

        try:
            with open(CAREER_FILE, 'r') as f:
                data = json.load(f)

            stats = CareerStats()
            version = data.get('version', 0)
            # Future: handle version migrations here
            stats.total_runs = data.get('total_runs', 0)
            stats.total_victories = data.get('total_victories', 0)
            stats.total_cows_defeated = data.get('total_cows_defeated', 0)
            stats.total_cows_fled = data.get('total_cows_fled', 0)
            stats.total_cash_earned = data.get('total_cash_earned', 0)
            stats.total_damage_dealt = data.get('total_damage_dealt', 0)
            stats.total_dairy_milked = data.get('total_dairy_milked', 0)
            stats.total_items_purchased = data.get('total_items_purchased', 0)
            stats.total_legendary_found = data.get('total_legendary_found', 0)
            stats.unlocks = data.get('unlocks', [])
            stats.best_run_cash = data.get('best_run_cash', 0)
            stats.best_run_cows = data.get('best_run_cows', 0)

            return stats
        except Exception as e:
            print(f"Error loading career stats: {e}")
            return CareerStats()

    def show_progress(self):
        """Display career progress and unlocks."""
        print("\n" + "="*60)
        print("CAREER PROGRESS")
        print("="*60)

        print(f"\nRuns: {self.total_runs} (Victories: {self.total_victories})")
        print(f"Cows Defeated: {self.total_cows_defeated}")
        print(f"Cash Earned: ${self.total_cash_earned}")
        print(f"Dairy Milked: {self.total_dairy_milked}")
        print(f"Legendary Found: {self.total_legendary_found}")

        print(f"\nBest Run:")
        print(f"  Most cows defeated: {self.best_run_cows}")
        print(f"  Most cash earned: ${self.best_run_cash}")

        print(f"\nUnlocks ({len(self.unlocks)}/{len(Unlock.UNLOCK_DATA)}):")
        if self.unlocks:
            for unlock_id in self.unlocks:
                unlock_info = Unlock.UNLOCK_DATA[unlock_id]
                print(f"  [OK] {unlock_info['name']}: {unlock_info['description']}")
        else:
            print("  (None yet - keep playing to unlock bonuses!)")

        # Show next unlock
        next_unlock = self._get_next_unlock()
        if next_unlock:
            print(f"\nNext Unlock:")
            print(f"  {next_unlock['name']}: {next_unlock['description']}")
            print(f"  Progress: {next_unlock['progress']}/{next_unlock['requirement']}")

    def _get_next_unlock(self) -> Optional[Dict]:
        """Find the closest unlock player hasn't achieved yet."""
        closest = None
        closest_diff = float('inf')

        for unlock_id, data in Unlock.UNLOCK_DATA.items():
            if unlock_id in self.unlocks:
                continue

            req_type = data['requirement_type']
            req_value = data['requirement_value']

            current = 0
            if req_type == 'cows_defeated':
                current = self.total_cows_defeated
            elif req_type == 'cash_earned':
                current = self.total_cash_earned
            elif req_type == 'dairy_milked':
                current = self.total_dairy_milked
            elif req_type == 'items_purchased':
                current = self.total_items_purchased
            elif req_type == 'legendary_found':
                current = self.total_legendary_found
            elif req_type == 'total_damage':
                current = self.total_damage_dealt

            diff = req_value - current
            if diff > 0 and diff < closest_diff:
                closest_diff = diff
                closest = {
                    'name': data['name'],
                    'description': data['description'],
                    'progress': current,
                    'requirement': req_value
                }

        return closest
