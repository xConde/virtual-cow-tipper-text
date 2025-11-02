# Current Terminal Requirements (Curses Implementation)

**Last Updated:** Pre-migration baseline (Task 0)

## Terminal Specifications

### Size Requirements
- **Width:** 85 characters (reduced from 100 for better margins)
- **Height:** 30 lines
- **Minimum Size:** 85x30 (fixed, non-responsive)

### Margins
- **Left Margin:** 2 characters
- **Right Margin:** 2 characters
- **Effective Display Area:** 81 characters wide

## Screen Layout (Y-coordinates)

### Header Section (Lines 0-4)
- **Line 0-2:** Player Info (left) | Cow Info (right at x=50)
- **Line 2:** Game Title (centered)
- **Line 4:** Separator line

### Main Display Area (Lines 5-19)
- **Lines 5-19:** ASCII Art / Combat Display Area
- **Total Height:** 14 lines for dynamic content

### Dialogue Section (Lines 20-21)
- **Lines 20-21:** Dialogue text (word-wrapped, max 2 lines)
- **Max Width:** 81 characters (with margins)

### Instructions Section (Lines 22-23)
- **Lines 22-23:** Instruction prompts
- **Height:** 1-2 lines

### Input Section (Line 24)
- **Line 24:** User input prompt

### Menu Section (Lines 25-28)
- **Lines 25-28:** Menu items
- **Max Items:** 3 visible items
- **Height:** 4 lines

## Curses Configuration

### Display Settings
- **Echo:** Disabled (`curses.noecho()`)
- **Break:** Enabled (`curses.cbreak()`)
- **Cursor:** Hidden (`curses.curs_set(0)`)
- **Keypad:** Enabled for arrow keys (`stdscr.keypad(True)`)

### Input Handling
- **Method:** `stdscr.getch()` blocking
- **Arrow Keys:** Curses constants (KEY_UP, KEY_DOWN)
- **Enter:** `ord('\n')`
- **Escape:** ASCII 27
- **Number Keys:** ASCII offset 49 (for menu selection)

## Color Support
- **Current Implementation:** No colors used
- **Style:** Plain ASCII text only
- **Attributes:** Basic (REVERSE for selection, BOLD for titles)

## Terminal Compatibility

### Tested Terminals
- macOS Terminal.app (primary development)
- iTerm2
- Standard UNIX terminals

### Known Issues
- Fixed size may not work on small terminals
- No graceful degradation for smaller screens
- No color support currently implemented

## Text Rendering

### Word Wrapping
- **Dialogue:** Automatic word wrap to fit 81-character width
- **Method:** Manual word-by-word wrapping in `draw_dialog()`
- **Max Lines:** 2 lines for dialogue

### Text Alignment
- **Left:** Default (with left margin)
- **Right:** Calculated from WIDTH - text_length - RIGHT_MARGIN
- **Center:** (WIDTH - text_length) // 2

### Text Truncation
- **Method:** Truncate with "..." if exceeds max width
- **Applied:** All text through `draw()` method

## Mouse Support
- **Menu Navigation:** Enabled via `curses.mousemask()`
- **Usage:** Limited to menu interactions
- **Disabled:** During most gameplay

## Performance Characteristics
- **Refresh Method:** `os.system('clear')` or `os.system('cls')`
- **Update Strategy:** Full screen clear + redraw
- **No Optimization:** Complete refresh on each update

## Limitations of Current Implementation
1. Fixed terminal size (no responsive design)
2. Manual coordinate management throughout codebase
3. No color support
4. Limited to ASCII art only
5. Full screen refresh (inefficient)
6. Hardcoded layout positions
7. No support for terminal resize events
8. Text overflow handled by truncation only

## Migration Goals
The new Textual implementation should address these limitations:
- Responsive layout adapting to terminal size
- Automatic layout management (no manual coordinates)
- Rich color support with theming
- Efficient partial updates
- Better text rendering with automatic wrapping
- Support for terminal resize events
- Minimum size: 80x24 (standard terminal)
