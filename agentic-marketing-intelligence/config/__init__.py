"""
config package
================
Centralized application configuration for the Agentic AI-Powered
Marketing Intelligence & Decision Support Platform.

Exposes:
    settings         -> singleton Settings instance (env-driven)
    get_logger       -> factory for module-level loggers
    constants        -> static enums/constants used across the app
"""

from config.settings import settings
from config.logging_config import get_logger

__all__ = ["settings", "get_logger"]
