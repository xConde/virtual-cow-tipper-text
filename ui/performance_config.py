"""
Performance configuration for Virtual Cow Tipper Textual UI.
Optimizes rendering, caching, and event handling.
"""

from typing import Dict, Any


class PerformanceConfig:
    """Performance tuning parameters for the Textual UI."""

    # ==================== Rendering Optimization ====================

    # Maximum FPS for UI updates
    MAX_FPS = 60

    # Minimum time between screen refreshes (ms)
    MIN_REFRESH_INTERVAL = 16  # ~60 FPS

    # Enable dirty region tracking
    ENABLE_DIRTY_TRACKING = True

    # Maximum number of widgets to render per frame
    MAX_WIDGETS_PER_FRAME = 100

    # ==================== Event Optimization ====================

    # Event queue size limit
    MAX_EVENT_QUEUE_SIZE = 1000

    # Event debounce time (ms)
    EVENT_DEBOUNCE_MS = 50

    # Maximum events to process per frame
    MAX_EVENTS_PER_FRAME = 10

    # Event priorities (lower = higher priority)
    EVENT_PRIORITIES = {
        'input': 1,
        'combat': 2,
        'ui_update': 3,
        'animation': 4,
        'background': 5
    }

    # ==================== Memory Optimization ====================

    # Maximum cached screens
    MAX_CACHED_SCREENS = 5

    # Maximum log entries to keep
    MAX_LOG_ENTRIES = 100

    # Maximum combat log messages
    MAX_COMBAT_LOG = 50

    # Clear old data after (seconds)
    CACHE_EXPIRY_TIME = 300  # 5 minutes

    # ==================== Animation Optimization ====================

    # Enable animations
    ENABLE_ANIMATIONS = True

    # Reduce animations on slow systems
    ADAPTIVE_QUALITY = True

    # Animation frame skip threshold (ms)
    ANIMATION_SKIP_THRESHOLD = 32  # Skip frames if > 32ms

    # Maximum concurrent animations
    MAX_CONCURRENT_ANIMATIONS = 5

    # ==================== Network/IO Optimization ====================

    # Save game debounce (ms)
    SAVE_DEBOUNCE_MS = 1000

    # Auto-save interval (seconds)
    AUTO_SAVE_INTERVAL = 60

    # Async IO timeout (seconds)
    ASYNC_IO_TIMEOUT = 5

    # ==================== CSS Optimization ====================

    # CSS cache size
    CSS_CACHE_SIZE = 100

    # Precompile CSS selectors
    PRECOMPILE_CSS = True

    # CSS hot reload in debug mode
    CSS_HOT_RELOAD = False

    # ==================== Profiling Configuration ====================

    # Enable performance profiling
    ENABLE_PROFILING = False

    # Profile sample rate (1 = every frame, 10 = every 10th frame)
    PROFILE_SAMPLE_RATE = 10

    # Performance warning thresholds (ms)
    PERF_WARNING_THRESHOLDS = {
        'frame_time': 16,      # Warn if frame takes > 16ms
        'event_processing': 5,  # Warn if event takes > 5ms
        'render_time': 10,     # Warn if render takes > 10ms
    }

    @classmethod
    def get_optimized_config(cls) -> Dict[str, Any]:
        """
        Get optimized configuration based on system capabilities.

        Returns:
            Dictionary of performance settings
        """
        import platform

        config = {}

        # Check system resources
        try:
            import psutil
            cpu_count = psutil.cpu_count()
            memory_gb = psutil.virtual_memory().total / (1024**3)
        except ImportError:
            # Fallback if psutil not available
            import os
            cpu_count = os.cpu_count() or 2
            memory_gb = 4  # Assume 4GB as default

        # Adjust based on system capabilities
        if cpu_count >= 4 and memory_gb >= 8:
            # High-end system
            config['quality'] = 'high'
            config['max_fps'] = 60
            config['enable_animations'] = True
            config['max_widgets'] = 200
        elif cpu_count >= 2 and memory_gb >= 4:
            # Mid-range system
            config['quality'] = 'medium'
            config['max_fps'] = 30
            config['enable_animations'] = True
            config['max_widgets'] = 100
        else:
            # Low-end system
            config['quality'] = 'low'
            config['max_fps'] = 15
            config['enable_animations'] = False
            config['max_widgets'] = 50

        # Platform-specific optimizations
        system = platform.system()
        if system == 'Windows':
            config['terminal_optimization'] = 'windows_terminal'
        elif system == 'Darwin':  # macOS
            config['terminal_optimization'] = 'macos_terminal'
        else:  # Linux/Unix
            config['terminal_optimization'] = 'unix_terminal'

        return config

    @classmethod
    def apply_optimizations(cls, app) -> None:
        """
        Apply performance optimizations to a Textual app.

        Args:
            app: Textual application instance
        """
        config = cls.get_optimized_config()

        # Apply FPS limit
        if hasattr(app, 'target_fps'):
            app.target_fps = config['max_fps']

        # Configure animation settings
        if not config['enable_animations']:
            # Disable animations for low-end systems
            app.animate = False

        # Set render limits
        if hasattr(app, 'max_widgets_per_frame'):
            app.max_widgets_per_frame = config['max_widgets']

        # Enable/disable features based on quality
        if config['quality'] == 'low':
            # Disable expensive features
            cls.ENABLE_DIRTY_TRACKING = False
            cls.ENABLE_ANIMATIONS = False
            cls.CSS_HOT_RELOAD = False

        return config


class PerformanceMonitor:
    """Monitor and report performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = {
            'frame_times': [],
            'event_times': [],
            'render_times': [],
            'memory_usage': []
        }
        self.enabled = PerformanceConfig.ENABLE_PROFILING

    def start_frame(self) -> None:
        """Mark the start of a frame."""
        if not self.enabled:
            return

        import time
        self.frame_start = time.perf_counter()

    def end_frame(self) -> None:
        """Mark the end of a frame and record metrics."""
        if not self.enabled:
            return

        import time
        frame_time = (time.perf_counter() - self.frame_start) * 1000  # Convert to ms
        self.metrics['frame_times'].append(frame_time)

        # Keep only last 100 samples
        if len(self.metrics['frame_times']) > 100:
            self.metrics['frame_times'].pop(0)

        # Check for performance warnings
        if frame_time > PerformanceConfig.PERF_WARNING_THRESHOLDS['frame_time']:
            self.log_warning(f"Slow frame: {frame_time:.2f}ms")

    def log_warning(self, message: str) -> None:
        """Log a performance warning."""
        import logging
        logging.warning(f"[PERF] {message}")

    def get_stats(self) -> Dict[str, float]:
        """
        Get performance statistics.

        Returns:
            Dictionary of performance metrics
        """
        if not self.metrics['frame_times']:
            return {}

        import statistics

        return {
            'avg_frame_time': statistics.mean(self.metrics['frame_times']),
            'max_frame_time': max(self.metrics['frame_times']),
            'min_frame_time': min(self.metrics['frame_times']),
            'fps': 1000 / statistics.mean(self.metrics['frame_times']) if self.metrics['frame_times'] else 0
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()