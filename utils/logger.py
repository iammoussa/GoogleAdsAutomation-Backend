"""
Logging configurato con loguru
"""

import sys
from loguru import logger
from pathlib import Path
from config.settings import settings

# Crea cartella logs se non esiste
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Rimuovi handler di default
logger.remove()

# Console output (colorato)
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True,
)

# File output (tutto)
logger.add(
    settings.LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
)

# File output (solo errori)
logger.add(
    "logs/errors.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="10 MB",
    retention="90 days",
    compression="zip",
)


def get_logger(name: str):
    """
    Ottiene un logger con il nome specificato
    
    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Test message")
    """
    return logger.bind(name=name)
