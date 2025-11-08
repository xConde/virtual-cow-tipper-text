# Testing Guide - Virtual Cow Tipper

## Quick Test

Run all tests at once:
```bash
python3 run_tests.py
```

Expected output: "ALL TESTS PASSED! Game is ready to play."

---

## Individual Test Suites

### 1. Cow Generation Tests
```bash
python3 tests/test_cow_generation.py
```

Tests:
- Cow mood calculation (upset/neutral/friendly)
- Cow scaling with player progression
- Random likeliness generation

### 2. Item Factory Tests
```bash
python3 tests/test_item_factory.py
```

Tests:
- Weapon creation
- Shield creation
- Rarity floor (Phase 3 fix)
- Damage rolling
- Shop inventory generation

### 3. Dialogue Manager Tests
```bash
python3 tests/test_dialogue_manager.py
```

Tests:
- All 30 dialogue combinations (3 moods × 10 types)
- Approach scenarios
- Interruption events
- Cow name generation
- Fallback for missing dialogue
- Context variable support
- Dialogue variety (randomness)

### 4. Integration Tests
```bash
python3 tests/test_game_integration.py
```

Tests:
- All module imports
- Config values loaded correctly
- Full cow generation → combat flow
- Item creation → damage calculation
- All systems working together

---

## What's Being Tested

### Phase 1 Fixes Verified
- Variable shadowing bug fixed (pack scores work correctly)
- Cross-platform keyboard input (msvcrt wrapper)
- Config extraction (60+ constants accessible)

### Phase 2 Refactoring Verified
- CowProperties dataclass working
- ItemFactory methods functional
- Cow constructor simplified (2 params)

### Phase 3 Features Verified
- Rarity floor working (legendary items strong)
- Stun effect tracking (player.stunned_turns)
- Death/restart system (restart() method exists)

### Phase 4 Polish Verified
- Type hints throughout (no type errors)
- Code cleanup (old build_item removed)
- All constants in config

### Phase 5 DialogueManager Verified
- All dialogue accessible
- 30 mood/type combinations work
- Your 558 lines of writing intact
- Random variety preserved

---

## Test Coverage

**Unit Tests:** 23 tests across 3 files
**Integration Tests:** 5 tests in 1 file
**Total:** 28 tests

**Coverage:**
- Cow generation OK
- Item generation OK
- Dialogue system OK
- Combat mechanics OK
- Config system OK
- All imports OK

---

## Running the Game

After tests pass:
```bash
python3 main.py
```

**Note:** Requires terminal that supports curses (most Unix terminals)

---

## Troubleshooting

### Tests Fail
1. Check you're in project root
2. Verify Python 3.10+ installed
3. Check no syntax errors: `python3 -m py_compile *.py`

### Import Errors
```bash
python3 -c "from game import VirtualCowTipper; print('OK')"
```

### Dialogue Not Working
```bash
python3 tests/test_dialogue_manager.py
```
Should show 30 dialogue combinations

---

## Test Development

To add new tests:
1. Create test file in `tests/`
2. Import from parent: `sys.path.insert(0, os.path.dirname(...))`
3. Add to `test_files` list in `run_tests.py`

---

**All tests passing = Game is production-ready!**
