
from configparser import ConfigParser
import os
import feedparser
import ssl
import smtplib
import re
from .logging_setup import setup_logger
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .path_module import CONFIG_FILE_PATH

logger = setup_logger(__name__)
config = ConfigParser()

#### MAILFUNCTIONS####


class SmtpClient:
    def __init__(self) -> None:
        self._update_self()

    def _update_self(self):
        self._user, self._password = read_login_mail()
        self._smtp_host, self._smtp_port = read_smtp_host_settings()
        self._server = None

    def _connect(self):
        self._server = smtplib.SMTP(self._smtp_host, self._smtp_port)
        self._server.ehlo()
        self._server.starttls()
        try:
            self._server.login(self._user, self._password)
            logger.info("SMTP anslutning lyckades.")
        except smtplib.SMTPAuthenticationError:
            logger.info("SMTP authentication misslyckades.")
        except smtplib.SMTPException as e:
            logger.info(
                "Ett fel uppstod medans anslutningen försökte upprättas:", exc_info=True)

    def _close(self):
        if self._server:
            self._server.quit()

    def send_mail(self, to, subject):
        self._connect()
        self._server.sendmail(self._user, to, subject)
        self._close()


def read_smtp_host_settings() -> tuple[str, int]:
    smtp_host = config.get('smtp_host', 'host')
    smtp_port = config.get('smtp_port', 'port')
    return smtp_host, int(smtp_port)


def read_login_mail():
    file = CONFIG_FILE_PATH
    config.read(file)
    usr = config.get('login_mail', 'usr')

    pwd_raw = config.get('login_mail', 'pwd')

    if pwd_raw == "" or usr == "":
        return "", ""

    # Decrypts the encrypted string to plain text before sending.
    try:
        pwd_decrypted = avkryptering_func(pwd_raw)

        return usr, pwd_decrypted
    except:
        logger.info("kunde ej avkryptera lösenord!")
        error_usr = "ERROR MAIL, LOGGA UT!"
        return error_usr, pwd_raw

# Validation for mail recepient.
def validera_email(email):
    pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    return pattern.match(email)


def mail_login_verify():
    file = CONFIG_FILE_PATH
    config.read(file)
    marker = config.getboolean('login_mail', 'verified')
    return marker


def remove_mail():
    file = CONFIG_FILE_PATH
    config.read(file)
    config.set('login_mail', 'usr', '')
    config.set('login_mail', 'pwd', '')
    config.set('login_mail', 'key', '')
    config.set('login_mail', 'verified', 'false')

    with open(file, "w+") as cfg:
        config.write(cfg)


def pwd_hash(func):
    def wrapper(usr, pwd, smtp_host, smtp_port):
        logger.info("inne i pwd_hash")
        if not isinstance(pwd, str):
            logger.info("PWD NOT STRING ERROR")
            return False
        salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(pwd.encode()))
        fernet = Fernet(key)

        encrypted_password = fernet.encrypt(pwd.encode())
        file = CONFIG_FILE_PATH
        # config = ConfigParser()
        config.read(file)

        # Decode byteobj to string so it's possible to save in config.ini
        key_string = key.decode()
        encrypted_password = encrypted_password.decode()

        return func(usr, encrypted_password, smtp_host, smtp_port, key_string)
    # If validation true, write to file with key, otherwise skip
    return wrapper


def avkryptering_func(encrypted_pwd, nyckel=None):
    logger.info('inne i avkryptering_func')
    file = CONFIG_FILE_PATH
    config.read(file)
    # Fetch encrypted key as string.
    # hämtar krypteringsnyckeln som sträng
    # If the function does not get a key should it be read! Thus key = none READ otherwise nyckel is the key which the function shall use.
    if nyckel is None:
        fernet_key_string = config.get('login_mail', 'key')
    else:
        fernet_key_string = nyckel
    fernet_key_bytes = fernet_key_string.encode()

    # Rework the encryption key to bytes-obj (fernet instantiation needs key in byte object)
    # Then create a fernet obj with the specific bytes-obj key.
    fernet = Fernet(fernet_key_bytes)
    # Finally, decrypt the encrypted pwd with the key assigned to the fernet object. Returns pwd in type bytes-object.
    pwd_bytes = fernet.decrypt(encrypted_pwd)
    logger.info("lösenord har genomgått godkänd avkryptering")
    # Returns decoded pwd, for easy of use decode it into string! :-)
    return pwd_bytes.decode()


@pwd_hash
def set_login_mail(usr, pwd_encrypted, smtp_host, smtp_port, nyckel=None) -> bool | str:
    try:
        # Try to decrypt first, if it does not work, something went wrong.
        pwd = avkryptering_func(pwd_encrypted, nyckel)
        # Then try to write values to config file.
        file = CONFIG_FILE_PATH
     #   config = ConfigParser()
        config.read(file)
        config.set('smtp_port', 'port', str(smtp_port))
        config.set('smtp_host', 'host', smtp_host)
        config.set('login_mail', 'usr', usr)
        config.set('login_mail', 'pwd', pwd_encrypted)
        config.set('login_mail', 'key', nyckel)
        config.set('login_mail', 'verified', "true")

        # If it succeeds, then send an email that the user logged in successfully!
        success_mail, errmsg = send_verification_email(
            usr, pwd, smtp_host, smtp_port)

        # return the boolean and error if failed sending verification mail
        if not success_mail:
            return success_mail, errmsg

        # If the mail went okay, then write the setting to the config...finally... //20221230
        with open(file, "w+") as cfg:
            config.write(cfg)
        return success_mail, None
    except Exception as e:
        logger.error(
            "Kunde inte skriva inställningar, se logg:", exc_info=True)
        return False, e


def send_verification_email(usr, pwd, smtp_host, smtp_port) -> bool | str:
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as conn:
            conn.ehlo()
            conn.starttls()
            conn.login(usr, pwd)
            conn.sendmail(
                usr, usr, 'Subject: Du har loggat in i RSS-MATIX! Grattis :-)')
        return True, None
    except Exception as e:
        logger.error(
            "Kunde inte skicka iväg verifieringsmeddelande, se logg:", exc_info=True)
        return False, e


# TODO: test send mail func
# Maybe a button for "Test mail"?
# Where every recipent recieves a mail notification to verify everythin works correctly.
def send_testmail():
    pass


# Checks if there is any recepients, marker --> F if no recepients.
def check_mail_list_marker(func):
    def wrapper(marker, mail_to_self):
        logger.info("inne i check_mail_list_marker")
        config.read(CONFIG_FILE_PATH)
        mail_list_len_check = config.items('smtp_reciever')
        logger.info(
            f"mail_list_len_check: {bool(mail_list_len_check)}, mail_to_self: {mail_to_self}")

        if not mail_list_len_check and not mail_to_self:
            func('false', mail_to_self)
        else:
            func(marker, mail_to_self)
    return wrapper


# Puts marker, T/F for save of "skicka RSS till mail"
@check_mail_list_marker
def set_marker_mail(marker: str, mail_to_self: bool):
    marker = str(marker)
    file = CONFIG_FILE_PATH
   # config = ConfigParser()
    config.read(file)
    config.items
    config.set('marker', '1', marker)

    with open(file, "w+") as cfgfile:
        config.write(cfgfile)


def read_marker():
    file = CONFIG_FILE_PATH
   # config = ConfigParser()
    config.read(file)
    marker = config.getboolean('marker', '1')
    return marker

# used for validating rss so the link is not dead.
def parse_test(f):
    def wrapper(url):
        try:
            feeds = f(url)
            if feeds.bozo == True:
                raise Exception("TRASIG LÄNK! FÖRSÖK IGEN!")
            BozoError = False
            return BozoError
        except:
            BozoError = True
            return BozoError
    return wrapper


@parse_test
def parse(url):
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context
    feed = feedparser.parse(url)
    return feed


if __name__ == "__main__":
    pass
