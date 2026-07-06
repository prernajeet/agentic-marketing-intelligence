"""
config/logging_config.py
==========================
Centralized logging setup for the entire platform.

Every module (nodes, ml, analytics, api, llm, etc.) should obtain its
logger via `get_logger(__name__)` rather than configuring logging
independently. This guarantees consistent formatting, log levels,
and output destinations (console + rotating file) across the app.
"""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger as _loguru_logger

from config.settings import settings

_LOG_DIR = settings.project_root / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)

_CONFIGURED = False


def _configure_once() -> None:
    """Configure loguru sinks exactly once per process."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    _loguru_logger.remove()  # remove default handler

    # Console sink
    _loguru_logger.add(
        sys.stdout,
        level=settings.log_level.upper(),
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )

    # Rotating file sink
    _loguru_logger.add(
        _LOG_DIR / "app.log",
        level=settings.log_level.upper(),
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    _CONFIGURED = True


def get_logger(name: str):
    """
    Factory that returns a loguru logger bound with a module name.

    Usage:
        from config.logging_config import get_logger
        logger = get_logger(__name__)
        logger.info("Data Retrieval Node started")
    """
    _configure_once()
    return _loguru_logger.bind(module=name)
