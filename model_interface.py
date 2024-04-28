from abc import ABC, abstractmethod


class IModel(ABC):
    @abstractmethod
    def validate_email(self, adress: str) -> str:
        pass

    @abstractmethod
    def return_current_entries(self) -> list:
        pass

    @abstractmethod
    def return_current_rows_entries(self) -> int:
        pass

    @abstractmethod
    def update_entry_data_attributes(self) -> None:
        pass

    @abstractmethod
    def remove_address_reciever(self, which_to_pop: int) -> None:
        pass

    @abstractmethod
    def remove_address_rss_url(self, which_to_pop: int) -> None:
        pass

    @abstractmethod
    def current_smtp_recievers(self):
        pass

    @abstractmethod
    def current_rss_urls(self):
        pass

    @abstractmethod
    def check_duplicate_adresses_recievers(self, adress: str) -> str:
        pass

    @abstractmethod
    def check_duplicate_adresses_rss_urls(self, adress: str) -> str:
        pass

    @abstractmethod
    def smtp_recievers_add(self, adress: str) -> int:
        pass

    @abstractmethod
    def rss_url_add(self, address: str) -> int:
        pass

    @abstractmethod
    def read_latest_entry_rss(self):
        pass

    @abstractmethod
    def check_exist_or_reset(self, Reset: bool) -> None:
        pass

    @abstractmethod
    def truncate_rss_history(self) -> None:
        pass

    @abstractmethod
    def read_all_entries(self):
        pass

    @abstractmethod
    def convert_time(self) -> str:
        pass

    @abstractmethod
    def mail_login_verify(self) -> str:
        pass

    @abstractmethod
    def count_recievers(self) -> int:
        pass

    @abstractmethod
    def read_login_mail(self):
        pass

    @abstractmethod
    def remove_mail(self) -> None:
        pass

    @abstractmethod
    def set_marker_mail(self, marker: str) -> None:
        pass

    @abstractmethod
    def read_marker(self) -> str:
        pass

    @abstractmethod
    def set_login_mail(self, new_usr: str, new_pwd: str) -> bool | str:
        pass

    @abstractmethod
    def parse_test_rss(self, address: str) -> str:
        pass

    @abstractmethod
    def start_reader(self):
        pass

    @abstractmethod
    def stop_reader(self):
        pass

    @abstractmethod
    def check_if_alive_and_restart(self):
        pass

    @abstractmethod
    def read_time(self):
        pass

    @abstractmethod
    def write_entries_reader(self):
        pass

    @abstractmethod
    def send_mail_to(self):
        pass

    @abstractmethod
    def read_to_self(self):
        pass

    @abstractmethod
    def set_mail_to_self(self):
        pass

    @abstractmethod
    def set_time(self):
        pass
