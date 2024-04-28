from .logging_setup import setup_logger
from configparser import ConfigParser
from .path_module import CONFIG_FILE_PATH
from .path_module import RSS_LOG_FILE_PATH


logger = setup_logger(__name__)
config = ConfigParser()

#### READ / WRITE entries functions from txt####
def write_entries_reader(Entries):
    try:
        with open(RSS_LOG_FILE_PATH, "r+") as inst:
            inst.read()
            inst.write(f'{Entries}\n')
            logger.info(f'Skrivit entry: {Entries}')
    except:
        # Creates file or truncate if error
        start_exit_program_truncate_txt()


def read_entries_tkinter(last_line_num):
    try:
        with open(RSS_LOG_FILE_PATH, "r") as inst:
            lines = inst.readlines()
            content = lines[last_line_num:]
            return content, len(lines)
    except:
        # creates file or truncate if error
        content = start_exit_program_truncate_txt()
        return content, last_line_num


def fetch_last_entry_line_num() -> int:
    try:
        with open(RSS_LOG_FILE_PATH, 'r') as entry_log:
            lines = entry_log.readlines()
            return len(lines)
    except:
        start_exit_program_truncate_txt()


def read_all_entries_tkinter():
    try:
        with open(RSS_LOG_FILE_PATH, "r") as inst:
            content = inst.readlines()[1:]
            return content
    except:
        pass


def start_exit_program_truncate_txt():
    logger.info(f'inne i start_exit_program_truncate_txt funktion')
    try:
        with open(RSS_LOG_FILE_PATH, "w+") as f:
            f.write('FIRST_LINE\n')
            f.flush()
            f.seek(0)
            content = f.readlines()[-1]
        return content
    except:
        pass


def validate_config(config_file=CONFIG_FILE_PATH):
    config.read(config_file)
    logger.info("LÄSER FILEN I VALIDATE CONFIG FUNKTIONEN")
    sections = ['rss_adresser', 'sleep', 'marker',
                'login_mail', 'smtp_reciever', 'smtp_to_self']
    for section in sections:
        if not config.has_section(section):
            check_existance_and_create_default_or_reset(Reset=True)


### RESET THE CONFIG FILE and create default####
def check_existance_and_create_default_or_reset(Reset: bool = False):
    # Settings used in RSS-matix.
    config['rss_adresser'] = {}
    config['sleep'] = {'1': '300'}
    config['marker'] = {'1': 'false'}
    config['login_mail'] = {'usr': '', 'pwd': '',
                            'key': '', 'verified': 'false'}
    config['smtp_reciever'] = {}
    config['smtp_to_self'] = {'t/f': 'false'}
    config['smtp_host'] = {'host': ''}
    config['smtp_port'] = {'port': ''}
    config['log_mode'] = {'logger_activated': 'false'}

# Reset to default if True from GUI
    if Reset is True:
        with open(CONFIG_FILE_PATH, 'w+') as cfg:
            config.write(cfg)
        return
# If false, test and see if everything is OK, otherwise return to default settings.
    try:
        with open(CONFIG_FILE_PATH, 'r') as cfg:
            print("filen existerar redan, do nothing. ALLT OK!")
    except:
        logger.error('Exception fångad. Filen existerar ej eller error vid inläsning av fel. \
                      Automatisk återställning av config.ini')
        # Resets config to default
        with open(CONFIG_FILE_PATH, 'w+') as cfg:
            config.write(cfg)


if __name__ == "__main__":
    pass
