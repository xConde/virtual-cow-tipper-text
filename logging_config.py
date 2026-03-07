"""
Logging configuration for Virtual Cow Tipper.

All log output goes to a file — never stdout/stderr (which would corrupt curses).
"""
import logging
import os

LOG_DIR = "logs"
LOG_FILE = "game.log"
MAX_LOG_BYTES = 1_000_000  # 1MB
BACKUP_COUNT = 3


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return the game logger.

    Logs to logs/game.log with rotation. Safe to call multiple times —
    returns the same logger instance.
    """
    logger = logging.getLogger("vct")

    # Only configure once
    if logger.handlers:
        return logger

    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, LOG_FILE)

    from logging.handlers import RotatingFileHandler
    handler = RotatingFileHandler(
        log_path,
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def get_logger(name: str = "vct") -> logging.Logger:
    """Get a child logger. Call setup_logging() first."""
    return logging.getLogger(name)
