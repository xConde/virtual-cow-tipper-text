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
AGGRO_BASE_CHANCE = 0.35  # 35% - INCREASED! Combat is the fun part!
AGGRO_MAX_CHANCE = 0.50  # Cap at 50% (increased from 40%)
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

# Combat Balance (REBALANCED!)
PLAYER_BASE_DAMAGE_MIN = 2
PLAYER_BASE_DAMAGE_MAX = 8
PLAYER_DAMAGE_CASH_SCALING = 15  # IMPROVED: was 25, now 15 (more damage!)
COW_MAX_STRENGTH_MULTIPLIER = 0.20  # REDUCED: was 0.25, now 0.20 (weaker cows)
COW_MAX_STRENGTH_FROM_CASH = 30  # INCREASED: was 20, now 30 (slower scaling)

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
PACK_SCORE_COMBAT_WIN = 2.0  # INCREASED! (was 1.0)
PACK_SCORE_COMBAT_FLEE = -2.0
PACK_SCORE_SHOP_BASE = 1.0
PACK_SCORE_SHOP_EXPENSIVE_BONUS = 50  # +1 per 50 cash spent

# Combat Rewards (IMPROVED!)
COMBAT_CASH_MULTIPLIER = 2.0  # Combat gives 2x cash!
COMBAT_ITEM_DROP_CHANCE = 0.15  # 15% chance for item drop

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
COW_TIP_CASH_SCALING = 100

# Mini-Game Bet Scaling (Multi-Factor Balance)
MINI_GAME_FLOOR_MULTIPLIER = 2        # Floor component: (floor - 1) * 2
MINI_GAME_CASH_DIVISOR = 100          # Cash component: cash // 100
# Encounter component: int((encounters / 10) * floor)

# Sell Price Calculation
SELL_PRICE_VALUE_MULTIPLIER = 30  # median_stat * 30 = rough value
SELL_PRICE_FRIENDLY = 0.70
SELL_PRICE_NEUTRAL = 0.60
SELL_PRICE_UPSET = 0.50
SELL_PRICE_MINIMUM = 10

# Victory Conditions
VICTORY_COWS_DEFEATED = 50
VICTORY_CASH_EARNED = 5000
VICTORY_LEGENDARY_ITEMS = 3  # Collect 3 legendary items

# Healing System
PLAYER_MAX_HP = 100  # HP cap
DAIRY_COW_HEAL_AMOUNT = 5  # Heal when successfully milking
REST_HEAL_AMOUNT = 10  # Heal when resting

# Health Potion Prices
POTION_MINOR_PRICE = 30   # Heals 10 HP
POTION_NORMAL_PRICE = 50  # Heals 20 HP
POTION_GREATER_PRICE = 80 # Heals 40 HP

# ============================================================================
# UI PROMPTS - Standardized prompt messages for consistent UX
# ============================================================================

# Generic continuation prompts
PROMPT_CONTINUE = "[Continue...]"
PROMPT_ANY_KEY = "[Press any key to continue...]"
PROMPT_BEGIN = "[Press any key to begin...]"
PROMPT_TRY_AGAIN = "[Press any key to try again...]"

# Combat-specific prompts
PROMPT_CONTINUE_TO_COW_TURN = "[Continue to cow's turn...]"
PROMPT_VICTORY = "[Victory!]"
PROMPT_ESCAPING = "[Escaping...]"

# Mini-game prompts
PROMPT_ROLL_DICE = "[Press ENTER to roll the dice...]"
PROMPT_SEE_RESULT = "[Press ENTER to see result...]"
PROMPT_BROWSE_ITEMS = "[Browse items...]"
PROMPT_CONTINUE_SHOPPING = "[Continue shopping...]"
PROMPT_CONTINUE_ADVENTURE = "[Continue adventure...]"

# ============================================================================
# MINI-GAMES - Configuration for mini-game mechanics
# ============================================================================

# Dice Rolling Game
DICE_FACES = 6
DICE_COUNT = 2
DICE_WIN_THRESHOLD = 7  # Need to roll 7+ to win

# Mini-Game Scoring
MINI_GAME_WIN_SCORE = 1.0
MINI_GAME_LOSS_SCORE = -0.5
QUICK_TIP_SCORE = 0.5
QUICK_TIP_PROFIT_MULTIPLIER = 1.5

# Cow Interaction Scoring
LEAVE_COW_PENALTY = -1.0
DICE_GAME_WIN_MULTIPLIER = 2  # Player gets bet back + profit (2x total)

# ============================================================================
# ENHANCED MINI-GAME - Betting and Rematch System
# ============================================================================

# Bet Multipliers (3 tiers)
MINI_GAME_CAUTIOUS_MULTIPLIER = 0.5   # 50% of base - play it safe
MINI_GAME_NORMAL_MULTIPLIER = 1.0     # 100% of base - standard bet
MINI_GAME_BOLD_MULTIPLIER = 2.0       # 200% of base - high risk/reward

# Personality-Based Adjustments
MINI_GAME_FRIENDLY_BET_REDUCTION = 0.8     # 20% cheaper bets
MINI_GAME_FRIENDLY_WIN_THRESHOLD = 6        # Easier to win (6+ instead of 7+)
MINI_GAME_UPSET_BET_INCREASE = 1.3          # 30% more expensive bets
MINI_GAME_NEUTRAL_WIN_THRESHOLD = 7         # Standard difficulty

# Enhanced Scoring System
MINI_GAME_WIN_SCORE_BASE = 0.5
MINI_GAME_WIN_SCORE_PER_BET_MULTIPLIER = 1.0  # Bonus for bigger bets
MINI_GAME_LOSS_SCORE = -0.5
MINI_GAME_REMATCH_WIN_SCORE = 0.0      # Break even (neutral)
MINI_GAME_REMATCH_LOSS_SCORE = -1.5    # Heavy penalty for double loss

# ============================================================================
# COW ATTACK PARAMETERS - Individual attack balance values
# ============================================================================

# Headbutt - Basic reliable attack
COW_ATTACK_HEADBUTT_DAMAGE_MIN = 3
COW_ATTACK_HEADBUTT_DAMAGE_BASE = 2
COW_ATTACK_HEADBUTT_ACCURACY = 85

# Hoof Kick - Higher damage, less accurate
COW_ATTACK_HOOF_KICK_DAMAGE_MIN = 5
COW_ATTACK_HOOF_KICK_DAMAGE_BASE = 4
COW_ATTACK_HOOF_KICK_ACCURACY = 60

# Tail Whip - Weak but very accurate
COW_ATTACK_TAIL_WHIP_DAMAGE_MIN = 1
COW_ATTACK_TAIL_WHIP_DAMAGE_BASE = 1
COW_ATTACK_TAIL_WHIP_STRENGTH_DIVISOR = 2
COW_ATTACK_TAIL_WHIP_ACCURACY = 95

# Stunning Bellow - Stun effect
COW_ATTACK_STUNNING_BELLOW_DURATION = 1
COW_ATTACK_STUNNING_BELLOW_ACCURACY = 75

# Paralyzing Stare - Variable stun duration
COW_ATTACK_PARALYZING_STARE_MIN_DURATION = 1
COW_ATTACK_PARALYZING_STARE_MAX_DURATION = 3
COW_ATTACK_PARALYZING_STARE_ACCURACY = 60

# Milk Rejuvenation - Cow self-heal
COW_ATTACK_MILK_REJUV_HEAL_MIN = 3
COW_ATTACK_MILK_REJUV_HEAL_BASE = 3
COW_ATTACK_MILK_REJUV_STRENGTH_MULTIPLIER = 0.5
COW_ATTACK_MILK_REJUV_ACCURACY = 100

# Power-up Snort - Strength boost
COW_ATTACK_POWER_UP_ACCURACY = 100

# Moo of Doom - Rare powerful attack
COW_ATTACK_MOO_DOOM_DAMAGE_MIN = 4
COW_ATTACK_MOO_DOOM_DAMAGE_BASE = 4
COW_ATTACK_MOO_DOOM_STRENGTH_MULTIPLIER = 1.5
COW_ATTACK_MOO_DOOM_ACCURACY = 65

# Haymaker - Very rare, very strong
COW_ATTACK_HAYMAKER_DAMAGE_MIN = 6
COW_ATTACK_HAYMAKER_DAMAGE_BASE = 5
COW_ATTACK_HAYMAKER_STRENGTH_MULTIPLIER = 1.7
COW_ATTACK_HAYMAKER_ACCURACY = 75

# Bull Rush - Legendary attack
COW_ATTACK_BULL_RUSH_DAMAGE_MIN = 5
COW_ATTACK_BULL_RUSH_DAMAGE_BASE = 5
COW_ATTACK_BULL_RUSH_STRENGTH_MULTIPLIER = 2.0
COW_ATTACK_BULL_RUSH_ACCURACY = 80

# ============================================================================
# ITEM CONFIGURATION - Healing, rewards, and item balance
# ============================================================================

# Health Potion Healing Amounts
POTION_MINOR_HEAL = 10
POTION_NORMAL_HEAL = 20
POTION_GREATER_HEAL = 40

# Liquid Gold Economy
LIQUID_GOLD_CASH_MULTIPLIER = 10  # Cash value per 50 player cash

# Shop Progression Thresholds
SHOP_GREATER_POTION_CASH_THRESHOLD = 200  # Cash needed to unlock greater potions

# Item Stat Calculation
ITEM_MEDIAN_STAT_DIVISOR = 3  # Used for upgrade comparison

# Rarity Stat Floor Multipliers
RARITY_FLOOR_MULTIPLIER_COMMON = 1.0
RARITY_FLOOR_MULTIPLIER_UNCOMMON = 1.2
RARITY_FLOOR_MULTIPLIER_MAGIC = 1.5
RARITY_FLOOR_MULTIPLIER_RARE = 2.0
RARITY_FLOOR_MULTIPLIER_LEGENDARY = 2.5

# ============================================================================
# ITEM DURABILITY - Cowbell and item breaking mechanics
# ============================================================================

COWBELL_BREAK_CASH_DIVISOR = 20  # Cash scaling for break chance (cash // 20)
