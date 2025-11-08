# Instructions for Claude Code Sessions

**READ THESE FILES ON EVERY SESSION START** (in this order):

1. `.claude/RULES.md` - Documentation rules (prevents .md sprawl)
2. `.claude/PROJECT_CONTEXT.md` - Project state and architecture
3. `.claude/FIXES_APPLIED.md` - What's been fixed
4. `.claude/CODE_PATTERNS.md` - How to code correctly

---

## Session Workflow

### Starting a Session
1. Read the 4 files above
2. Understand current project state
3. Know what patterns to follow
4. Know where documentation goes

### During a Session
- Follow patterns in CODE_PATTERNS.md
- Use constants from game_config.py
- Use helpers from game_helpers.py
- Don't create .md files in root (RULES.md explains)

### Ending a Session
1. Update `CHANGELOG.md` with user-facing summary
2. Add one-liner to `FIXES_APPLIED.md` if fixes applied
3. Create `.archive/sessions/YYYY-MM-DD-topic.md` for detailed work
4. Update PROJECT_CONTEXT.md only if major architecture changed

---

## Critical Rules

**NEVER**:
- ❌ Create .md files in root directory
- ❌ Use print() or safe_print() in curses mode
- ❌ Add magic numbers (use game_config.py)
- ❌ Duplicate code (use game_helpers.py)

**ALWAYS**:
- ✅ Update CHANGELOG.md with changes
- ✅ Use pause_with_prompt() for continuation prompts
- ✅ Use draw_dialog() for all user-facing text
- ✅ Follow patterns in CODE_PATTERNS.md

---

## Quick Reference

**Where to put things**:
- User changes → CHANGELOG.md
- Detailed work → .archive/sessions/DATE-topic.md
- Code constants → game_config.py
- Helper functions → game_helpers.py
- Code → Appropriate .py file

**How to code**:
- See CODE_PATTERNS.md for all patterns
- See FIXES_APPLIED.md for known fixes
- See PROJECT_CONTEXT.md for file purposes

---

**This system prevents documentation sprawl automatically** because:
1. Rules are read on every session
2. Clear guidelines on where docs go
3. Root directory is protected (only 2 .md files)
4. Archive system keeps history without clutter
