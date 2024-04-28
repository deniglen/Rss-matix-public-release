from configparser import ConfigParser
from .logging_setup import setup_logger
from .path_module import CONFIG_FILE_PATH


logger = setup_logger(__name__)


# Class for handling addresses in config.ini for email recipients and RSS URLs
class ConfigFile:
    def __init__(self):
        # Load the config.ini file and create the rss_addresses and smtp_recievers dictionaries
        self.config = ConfigParser()
        self.config.read(CONFIG_FILE_PATH)
        self.mail_to_self = self.config.getboolean('smtp_to_self', 't/f')
        self.rss_addresses = {
            int(k): v for k, v in self.config.items('rss_adresser')}
        self.smtp_recievers = {
            int(k): v for k, v in self.config.items('smtp_reciever')}

    def set_mail_to_self(self, T_or_F: bool):
        self.mail_to_self = T_or_F
        converted_T_or_F = str(T_or_F)
        self.config.read(CONFIG_FILE_PATH)
        self.config.set('smtp_to_self', 't/f', converted_T_or_F)

        with open(CONFIG_FILE_PATH, 'w+') as cfgfile:
            self.config.write(cfgfile)

    def check_adress_duplicate_recievers(self, address):
        if address in self.smtp_recievers.values():
            logger.info(f"Adress som redan existerade: {address}")
            return True
        return False

    def check_adress_duplicate_rss_urls(self, address):
        if address in self.rss_addresses.values():
            logger.info(f"Adress som redan existerade: {address}")
            return True
        return False

    # TODO: See comments down below, also boilerplate and doing too much stuff...
    def add_address(self, address, rss=True):
        # Add the address to the appropriate dictionary and update the config.ini file
        if rss:
            self.rss_addresses[len(self.rss_addresses) + 1] = address
            self.config['rss_adresser'] = self.rss_addresses

            # maybe just refactor if len(self.rss_addresses) + 1 works fine and return that as int_id
            id_list = list(self.rss_addresses.keys())
            int_list = [int(x) for x in id_list]
            id_max = max(int_list, default=0)
            id_int = int(id_max)
        else:
            self.smtp_recievers[len(self.smtp_recievers) + 1] = address
            self.config['smtp_reciever'] = self.smtp_recievers

            # Maybe just refactor if len(self.rss_addresses) + 1 works fine and return that as int_id
            id_list = list(self.smtp_recievers.keys())
            int_list = [int(x) for x in id_list]

            id_max = max(int_list, default=0)
            id_int = int(id_max)

            print("inne i smtp_reciever add")
        with open(CONFIG_FILE_PATH, 'w+') as cfgfile:
            self.config.write(cfgfile)
        return id_int

    def remove_address(self, pop, rss=True):

        # Remove the address from the appropriate dictionary and update the config.ini file
        pop = int(pop)

        if rss:
            self.rss_addresses.pop(pop, None)
        else:
            self.smtp_recievers.pop(pop, None)

        # Re-index the keys in the dictionaries so that they are in sequential order starting from 1
        if rss:
            dict_adresser = self.rss_addresses
        else:
            dict_adresser = self.smtp_recievers

        keys_to_update = list(dict_adresser.keys())
        ReEvalDict = dict_adresser
        for idx, key in enumerate(keys_to_update, start=1):
            ReEvalDict[idx] = ReEvalDict.pop(key)

        self.config.read(CONFIG_FILE_PATH)
        if rss:
            self.config['rss_adresser'] = ReEvalDict
        else:
            self.config['smtp_reciever'] = ReEvalDict

        with open(CONFIG_FILE_PATH, 'w+') as cfgfile:
            self.config.write(cfgfile)


if __name__ == "__main__":
    pass
