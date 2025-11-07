# Documentation Rules - Preventing .md Sprawl

**READ THIS FIRST**: Rules for managing documentation in this project

---

## The Golden Rule

**DO NOT create new .md files in the root directory.**

Only 2 .md files belong in root:
1. `README.md` - Project overview
2. `CHANGELOG.md` - Recent changes

---

## Where Documentation Goes

### When Working on This Project

**User asks for documentation / wants to track changes:**

1. **Update CHANGELOG.md** (append to top)
   - Add date header: `## 2025-11-05`
   - List what changed (bullet points)
   - Keep it under 100 lines total (trim old entries)

2. **Update .claude/ files if architecture changes:**
   - PROJECT_CONTEXT.md - Only if major project state change
   - FIXES_APPLIED.md - Add one-line summary of fix
   - CODE_PATTERNS.md - Only if new pattern established

3. **For detailed session work:**
   - Create `.archive/sessions/YYYY-MM-DD-topic.md`
   - Example: `.archive/sessions/2025-11-05-inventory-fix.md`
   - This is for historical reference only

**NEVER create**:
- `NEW_FEATURE_DOCS.md` in root ❌
- `BUGFIX_SUMMARY.md` in root ❌
- `SESSION_NOTES.md` in root ❌
- Any other .md in root ❌

**ALWAYS use**:
- `CHANGELOG.md` for recent changes ✅
- `.archive/sessions/DATE-topic.md` for details ✅

---

## Update Patterns

### Small Bug Fix
```markdown
# CHANGELOG.md (just append)
## 2025-11-06
### Fixed
- Menu now hides during pauses (cow_interaction.py:540)
```

### New Feature
```markdown
# CHANGELOG.md
## 2025-11-06
### Added
- Weapon upgrade comparison system
- Shows upgrade indicator in shop

# .claude/FIXES_APPLIED.md (one line)
2025-11-06: Weapon upgrade system - shop.py:123

# .archive/sessions/2025-11-06-weapon-upgrades.md (detailed work)
(Full detailed documentation)
```

### Architecture Change
```markdown
# CHANGELOG.md
## 2025-11-06
### Changed
- Refactored combat system into combat_manager.py

# .claude/PROJECT_CONTEXT.md (update key files section)
- combat_manager.py - NEW - Handles all combat logic

# .claude/CODE_PATTERNS.md (add new pattern if applicable)
### Combat Pattern
(example of new pattern)
```

---

## Enforcement Mechanism

### Claude Instructions (Auto-loaded)

When Claude starts a session, it reads:
1. `.claude/RULES.md` (this file) - First thing read
2. `.claude/PROJECT_CONTEXT.md` - Project state
3. `.claude/CODE_PATTERNS.md` - How to code

**Rule #1 in this file**: Don't create .md files in root!

Claude will follow this automatically because it reads rules on load.

---

## Document Lifecycle

### Creation
```
New work needed
    ↓
Update CHANGELOG.md (user-facing summary)
    ↓
Create .archive/sessions/DATE-topic.md (detailed notes)
    ↓
Update .claude/* ONLY if patterns/architecture changed
```

### Maintenance
- **CHANGELOG.md**: Keep last 3-6 months, trim older
- **.claude/***: Update when architecture changes
- **.archive/sessions/***: Keep forever, never trim

### Deletion
- **Never delete** .archive/ files (history)
- **Trim** CHANGELOG.md when > 200 lines (keep recent only)
- **Don't delete** .claude/ files (permanent patterns)

---

## File Size Limits

To prevent bloat:

- `README.md`: Max 100 lines
- `CHANGELOG.md`: Max 200 lines (trim old entries)
- `.claude/PROJECT_CONTEXT.md`: Max 150 lines
- `.claude/FIXES_APPLIED.md`: Max 100 lines
- `.claude/CODE_PATTERNS.md`: Max 100 lines
- `.archive/sessions/*`: No limit (archived)

**When limit reached**: Trim oldest content, move to archive if needed

---

## Examples of Correct Behavior

### ✅ User: "Document this bug fix"
**Claude should**:
```bash
# Update CHANGELOG.md
echo "### Fixed\n- Bug description (file:line)" >> CHANGELOG.md

# Create detailed notes in archive
cat > .archive/sessions/2025-11-06-bugfix.md << EOF
(detailed documentation)
EOF
```

### ✅ User: "Track this session's work"
**Claude should**:
```bash
# Update CHANGELOG.md with summary
# Create .archive/sessions/DATE-SESSION.md with details
# Update .claude/FIXES_APPLIED.md with one-liner
```

### ❌ User: "Create documentation"
**Claude should NOT**:
```bash
# WRONG - Don't do this!
cat > DOCUMENTATION.md << EOF  # ← ROOT DIRECTORY!
EOF
```

**Claude should instead**:
```bash
# CORRECT - Use the system
# Update CHANGELOG.md with summary
# Put details in .archive/sessions/
```

---

## Auto-Reminder System

### Add to .claude/PROJECT_CONTEXT.md

At the top of PROJECT_CONTEXT.md:
```markdown
**DOCUMENTATION RULE**:
- Root: Only README.md and CHANGELOG.md
- Details: .archive/sessions/DATE-topic.md
- Never create .md files in root directory!
```

This reminds Claude every session to follow the rules.

---

## Summary

**The System**:
1. Root: 2 .md files only (README + CHANGELOG)
2. .claude/: 3 context files (auto-read on load)
3. .archive/: All detailed docs (searchable, hidden)

**The Prevention**:
1. .claude/RULES.md (this file) - Read first by Claude
2. Explicit instructions in PROJECT_CONTEXT.md
3. Clear patterns for where docs go
4. File size limits enforce trimming

**The Result**:
- Clean root directory forever
- No .md sprawl
- Claude always knows where docs go
- You only see what matters

---

**Status**: System designed, ready to implement
