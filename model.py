
import multiprocessing
from model_package.logging_setup import setup_logger
from model_package.config_funcs import ConfigFile
import model_package.rss_lasare_V2 as rss_lasare_V2
from model_package import mail_funcs as mail_model
from model_package import read_from_txt_model as txt_model
from model_package import time_model_funcs as time_model
from model_interface import IModel


class model(IModel):
    def __init__(self):
        self.logger = setup_logger(__name__)
        # Begin with validation of config file, if does not exist or faulty create default.
        txt_model.validate_config()

        # Lock for various IO operations
        self.lock = multiprocessing.Lock()

        # Create objects that handles logic and RSS-fetcher loop
        self.rss_and_email_adresses_model = ConfigFile()
        self.reader_rss = rss_lasare_V2.rss_reader(self)

        # set some initial state..
        self.current_entries, self.current_rows_entries = self.read_latest_entry_rss(
            txt_model.fetch_last_entry_line_num())


# Lock one process, runs the argument function, then releases the lock.
    def lock_decorator(func):
        def wrapper(self: 'model', *args, **kwargs):
            self.lock.acquire(timeout=10)
            result = func(self, *args, **kwargs)
            self.lock.release()
            return result
        return wrapper

    @lock_decorator
    def send_mail_notification_rss_update(self, recipient, msg):
        client = mail_model.SmtpClient()
        client.send_mail(recipient, msg)

    @lock_decorator
    def read_latest_entry_rss(self, read_from_line):
        return txt_model.read_entries_tkinter(read_from_line)

    @lock_decorator
    def check_exist_or_reset(self, Reset):
        txt_model.check_existance_and_create_default_or_reset(Reset)

    @lock_decorator
    def truncate_rss_history(self):
        return txt_model.start_exit_program_truncate_txt()

    @lock_decorator
    def read_all_entries(self):
        return txt_model.read_all_entries_tkinter()

    @lock_decorator
    def write_entries_reader(self, entries):
        txt_model.write_entries_reader(entries)

    @lock_decorator
    def validate_email(self, adress):
        return mail_model.validera_email(adress)

    def remove_address_reciever(self, which_to_pop):
        self.rss_and_email_adresses_model.remove_address(which_to_pop, False)

    def remove_address_rss_url(self, which_to_pop):
        self.rss_and_email_adresses_model.remove_address(which_to_pop, True)

    @lock_decorator
    def current_smtp_recievers(self):
        result = self.rss_and_email_adresses_model.smtp_recievers
        return result

    def current_rss_urls(self):
        return self.rss_and_email_adresses_model.rss_addresses

    def check_duplicate_adresses_recievers(self, adress):
        return self.rss_and_email_adresses_model.check_adress_duplicate_recievers(adress)

    def check_duplicate_adresses_rss_urls(self, adress):
        return self.rss_and_email_adresses_model.check_adress_duplicate_rss_urls(adress)

    def smtp_recievers_add(self, adress):
        add_id = self.rss_and_email_adresses_model.add_address(adress, False)
        return add_id

    def rss_url_add(self, address):
        add_id = self.rss_and_email_adresses_model.add_address(address, True)
        return add_id

    def mail_login_verify(self):
        return mail_model.mail_login_verify()

    # Counts amount of SMTP recipients
    def count_recievers(self):
        self.logger.info("RÄKNAR ANTALET ADRESSER!")
        return self.rss_and_email_adresses_model.smtp_recievers

    @lock_decorator
    def read_login_mail(self):
        return mail_model.read_login_mail()

    @lock_decorator
    def remove_mail(self):
        mail_model.remove_mail()

    @lock_decorator
    def set_marker_mail(self, marker):
        mail_model.set_marker_mail(
            marker, self.rss_and_email_adresses_model.mail_to_self)

    @lock_decorator
    def read_marker(self):
        return mail_model.read_marker()

    @lock_decorator
    def set_login_mail(self, new_usr, new_pwd, smtp_host, smtp_port) -> bool | str:
        return mail_model.set_login_mail(new_usr, new_pwd, smtp_host, smtp_port)

    @lock_decorator
    def parse_test_rss(self, address):
        return mail_model.parse(address)

    @lock_decorator
    def convert_time(self):
        return time_model.convert_time_value_menu()

    @lock_decorator
    def read_time(self):
        return time_model.read_time()

    def start_reader(self):
        self.reader_rss.start_reader()

    @lock_decorator
    def stop_reader(self):
        self.reader_rss.stop_reader()

    @lock_decorator
    def set_time(self, time):
        time_model.set_time(time)

    @lock_decorator
    def check_if_alive_and_restart(self):
        self.reader_rss.check_if_alive_and_restart()

    @lock_decorator
    def read_to_self(self):
        return self.rss_and_email_adresses_model.mail_to_self

    @lock_decorator
    def set_mail_to_self(self, T_OR_F: bool):
        self.rss_and_email_adresses_model.set_mail_to_self(T_OR_F)
    # Should return one simple thing.. TRUE OR FALSE

    def return_current_entries(self) -> list:
        return self.current_entries

    def return_current_rows_entries(self) -> int:
        return self.current_rows_entries

    def update_entry_data_attributes(self) -> None:
        # updates entries from last update.
        self.current_entries, self.current_rows_entries = self.read_latest_entry_rss(
            self.current_rows_entries)

    def send_mail_to(self):
        marker_mail_to_others = self.read_marker()
        usr, _ = self.read_login_mail()
        mail_to_self = self.read_to_self()

        if marker_mail_to_others is False:
            return False, "_"

        mail_list = self.current_smtp_recievers()
        mail_list = list(mail_list.values())
        corrected_mail_list = [x for x in mail_list if "@." and "." in x]

        if mail_to_self is True:
            corrected_mail_list.insert(0, usr)

        return True, corrected_mail_list


if __name__ == "__main__":
    pass
