
from configparser import ConfigParser
from .logging_setup import setup_logger
from .path_module import CONFIG_FILE_PATH

logger = setup_logger(__name__)


#### TIMEFUNCTIONS RELATED TO RSS-FEEDS####
def set_time(tidvariable):
    tidvariable = str(tidvariable)
    file = CONFIG_FILE_PATH
    config = ConfigParser()
    config.read(file)
    config.set('sleep', '1', tidvariable)
    with open(CONFIG_FILE_PATH, "w+") as cfgfile:
        config.write(cfgfile)


# Refactor this to "start, minutes, string" excluding the last to chars 60.00 (00 should not be included)
def convert_time_value_menu():
    TimeValueStart = read_time()
    TimeValueStart = int(TimeValueStart)/60
    TimeValueStart = str(TimeValueStart)
    TimeValueStart = TimeValueStart[:-2]
    logger.info(f'printar tidsintervall minuter: {TimeValueStart}')
    return TimeValueStart


def read_time():
    file = CONFIG_FILE_PATH
    config = ConfigParser()
    config.read(file)
    valuetest = config.get('sleep', '1')
    return valuetest


if __name__ == "__main__":
    # set_time(60)
    pass
