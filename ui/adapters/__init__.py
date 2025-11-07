"""
UI Adapters package.
"""

from .curses_adapter import CursesAdapter

# Only import TextualAdapter if textual is available
try:
    from .textual_adapter import TextualAdapter
    __all__ = ['CursesAdapter', 'TextualAdapter']
except ImportError:
    # Textual not available, only expose CursesAdapter
    __all__ = ['CursesAdapter']
    TextualAdapter = None
