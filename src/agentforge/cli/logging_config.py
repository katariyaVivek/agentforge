import logging
import sys
from typing import Optional


def configure_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO

    format_str = "%(levelname)s: %(message)s"

    logging.basicConfig(level=level, format=format_str, stream=sys.stdout)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
