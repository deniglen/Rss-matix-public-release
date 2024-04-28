from __future__ import annotations
import feedparser
import ssl
import time
from .logging_setup import setup_logger
import multiprocessing

logger = setup_logger(__name__)
#### START RSS_READER!####


class rss_reader:

    class RssReaderLoop:
        def __init__(self, set_model: 'model'):
            self.errors_occured = 0
            self.run_loop = True
            self.model = set_model
            self.usr, _ = self.model.read_login_mail()
            self.sleep_timer = int(self.model.read_time())
            self.lista_adresser = list(self.model.current_rss_urls().values())
            self.entries = ["NULL"] * len(self.lista_adresser)
            self.new_entries = ["NULL"] * len(self.lista_adresser)
            self.marker_mail, self.corrected_mail_list = self.model.send_mail_to()
            # populates entries and new_entries with the same latest update.
            self._load_latest_entries_as_default()
            self._timer = 0.5

        def _re_read_all(self):
            self.usr, _ = self.model.read_login_mail()
            self.sleep_timer = int(self.model.read_time())
            self.lista_adresser = list(self.model.current_rss_urls().values())
            self.lista_adresser.clear()
            self.entries.clear()
            self.new_entries.clear()
            self.marker_mail, self.corrected_mail_list = self.model.send_mail_to()
            # This is the one which takes *alot* of time to go throu.
            self._load_latest_entries_as_default()

        def _format_feed(self, entry) -> tuple[str, str, str]:
            publicerad = entry.published
            titel = entry.title
            summering = entry.summary
            publicerad = publicerad.replace(
                "ä", "a").replace("å", "a").replace("ö", "o")
            titel = titel.replace("ä", "a").replace("å", "a").replace("ö", "o")
            summering = summering.replace("ä", "a").replace(
                "å", "a").replace("ö", "o")
            return publicerad, titel, summering

        def _parse(self, url, date=True):
            time.sleep(self._timer)
            if hasattr(ssl, '_create_unverified_context'):
                ssl._create_default_https_context = ssl._create_unverified_context
                feed = feedparser.parse(url)

                if not feed.entries:
                    return "no feed on address"

                if not date:
                    return self._format_feed(feed.entries[0])
                # there is a feed, and we are looking at date published
                return feed.entries[0].published

        def _load_latest_entries_as_default(self):
            for i, adress in enumerate(self.lista_adresser):
                load_into_list = self._parse(adress)
                self.entries[i] = load_into_list
                self.new_entries[i] = load_into_list
                print(self.entries[i], self.new_entries[i])

        # Provide default arguments here and push changes from view to controller instead in GUI?
        def _utskrift(self, feed):
            publicerad, titel, summering = self._parse(feed, False)
            self.model.write_entries_reader(
                f'{publicerad} : {titel} : {summering}')
            self.marker_mail, self.corrected_mail_list = self.model.send_mail_to()
            if not self.marker_mail:
                return
            self.model.send_mail_notification_rss_update(
                self.corrected_mail_list, 'Subject: {}..!\n\nVakna!\n\n{}..\n\n{}..\n\nRSS-MATIX ALFA 1.3' .format(titel, summering, publicerad).encode('utf-8'))

        # Legacy, do not touch :-D
        def check_updates_loop(self):
            try:
                while self.run_loop:
                    for i, addr_new_entry in enumerate(self.lista_adresser):
                        self.new_entries[i] = self._parse(addr_new_entry)
                        print('for loop new entries')
                        time.sleep(self._timer)

                    for w, each in enumerate(self.lista_adresser):
                        if self.new_entries[w] != self.entries[w]:
                            self.entries[w] = self.new_entries[w]
                            logger.info(self.lista_adresser[w])
                            self._utskrift(self.lista_adresser[w])

                    logger.info(
                        f'kollat alla entries, sover i {(self.sleep_timer-len(self.lista_adresser)*2)} sekunder och uppdaterar ev inställningar')
                    self.sleep_timer = int(self.model.read_time())
                    if self.sleep_timer-len(self.lista_adresser)*self._timer >= 0:
                        time.sleep(self.sleep_timer -
                                   len(self.lista_adresser)*self._timer)
                    logger.info("Begin parsing next round of RSS-feeds")
            except Exception as e:
                self.error_handling(e)

        def error_handling(self, e):
            self.errors_occured = self.errors_occured + 1
            self._re_read_all()
            self.model.send_mail_notification_rss_update(
                self.usr, f'Subject: Din RSS-reader har rest undantag, omstart om 20 sec! Genererat felmeddelande: {e}')
            time.sleep(20)

    def __init__(self, model_obj: 'model'):
        self.model = model_obj
        self.rss_fetcher_process = multiprocessing.Process(target=self._main)

    def start_reader(self):
        if not self.rss_fetcher_process.is_alive():
            self.rss_fetcher_process = multiprocessing.Process(
                target=self._main)
            self.rss_fetcher_process.start()
            time.sleep(0.1)
            print("Startar reader efter stopp.")
        else:
            print("Kan inte starta fler processer")

    def stop_reader(self):
        try:
            self.rss_fetcher_process.terminate()
            self.rss_fetcher_process.join()
            time.sleep(0.1)
            print(
                f'Lever processen fortfarande? {self.rss_fetcher_process.is_alive()}')
        except Exception:
            print("Reader kördes inte från början.")

    def check_if_alive_and_restart(self):
        if self.rss_fetcher_process.is_alive():
            self.stop_reader()
            self.start_reader()
        else:
            print("Reader död. Startar om...")
            self.start_reader()

    def _main(self):
        logger.info("Starting rss_lasare_V2")
        try:
            self.reader_loop_obj = self.RssReaderLoop(self.model)
            self.reader_loop_obj.check_updates_loop()
        except Exception as e:
            logger.error(e, exc_info=True)
            logger.info("Fel när RssReaderLoop initierades")
            quit()


if __name__ == "__main__":
    from controller import IModel
    from model import model
