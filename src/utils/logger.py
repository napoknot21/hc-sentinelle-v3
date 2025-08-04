import logging, os
from datetime import datetime

from src.config.paths import LOG_DIR
os.makedirs(LOG_DIR, exist_ok=True)


def get_logger (name: str = "sentinelle") -> logging.Logger:
    """
    Create or retrieve a logger with a given name.

    Logs are written both to the console and to a rotating daily log file.

    Args:
        name (str): Logger name (used to identify the module or context).

    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers :

        # Format for log messages
        formatter = logging.Formatter(
            fmt="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File handler
        date_str = datetime.now().strftime("%Y-%m-%d")
        LOG_FILE_NAME=os.path.join(LOG_DIR, f"sentinelle_{datetime.now().strftime('%Y-%m-%d')}.log")
        file_handler = logging.FileHandler(LOG_FILE_NAME)

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler
        #console_handler = logging.StreamHandler()
        #console_handler.setFormatter(formatter)

        #logger.addHandler(console_handler)

    return logger


def log (message: str, level: str = "info", module: str = "sentinelle"):
    """
    Log a message with the desired log level and module name.

    Args:
        message (str): The log message.
        level (str): Logging level ("info", "debug", "warning", "error", "critical").
        module (str): Logger name or module name.
    """
    logger = get_logger(module)

    level = level.lower()

    if level == "debug" :
        logger.debug(message) # [*]

    elif level == "warning" :
        logger.warning(message) # [!]

    elif level == "error" :
        logger.error(message) # [-]

    elif level == "critical" :
        logger.critical(message) # [-]

    else :
        logger.info(message) # [+] or [*]