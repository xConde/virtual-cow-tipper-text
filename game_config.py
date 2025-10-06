"""
Game Configuration - All constants and balance values
Extracted from scattered magic numbers across codebase
"""

# Player Starting Values
PLAYER_STARTING_HP = 20
PLAYER_STARTING_CASH = 50
PLAYER_MAX_INVENTORY_SIZE = 8

# Cow Generation
COW_QUEUE_SIZE = 3
NUM_COW_PACKS = 6
DAIRY_ENCOUNTER_BASE_CHANCE = 0.05  # 5%
DAIRY_ENCOUNTER_WITH_COWBELL = 0.15  # 15%
AGGRO_BASE_CHANCE = 0.15  # 15%
SHOP_CHANCE = 0.15  # 15%

# Game Events
INTERRUPTION_CHANCE = 0.10  # 10%
COWBELL_BREAK_CHANCE_BASE = 0.05  # 5%

# Cow Likeliness (Mood System)
LIKELINESS_BASE = 5
LIKELINESS_UPSET_THRESHOLD = 4  # <= 4 is upset
LIKELINESS_FRIENDLY_THRESHOLD = 7  # >= 7 is friendly
LIKELINESS_MOOD_OFFSETS = [-2, 0, 2]  # Random offsets
LIKELINESS_MOOD_WEIGHTS = [10, 80, 10]  # Weights for offsets

# Combat Balance
PLAYER_BASE_DAMAGE_MIN = 2
PLAYER_BASE_DAMAGE_MAX = 8
PLAYER_DAMAGE_CASH_SCALING = 25  # Damage += cash // 25
COW_MAX_STRENGTH_MULTIPLIER = 0.25  # Max strength = player.hp * 0.25
COW_MAX_STRENGTH_FROM_CASH = 20  # Max strength = player.cash // 20

# Damage Context Thresholds
SMALL_DAMAGE_THRESHOLD = 0.20  # <= 20% of cow HP
LARGE_DAMAGE_THRESHOLD = 0.50  # >= 50% of cow HP
SMALL_DAMAGE_CONTEXT_CHANCE = 0.66  # 66% chance to show context

# Shop Balance
SHOP_PRICE_BASE_MIN = 20
SHOP_PRICE_BASE_MAX = 25
SHOP_PRICE_CASH_SCALING = 50  # Price += 3 * (cash // 50)
SHOP_PRICE_UPSET_MULTIPLIER = 2.0
SHOP_LUCKY_CHANCE_FRIENDLY = 0.25  # 25%
SHOP_LUCKY_CHANCE_UPSET = 0.40  # 40%

# Item Pricing Multipliers
SHOP_RANDOM_ITEM_MULTIPLIER = 1.0
SHOP_WEAPON_MULTIPLIER = 1.5
SHOP_SHIELD_MULTIPLIER = 2.0

# Pack Score Updates
PACK_SCORE_COMBAT_WIN = 1.0
PACK_SCORE_COMBAT_FLEE = -2.0
PACK_SCORE_SHOP_BASE = 1.0
PACK_SCORE_SHOP_EXPENSIVE_BONUS = 50  # +1 per 50 cash spent

# Mini-Game Settings
TIPPING_BAR_MAX_MULTIPLIER = 3  # Max reward = bet * 3
TIPPING_BAR_TIME_BASE = 0.30
TIPPING_BAR_TIME_SCALING = 0.01  # Faster with higher bets
COW_RACE_LENGTH = 50
COW_RACE_BASE_SPEED = 1
COW_RACE_WIN_MULTIPLIER = 2  # Win = bet * 2
GUESSING_GAME_MAX_GUESSES = 4
GUESSING_GAME_RANGE_MULTIPLIER = 1.5  # Range = bet * 1.5

# Item Generation Weights
ITEM_TYPE_WEIGHTS_NORMAL = [35, 30, 32, 3]  # weapon, shield, tool, object
ITEM_TYPE_WEIGHTS_LUCKY = [63, 15, 20, 2]

# Weapon/Shield tier weights
ITEM_TIER_WEIGHTS_NORMAL = [35, 28, 24, 15, 12, 9, 6, 4, 2, 1]
ITEM_TIER_WEIGHTS_LUCKY = [40, 30, 20, 10, 5, 3, 2, 1, 1, 1]

# Rarity weights
RARITY_WEIGHTS_NORMAL = [60, 35, 10, 4, 1]  # common, uncommon, magic, rare, legendary
RARITY_WEIGHTS_LUCKY = [72, 32, 3, 2, 1]

# Stat Scaling by Rarity
RARITY_MIN_STAT_MULTIPLIER = 0.25  # min_stat * scale * 0.25
RARITY_MAX_STAT_MULTIPLIER = 0.60  # max_stat * scale * 0.60

# Cow Attack Weights (10 attack types)
COW_ATTACK_WEIGHTS = [25, 15, 18, 9, 9, 9, 9, 3, 2, 1]
# [headbutt, hoof kick, tail whip, stunning bellow, paralyzing stare,
#  milk rejuvenation, power-up snort, moo of doom, haymaker, bull rush]

# Liquid Gold Value
LIQUID_GOLD_BASE_VALUE = 150
LIQUID_GOLD_WEAPON_DPS_MULTIPLIER = 5
LIQUID_GOLD_CASH_SCALING = 50  # +10 per 50 cash

# Terminal Layout
TERMINAL_WIDTH = 100
TERMINAL_HEIGHT = 30

# Dialog System
DIALOG_HISTORY_MAX_LENGTH = 5
DIALOG_MESSAGE_MAX_CHARS = 75

# Cow Generation - Detailed
COW_MIN_HP = 10
COW_HP_STRENGTH_MULTIPLIER_LOW = 1
COW_HP_STRENGTH_MULTIPLIER_HIGH = 2
COW_HP_LIKELINESS_MULTIPLIER = 2  # Doubled for friendly cows
COW_HP_CASH_BONUS_MIN = 1
COW_HP_CASH_BONUS_MAX = 3
COW_HP_CASH_MODULO = 20

COW_TIP_REQUIREMENT_MIN = 3
COW_TIP_REQUIREMENT_MAX = 12
COW_TIP_CASH_SCALING = 25

# Sell Price Calculation
SELL_PRICE_VALUE_MULTIPLIER = 30  # median_stat * 30 = rough value
SELL_PRICE_FRIENDLY = 0.70
SELL_PRICE_NEUTRAL = 0.60
SELL_PRICE_UPSET = 0.50
SELL_PRICE_MINIMUM = 10
