"""
logger_setup.py

Shared logging setup for the Spotify playlist automator.

The AHK launcher runs everything through pythonw.exe so no console
window ever appears. That means print() output goes nowhere, so
instead every script here logs to a file next to the code. Check
playlist_automator.log if something isn't working.
"""

import logging
import os

# Log file lives next to the scripts so it's easy to find
LOG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "playlist_automator.log"
)


def get_logger(name):
    """
    Returns a logger that writes timestamped lines to LOG_PATH.
    Safe to call repeatedly (from both scripts) without duplicating
    handlers.
    """
    logger = logging.getLogger(name)

    # Only attach a handler once, even if this gets called again
    if not logger.handlers:
        handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
