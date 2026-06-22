"""
LabhArth AI — Logging Setup
============================
Structured logging with configurable levels.
Uses Python's built-in logging with rich formatting.
"""

import logging
import sys
from typing import Optional

from backend.utils.config import get_settings


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Create and configure a logger instance.

    Args:
        name: Logger name. Defaults to 'labharth'.

    Returns:
        Configured logger instance.
    """
    settings = get_settings()
    logger_name = name or "labharth"
    logger = logging.getLogger(logger_name)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Console handler with structured format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Default application logger
logger = setup_logger("labharth")
