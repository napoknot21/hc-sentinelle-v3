from __future__ import annotations

import os
import logging
import datetime as dt

from src.config.paths import LOGS_DIR_REL_PATH


def log (message : str, level: str = "info", module: str = "sentinelle") :
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
        logger.debug(message)  # [*]

    elif level == "warning" :
        logger.warning(message)  # [!]

    elif level == "error" :
        logger.error(message)  # [-]

    elif level == "critical" :
        logger.critical(message)  # [-]

    else :
        logger.info(message)  # [+] or [*]

    print(f"\n{message}")


def get_logger(name: str = "sentinelle") -> logging.Logger :
    """
    Create or retrieve a logger with a given name.

    Logs are written both to the console and to a daily log file.
    Automatically switches to a new file when the day changes.

    Args:
        name (str): Logger name (used to identify the module or context).

    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    logger.propagate = False

    # Vérifier si on doit changer de fichier (nouveau jour)
    today = dt.datetime.now().strftime('%d-%m-%Y')
    
    if logger.handlers :

        # Vérifier si la date a changé
        current_handler = logger.handlers[0]
        
        if hasattr(current_handler, '_log_date') and current_handler._log_date == today :
            return logger
        
        else :

            # Nouveau jour : fermer l'ancien handler et créer un nouveau
            for handler in logger.handlers[:]:
            
                handler.close()
                logger.removeHandler(handler)
    
    # Format for log messages
    formatter = logging.Formatter(

        fmt="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    
    )

    # File handler
    os.makedirs(LOGS_DIR_REL_PATH, exist_ok=True)

    # Nom de fichier avec la date du jour au format dd-mm-yyyy
    filename = f"sentinelle_{today}.log"
    LOG_FILE_NAME = os.path.join(LOGS_DIR_REL_PATH, filename)

    file_handler = logging.FileHandler(
    
        filename=LOG_FILE_NAME,
        encoding="utf-8"
    
    )
    
    # Stocker la date pour vérification future
    file_handler._log_date = today

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger