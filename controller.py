from typing import Type
from model_interface import IModel
### Controller for RSS-MATIX!###


class Controller():
    def __init__(self, windows: Type['windows'], model: IModel):
        self.model = model
        # Initiate windows last, can't be initated earlier since it uses model logic present in the controller.
        self.view = windows(self)

    def start_mainloop(self):
        self.view.mainloop()

# Appends smtp reciever email to dict if passes test, prints out in view
    def add_address(self, address: str) -> None:
        if address is None:
            return "No address provided"

        if self.model.check_duplicate_adresses_recievers(address):
            return "Duplicate address"
        elif self.model.validate_email(address):
            new_address_id = self.model.smtp_recievers_add(address)
            self.model.check_if_alive_and_restart()
            return f"Mottagaradress: {new_address_id}: {address}\n"
        else:
            return "Invalid address"

    def pop_feed_url(self, pop_index):
        if bool(pop_index) is False or pop_index == "":
            return

        self.model.remove_address_rss_url(pop_index)
        self.model.check_if_alive_and_restart()
        current_addresses_rss = self.model.current_rss_urls()

        if bool(current_addresses_rss) is False:
            self.model.set_marker_mail('false')
            return current_addresses_rss, False
        else:
            return current_addresses_rss, True

    def pop_smtp_reciever(self, pop_index):
        if bool(pop_index) is False or pop_index == "":
            return

        # TODO: Refactor? Uses same function for pop_feed_url.
        # Except if second argument is False, then pop SMTP reciever instead.
        self.model.remove_address_reciever(pop_index)
        current_smtp_recievers = self.model.current_smtp_recievers()
        if bool(current_smtp_recievers) is False:
            self.model.set_marker_mail('false')
            return current_smtp_recievers, False
        else:
            return current_smtp_recievers, True

    def set_mail_to_self(self, set_bool):
        self.model.set_mail_to_self(set_bool)
        # if mail to smtp sender is false and no smtp recievers in list, deactivate in view.
        if not set_bool and not self.model.current_smtp_recievers():
            self.view.StartPage.set_radio_button_off()
            self.model.set_marker_mail("false")
        # do nothing more, then its recepients in the list and RSS to mail can still be active

    def update_logged_in_mail(self):
        if self.model.mail_login_verify():
            self.view.SmtpPage.activate_logged_in()

    def toggle_email_notifcations(self, toggle: str) -> None:
        verify_mail = self.model.mail_login_verify()
        send_to_self = self.model.read_to_self()
        has_recievers = self.model.current_smtp_recievers()
        has_rss_urls = self.model.current_rss_urls()
        # only need checks if going from false -> true.
        if ((verify_mail == False or
            (bool(has_recievers) == False and send_to_self == False) or
                (bool(has_rss_urls)) == False) and toggle == "true"):

            self.view.StartPage.set_radio_button_off()
            self.view.show_warning_popup(title="Error mail-funktion",
                                         message="Kan ej aktivera RSS-till mail. "
                                         ":-( \n \n Vänligen gå till SMTP/E-mail inställningar i menyn och logga"
                                         "in eller lägg till mottagare först!\n alternativt,"
                                         " kryssa i radioknapp för att inkludera mailnotiser till inloggad mail.")
        # should not be able to set marker to true if login is not verified!
        else:
            self.model.set_marker_mail(toggle)

    # Reads current addresses from model and returns time as string
    def update_time(self, new_time):
        self.model.set_time(new_time)
        self.model.check_if_alive_and_restart()
        return self.model.convert_time()

    # reset settings in config file
    def reset_settings(self):
        self.model.stop_reader()
        self.model.check_exist_or_reset(Reset=True)

    def check_latest_entry(self, read_from_line=0) -> tuple[str, int]:
        entries, latest_entry_line_number = self.model.read_latest_entry_rss(
            read_from_line)
        return entries, latest_entry_line_number

    def update_rss_updates(self) -> None:
        # update with only the latest, not from previous session
        current_entries = self.model.return_current_entries()
        for entry in current_entries:
            if entry != "FIRST_LINE\n":
                self.view.StartPage.insert_output_in_textbox(entry)
        self.model.update_entry_data_attributes()

    def remove_sender(self):
        usr, pwd = self.model.read_login_mail()
        if usr != "" or pwd != "":
            ta_bort_inlog = self.view.ask_question(
                title="Inloggning", message="Säker på att du vill ta bort inloggning?")
            if ta_bort_inlog == 'yes':
                self.model.stop_reader()
                self.model.remove_mail()
                self.view.SmtpPage.set_no_login_gui()

    def delete_history(self):
        PromtRadera = self.view.ask_yes_no(
            'RaderaPromt', 'RADERA ALL HISTORIK I FILEN?')
        if PromtRadera:
            self.model.truncate_rss_history()
            self.view.StartPage.output_delete_box()

    def show_history(self):
        entries_history = self.model.read_all_entries()
        if not bool(entries_history):
            self.view.show_warning_popup(
                "Ingen historik", "Finns ingen tillgänglig historik att visa.")
            return
        # If history available, show in view output.
        entries_history = '\n'.join(entries_history)
        self.view.StartPage.show_history(entries_history)

    def add_user(self):
        smtp_host = self.view.ask_user_input_string(
            "Skriv in SMTP-host", "Hostadress")
        smtp_port = self.view.ask_user_input_integer(
            "Skriv in SMTP-port", "Port")
        user = self.view.ask_user_input_string(
            "Lägg till / ändra adress", "Adress")

        if not user or not smtp_host or not smtp_port:
            self.view.show_info_popup(title="ERROR", message="Ogiltigt format")
            return
        password = self.view.ask_user_input_string(
            "Lägg till / ändra lösenord", "Lösenord", show="*")
        if not password:
            return
        password_check = self.view.ask_user_input_string(
            "Skriv in lösenordet igen", "Lösenord", show="*")
        if not password_check:
            return
        if password != password_check:
            self.view.showwarning(
                title="Error lösenord", message="Du skrev ej in samma lösenord två gånger. :-( \n Vänligen försök igen!")
            return

        # Catch any errors returned and show to user
        successbool, errmsg = self.model.set_login_mail(
            user, password, smtp_host, smtp_port)
        if not successbool:
            self.view.show_info_popup(title="ERROR", message=errmsg)
            return

        self.view.show_info_popup(
            title="Status", message=f"Succé! Ett verifieringsmail om lyckad inloggning ska ha blivit ivägskickat till {user}")
        self.view.SmtpPage.activate_logged_in()

    def address_add_rss(self) -> None:
        # Get user input
        new_address = self.view.ask_user_input_string("Add RSS URL", "RSS URL")
        if not new_address:
            # Return without doing anything (could be cancel or just obvious empty string input)
            return

        # Check if address already exists in list
        if self.model.check_duplicate_adresses_rss_urls(new_address):
            # error_callback("Error", "Adressen finns redan i listan")
            self.view.show_warning_popup(
                "Error", "Adressen finns redan i listan")
            return

        # Verify valid RSS url by pinging it
        if self.model.parse_test_rss(new_address):
            self.view.show_warning_popup(
                "Adress ogiltig", "Du skrev in en ogiltig adress. :-( \n Vänligen försök igen!")
            return

        # If all good then add to list and restart process
        id_to_add_in_gui = self.model.rss_url_add(new_address)
        self.view.RssUrlPage.on_add_success(id_to_add_in_gui)
        self.model.check_if_alive_and_restart()


if __name__ == "__main__":
    from tkinter_view import windows
    from model_interface import IModel
