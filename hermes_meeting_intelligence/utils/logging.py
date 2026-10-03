"""
Logging and Utility helpers for Hermes Meeting Intelligence.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Optional


def setup_logger(name: str = "hermes_meeting", level: Optional[str] = None) -> logging.Logger:
    raw_level = level or os.getenv("HERMES_LOG_LEVEL", "INFO") or "INFO"
    log_level = getattr(logging, raw_level.upper(), logging.INFO)
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        logger.addHandler(handler)

    return logger
