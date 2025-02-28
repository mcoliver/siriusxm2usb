import logging
import sys
from pathlib import Path
from typing import Optional

try:
    import colorlog
except ImportError:
    print("colorlog not found. Install with: pip install colorlog")
    sys.exit(1)

# Create a module-level logger
logger = logging.getLogger('siriusxm2usb')

def setup_logging(log_file: Optional[Path] = None, debug: bool = False) -> logging.Logger:
    """Configure logging with colors to both stdout and optionally a file."""
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Remove any existing handlers
    logger.handlers = []

    # Color formatter for console output
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s %(levelname)-8s%(reset)s %(cyan)s%(name)s%(reset)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={
            'name': {
                'DEBUG':    'cyan',
                'INFO':     'cyan',
                'WARNING':  'cyan',
                'ERROR':    'cyan',
                'CRITICAL': 'cyan',
            }
        }
    )

    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler if specified (without colors)
    if log_file:
        # Create parent directories if they don't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Plain formatter without color codes for file output
        file_formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: The name of the logger. If None, returns the root siriusxm2usb logger.
    
    Returns:
        A configured logger instance.
    """
    if name:
        return logging.getLogger(f'siriusxm2usb.{name}')
    return logger
