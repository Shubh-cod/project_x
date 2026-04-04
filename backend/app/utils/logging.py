import logging
import sys
from app.config import get_settings

settings = get_settings()

def setup_logging():
    """Configure standard logging for the application."""
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    
    # Default level is INFO, but DEBUG if settings.debug is true
    level = logging.DEBUG if settings.debug else logging.INFO
    
    # Unified configuration
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True  # Ensure we override any previous basicConfig
    )

    # Specific logger for the app
    logger = logging.getLogger("novacrm")
    logger.setLevel(level)
    
    return logger

# Create the standard logger instance to be imported elsewhere
logger = logging.getLogger("novacrm")
