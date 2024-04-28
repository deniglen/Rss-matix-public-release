import logging
import os
from .path_module import LOG_FILE_PATH, CONFIG_FILE_PATH
from configparser import ConfigParser

# Skipping adding this to gui. Manual configuration needed.
config_parser = ConfigParser()
config_parser.read(CONFIG_FILE_PATH)
#if not config is setup already, handle it.
try:
    logger_activated = config_parser.getboolean("log_mode", "logger_activated")
except Exception as e:
    print(f"Error when tried reading log mode: {e}, defaults to logging off")
    logger_activated = False


current_dir = os.path.dirname(__file__)
current_dir_where_run_from = os.getcwd()

# Create a logger


def setup_logger(name=__name__):
    logger = logging.getLogger(name)

# Set the logging level
    if not logger_activated:
        logger.disabled = True
    else:
        logger.setLevel(logging.INFO)

    # Create a FileHandler to write log messages to a file
    file_handler = logging.FileHandler(LOG_FILE_PATH)

    # Create a StreamHandler to write log messages to the console
    stream_handler = logging.StreamHandler()

    # Create a Formatter to specify the format of the log messages
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Add the Formatter to the FileHandler and StreamHandler objects
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add the FileHandler and StreamHandler to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info(current_dir_where_run_from)
    # Return logger object for usage in other modules

    return logger


if __name__ == "__main__":
    pass
    # logger = setup_logger()
