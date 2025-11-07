# Virtual Cow Tipper - Issues Checklist

## Critical Issues (Application Won't Run)

- [ ] **Issue #1**: `ui/adapters/textual_adapter.py:47`
  - `await self.app.run_async()` - method doesn't exist
  - Should use `asyncio.create_task()` or different initialization

- [ ] **Issue #2**: `ui/textual_app.py:184`
  - `await super().push_screen(screen)` - push_screen is NOT async
  - Should be `self.push_screen(screen)` or refactor to sync

- [ ] **Issue #3**: `ui/adapters/textual_adapter.py:28-39`
  - App initialization incomplete - not actually running
  - Need proper Textual app lifecycle management

- [ ] **Issue #4**: `ui/adapters/textual_adapter.py:97-139`
  - `show_menu()` waits on `_response_queue.get()`
  - But nothing ever calls `send_response()` from UI screens
  - Menus will timeout

- [ ] **Issue #5**: `main_ui.py:150-174`
  - `run_game()` is a placeholder with no actual game logic
  - Game never runs, just shows a message

## High Priority Issues (Game Won't Function)

- [ ] **Issue #6**: `game.py:64-71`
  - Game logic is fully synchronous
  - `main_ui.py` is fully asynchronous
  - Mismatch prevents integration

- [ ] **Issue #7**: `ui/game_ui_bridge.py:102-111`
  - `send_event_sync()` uses `asyncio.create_task()` without event loop
  - Will fail if called from sync game code

- [ ] **Issue #8**: `ui/textual_app.py:36`
  - `CSS_PATH = "styles/main.css"` - file doesn't exist
  - App will crash trying to load CSS

- [ ] **Issue #9**: `main_ui.py:34-39`
  - TextualAdapter registration conditional on import
  - Better error handling needed if --textual requested but Textual not available

- [ ] **Issue #10**: `ui/adapters/curses_adapter.py:316-328`
  - `on_pause()` calls sync `pause()` method
  - Async method calling sync method is problematic

## Functional Gaps (Missing Implementation)

- [ ] **Gap #1**: `ui/textual_app.py:346-352`
  - `GameScreen._start_game()` - TODO: Connect to actual game logic

- [ ] **Gap #2**: `ui/textual_app.py:417`
  - `CombatScreen.on_button_pressed()` - TODO: Implement combat logic

- [ ] **Gap #3**: `ui/textual_app.py:435`
  - `ShopScreen.compose()` - TODO: Generate from actual shop items

- [ ] **Gap #4**: `ui/textual_app.py:562`
  - `CareerScreen.compose()` - TODO: Load actual career stats

- [ ] **Gap #5**: `ui/textual_app.py:626`
  - `SaveGameScreen.on_mount()` - TODO: Implement actual save

- [ ] **Gap #6**: `ui/textual_app.py:640`
  - `LoadGameScreen.compose()` - TODO: Show actual save files

- [ ] **Gap #7**: `ui/textual_app.py:664`
  - `SavePromptScreen.on_button_pressed()` - TODO: Save game

- [ ] **Gap #8**: `ui/textual_app.py:609`
  - `DialogueScreen.on_button_pressed()` - TODO: Send choice back to game logic

## Import/Path Issues

- [ ] **Issue #11**: `ui/adapters/textual_adapter.py:9`
  - `sys.path.insert(0, '.')` - working directory dependency
  - Will fail if run from different directory

## Missing Files

- [ ] CSS file: `styles/main.css` or `ui/styles/main.css`
  - Referenced by `ui/textual_app.py:36`
  - App will fail to load without it

## Verification Checklist

### What Works:
- [x] `main.py` entry point - original game with curses UI
- [x] `game.py` - game logic (when used with main.py)
- [x] `terminal/game_terminal.py` - curses terminal wrapper
- [x] `ui/ui_factory.py` - UI factory pattern
- [x] `ui/interfaces/base_ui.py` - interface design
- [x] Imports - basic imports work (except Textual when not installed)

### What Doesn't Work:
- [ ] `main_ui.py` - new entry point (async/incomplete)
- [ ] `ui/adapters/textual_adapter.py` - Textual adapter (run_async issue)
- [ ] `ui/textual_app.py` - Textual application (multiple issues)
- [ ] Game integration with new UI - not connected
- [ ] Textual mode - would crash on startup

## Testing Status

| Component | Test | Status |
|-----------|------|--------|
| main.py | `python main.py` | ✓ Works |
| main_ui.py --curses | `python main_ui.py --curses` | ✗ Hangs/crashes |
| main_ui.py --textual | `python main_ui.py --textual` | ✗ Crashes (no run_async) |
| UIFactory imports | Python imports | ✓ Works |
| CursesAdapter | Initialize | ✓ Works |
| TextualAdapter | Initialize | ✗ Breaks (Textual not installed) |
| GameUIBridge | Create/start | ✗ Issues with event loop |

## Fix Priority

1. **FIRST** (Blocking):
   - Remove `run_async()` call
   - Fix `push_screen()` async issue
   - Implement response queue population
   - Create CSS file

2. **SECOND** (Critical):
   - Decide game integration strategy
   - Fix async/sync mismatches
   - Connect actual game logic

3. **THIRD** (Important):
   - Implement all TODOs
   - Fix imports and paths
   - Add error handling

## Notes for Developer

- Original `main.py` works perfectly - use as reference
- New `main_ui.py` is architecturally good but execution has critical flaws
- Choose one approach: sync game in thread OR async game conversion
- Most issues are fixable in 4-6 hours for critical items
- Full implementation would take 10-15 hours
