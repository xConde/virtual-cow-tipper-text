# Migration Rollback Plan

## Overview
This document outlines the rollback procedure if issues are encountered with the Textual UI migration. The architecture has been designed with dual-UI support to enable seamless fallback to the original curses implementation.

## Rollback Triggers

### Critical Issues
- [ ] Textual crashes on startup
- [ ] Performance degradation >50%
- [ ] Core functionality broken
- [ ] Terminal compatibility issues
- [ ] Memory leaks or resource exhaustion

### Non-Critical Issues
- [ ] Minor visual glitches
- [ ] Animation problems
- [ ] Color rendering issues
- [ ] Layout inconsistencies

## Rollback Levels

### Level 1: UI Mode Fallback (Immediate)
**Time Required:** 0 minutes
**Impact:** Minimal - Users continue with curses UI

```bash
# Run with curses mode explicitly
python3 main.py  # Uses curses by default

# Or set environment variable
export VCT_UI_MODE=curses
python3 main_ui.py
```

### Level 2: Code Revert (Quick)
**Time Required:** 5 minutes
**Impact:** Low - Revert to previous commit

```bash
# Revert to pre-Textual commit
git checkout master
git pull origin master

# Or revert specific commits
git revert <textual-commit-hash>
```

### Level 3: Branch Isolation (Moderate)
**Time Required:** 15 minutes
**Impact:** Medium - Isolate Textual changes

```bash
# Create rollback branch
git checkout -b rollback/pre-textual
git reset --hard <last-stable-commit>

# Cherry-pick non-UI improvements
git cherry-pick <bug-fix-commits>

# Push rollback branch
git push origin rollback/pre-textual
```

### Level 4: Full Restoration (Complete)
**Time Required:** 30 minutes
**Impact:** High - Complete removal of Textual code

1. **Remove Textual dependencies:**
```bash
rm -rf venv_textual/
rm requirements_textual.txt
```

2. **Remove UI abstraction layer:**
```bash
rm -rf ui/
rm main_ui.py
rm game_textual_integration.py
```

3. **Restore original main.py:**
```bash
git checkout master -- main.py
```

4. **Clean up test files:**
```bash
rm test_textual_app.py
rm test_ui_abstraction.py
rm test_integration.py
rm test_comprehensive.py
rm verify_*.py
```

## Verification Steps

### Pre-Rollback Checks
1. Backup current state:
```bash
git stash
git branch backup/textual-$(date +%Y%m%d)
```

2. Document issue:
```bash
echo "Issue: <description>" >> rollback.log
echo "Date: $(date)" >> rollback.log
```

### Post-Rollback Validation
1. **Test curses UI:**
```bash
python3 main.py
# Verify main menu loads
# Test new game starts
# Check combat works
```

2. **Run original test suite:**
```bash
python3 run_tests.py
```

3. **Check performance:**
```bash
python3 profile_baseline.py
```

## Gradual Migration Strategy

### Phase 1: Dual-UI Support (Current)
- Both UIs available
- Curses as default
- Textual as opt-in

### Phase 2: Textual Default (Future)
- Textual as default
- Curses as fallback
- Monitor for 2 weeks

### Phase 3: Curses Deprecation (Future)
- Mark curses as deprecated
- Maintain for 1 month
- Remove if stable

## Configuration Fallback

### Application Settings
```python
# In main_ui.py or game_config.py
UI_MODE = "curses"  # Force curses mode
ENABLE_TEXTUAL = False  # Disable Textual completely
FALLBACK_ON_ERROR = True  # Auto-fallback on Textual error
```

### Environment Variables
```bash
export VCT_UI_MODE=curses
export VCT_DISABLE_TEXTUAL=1
export VCT_DEBUG_MODE=1
```

## Emergency Contacts

### Issue Reporting
- GitHub Issues: https://github.com/user/virtual-cow-tipper/issues
- Rollback Branch: rollback/pre-textual

### Recovery Files
- Pre-migration backup: `git tag pre-textual-migration`
- Stable curses version: `git checkout master`
- Test baseline: `tests_baseline.txt`
- Performance baseline: `performance_baseline.txt`

## Monitoring Checklist

### Daily Checks (First Week)
- [ ] Application starts without errors
- [ ] All screens load properly
- [ ] Combat system functional
- [ ] Save/load working
- [ ] No memory leaks

### Weekly Checks (First Month)
- [ ] Performance metrics within baseline
- [ ] No user complaints
- [ ] Test suite passing
- [ ] No terminal compatibility issues

## Rollback Decision Matrix

| Issue Severity | User Impact | Rollback Level | Timeline |
|---------------|-------------|----------------|----------|
| Critical      | All users   | Level 1-2      | Immediate |
| High          | >50% users  | Level 2        | 24 hours |
| Medium        | 10-50%      | Level 1        | 48 hours |
| Low           | <10%        | Monitor        | 1 week |

## Automated Rollback Script

Create `rollback.sh`:
```bash
#!/bin/bash
# Automated rollback script

echo "Virtual Cow Tipper - UI Rollback"
echo "================================"

# Check rollback level
read -p "Rollback level (1-4): " level

case $level in
    1)
        echo "Switching to curses mode..."
        export VCT_UI_MODE=curses
        python3 main.py
        ;;
    2)
        echo "Reverting to master branch..."
        git checkout master
        python3 main.py
        ;;
    3)
        echo "Creating rollback branch..."
        git checkout -b rollback/$(date +%Y%m%d)
        git reset --hard pre-textual-migration
        ;;
    4)
        echo "Full restoration..."
        rm -rf ui/ venv_textual/
        git checkout master -- .
        ;;
    *)
        echo "Invalid level"
        exit 1
        ;;
esac

echo "Rollback complete!"
```

## Testing After Rollback

### Smoke Tests
1. Application starts: `python3 main.py`
2. Create new game
3. Fight one cow
4. Save game
5. Load game
6. Exit cleanly

### Full Test Suite
```bash
# Run all original tests
python3 run_tests.py

# Check specific components
python3 -m pytest tests/test_cow.py
python3 -m pytest tests/test_player.py
python3 -m pytest tests/test_combat.py
```

## Lessons Learned Log

Document any issues encountered:
```markdown
### Issue: [Date]
**Description:**
**Resolution:**
**Prevention:**
```

## Success Criteria for Permanent Migration

- [ ] 2 weeks without critical issues
- [ ] Performance equal or better than curses
- [ ] All tests passing consistently
- [ ] Positive user feedback
- [ ] No terminal compatibility issues
- [ ] Documentation complete

---

**Last Updated:** 2025-11-01
**Rollback Plan Version:** 1.0
**Status:** Ready for deployment