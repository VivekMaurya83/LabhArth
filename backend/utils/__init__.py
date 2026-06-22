"""
LabhArth AI — Utility Package
===============================
Shared utilities: configuration, logging, and helpers.
"""

from backend.utils.config import get_settings
from backend.utils.logger import logger, setup_logger

__all__ = ["get_settings", "logger", "setup_logger"]
