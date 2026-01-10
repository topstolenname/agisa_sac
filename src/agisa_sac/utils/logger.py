"""Logging configuration and utilities for AGI-SAC.

This module provides a unified logging system that replaces print statements
and warnings throughout the codebase. It supports:
- Environment-based log level configuration
- Console and file output
- Structured JSON logging for production
- Rich formatting for development
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional, cast

# Default log format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - "
    "[%(filename)s:%(lineno)d] - %(message)s"
)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


def get_log_level() -> int:
    """Get log level from environment variable.

    Returns:
        Log level (defaults to INFO if not set or invalid)
    """
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_name, logging.INFO)


def setup_logging(
    level: Optional[int] = None,
    log_file: Optional[Path] = None,
    json_format: bool = False,
    verbose: bool = False,
) -> None:
    """Configure logging for the entire application.

    Args:
        level: Log level (if None, reads from LOG_LEVEL env var)
        log_file: Optional file path for persistent logging
        json_format: Use JSON formatting (recommended for production)
        verbose: Enable detailed formatting with file/line info
    """
    if level is None:
        level = get_log_level()

    # Remove any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    console_formatter: logging.Formatter
    if json_format:
        console_formatter = JsonFormatter()
    else:
        format_string = DETAILED_FORMAT if verbose else DEFAULT_FORMAT
        console_formatter = logging.Formatter(format_string)

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # Always use JSON for file logging
        file_formatter = (
            JsonFormatter()
            if json_format
            else logging.Formatter(DETAILED_FORMAT)
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Convenience function for quick setup
def configure_simple_logging(verbose: bool = False) -> None:
    """Quick logging setup for CLI tools.

    Args:
        verbose: Enable verbose output (DEBUG level with detailed format)
    """
    level = logging.DEBUG if verbose else get_log_level()
    setup_logging(level=level, verbose=verbose)
