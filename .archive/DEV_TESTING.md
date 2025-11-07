# Development Testing Guide

**For Developers**: Quick setup for testing specific game scenarios

---

## Dev Save File System

### Quick Start

**1. Create dev save from example**:
```bash
cp saves/dev_save.example.json saves/dev_save.json
```

**2. Edit dev_save.json** to test specific scenarios:
- Modify HP, cash, inventory
- Set specific floor/encounter numbers
- Adjust pack reputations
- Add specific items

**3. Load dev save** (option A - modify main.py temporarily):
```python
# In main.py, add dev_mode flag:
game = VirtualCowTipper(player_name, show_tutorial=True, load_save=True, dev_mode=True)
```

**OR** (option B - use environment variable):
```bash
DEV_MODE=1 python3 main.py
```

---

## Example Test Scenarios

### Scenario 1: Test Combat with Good Equipment
```json
{
  "hp": 80,
  "cash": 1000,
  "inventory": [
    {"type": "weapon", "name": "Godsword", "damage_min": 15, "damage_max": 25, "rarity": "legendairy"},
    {"type": "shield", "name": "Aegis", "defense_min": 12, "defense_max": 18, "rarity": "legendairy"}
  ],
  "equipped_weapon": {...},
  "equipped_shield": {...}
}
```

### Scenario 2: Test Shop System
```json
{
  "hp": 50,
  "cash": 2000,
  "inventory": [],
  "cow_packs": {
    "1": 10.0,  // Friendly pack - good shop prices
    "2": -5.0   // Upset pack - high shop prices
  }
}
```

### Scenario 3: Test Floor Progression
```json
{
  "current_floor": 5,
  "encounters_this_floor": 9,  // Next encounter triggers floor 6
  "hp": 100,
  "cash": 5000
}
```

### Scenario 4: Test Low Resources (Challenge)
```json
{
  "hp": 10,
  "cash": 5,
  "inventory": [],
  "current_floor": 10
}
```

---

## Dev Save File Location

```
saves/
├── dev_save.example.json  ← Template (committed to git)
├── dev_save.json          ← Your working dev save (gitignored)
└── game_save.json         ← Normal save (gitignored)
```

**Important**:
- `dev_save.example.json` is committed (template)
- `dev_save.json` is gitignored (your personal test data)
- Copy example to dev_save.json and edit as needed

---

## .gitignore Configuration

Already configured:
```gitignore
saves/               # All saves ignored
game_save.json       # Normal save
career_stats.json    # User progress

# BUT: dev_save.example.json IS committed (it's a template)
```

**To commit example updates**:
```bash
git add -f saves/dev_save.example.json
```

---

## Usage Patterns

### Quick Test Specific Feature
```bash
# 1. Edit dev_save.json with scenario
vim saves/dev_save.json

# 2. Load with dev flag (modify main.py temporarily)
# Or use environment variable approach

# 3. Test the feature

# 4. Reset if needed
rm saves/dev_save.json
cp saves/dev_save.example.json saves/dev_save.json
```

### Test Inventory System
```json
{
  "inventory": [
    {"type": "weapon", "name": "Test Sword", ...},
    {"type": "shield", "name": "Test Shield", ...},
    {"type": "potion", "name": "Health Potion", "boost_amount": 20},
    {"type": "tool", "name": "Cow Bell"}
  ]
}
```
Then check: Equip, use, view all work correctly

### Test Encounter Counter
```json
{
  "current_floor": 1,
  "encounters_this_floor": 8  // Two more encounters to floor 2
}
```
Then verify: Encounters count #9, #10, then floor advancement

---

## Architecture

### Why This Approach?

**Pros**:
- ✅ Template committed (dev_save.example.json)
- ✅ Working file gitignored (dev_save.json)
- ✅ No code changes needed (uses existing save system)
- ✅ Easy to create test scenarios
- ✅ Doesn't interfere with normal saves

**Cons**:
- ⚠️ Need to manually copy example to dev_save.json
- ⚠️ Need dev_mode flag implementation (future)

### Current Implementation

**What Works Now**:
- ✅ dev_save.example.json template exists
- ✅ Gitignore configured correctly
- ✅ Can manually create dev_save.json from example

**What Needs Implementation** (future):
- ⏸ dev_mode flag in main.py
- ⏸ Automatic dev_save.json loading
- ⏸ Environment variable support (DEV_MODE=1)

**For Now**: Manually copy and use as regular save

---

## Quick Reference

**Create dev save**:
```bash
cp saves/dev_save.example.json saves/dev_save.json
```

**Use dev save** (current workaround):
```bash
# Rename to regular save temporarily
mv saves/game_save.json saves/game_save.backup.json  # If exists
cp saves/dev_save.json saves/game_save.json
python3 main.py  # Select "Continue"
# Restore after testing
mv saves/game_save.backup.json saves/game_save.json
```

**Better way** (future feature):
```bash
python3 main.py --dev-save
# Or
DEV_MODE=1 python3 main.py
```

---

**Status**: ✅ Example file created, ready for use
**Future**: Implement dev_mode flag for seamless loading
