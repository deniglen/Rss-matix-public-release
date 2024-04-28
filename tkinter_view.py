from __future__ import annotations
import time
import sys
# from configparser import ConfigParser
import os
from PIL import ImageTk, Image
from tkinter import messagebox
from tkinter import simpledialog
import customtkinter as Ctk

from model_package.logging_setup import setup_logger
from typing import Type

logger = setup_logger(__name__)


class windows():
    def __init__(self, controller: Controller):
        current_dir = os.path.dirname(__file__)
        logger.info(f"{current_dir}")
        print('Get current working directory : ', os.getcwd())
        logger.info("Starting GUI")

        self.controllerfuncs = controller

        # Creates a tkinter root window. Frames need a root window object to be passed as argument.
        self.APP_MAIN = App(self.controllerfuncs)

        self.frames = {}
        self.frame_method = {}
        self.frames_str_dict = {}
        self.SmtpPage: SmtpPage
        self.RssUrlPage: RssUrlPage
        self.UpdateTimePage: UpdateTimePage
        self.StartPage: StartPage
        # bind the methods in the controller and simultaneously pass the controller methods to buttons and bind them to "callback".
        # Adds frames to a dict
        for F in (RssUrlPage, UpdateTimePage, SmtpPage, StartPage):
            frame = F(self.APP_MAIN, self)
            # The windows class acts as the root window for the frames.
            self.frames[F] = frame
            # assign to the attributes, makes it accessible from controller.
            self.frames_str_dict[F.__name__] = frame
            setattr(self, F.__name__, frame)
            frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Using a method to switch frames
        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        # Raises the current frame to the top
        frame.tkraise()

    def get_page(self, page_name: Type[Ctk.CTkFrame]) -> Ctk.CTkFrame:
        return self.frames[page_name]

    def mainloop(self):
        try:
            self.APP_MAIN.mainloop()
        except Exception as e:
            logger.error(e, exc_info=True)

    def start_reader(self):
        self.APP_MAIN.start_reader(self.controllerfuncs)

    def ask_user_input_string(self, title: str, prompt: str, **kwargs) -> simpledialog.askstring:
        return simpledialog.askstring(title, prompt, **kwargs)

    def ask_user_input_integer(self, title: str = None, prompt: str = None, **kwargs) -> simpledialog.askstring:
        return simpledialog.askinteger(title, prompt, **kwargs)

    def show_info_popup(self, title, message) -> None:
        messagebox.showinfo(title, message)

    def show_warning_popup(self, title: str, message: str) -> None:
        messagebox.showwarning(title, message)

    def ask_question(self, title: str, message: str) -> None:
        return messagebox.askquestion(title, message)

    def ask_yes_no(self, title: str, message: str) -> None:
        return messagebox.askyesno(title, message)


class SmtpPage(Ctk.CTkFrame):
    def __init__(self, parent, controller: windows):
        super().__init__(parent)
        self.controller = controller

        switch_window_button = Ctk.CTkButton(
            self,
            text="Gå till huvudmeny",
            command=lambda: controller.show_frame(StartPage),
        )
        switch_window_button.grid(row=5, column=0, sticky=Ctk.W)

        # Create labels and buttons for the page, hide them and show them when needed
        self.remove_sender_label = Ctk.CTkButton(self, text="Ta bort inloggad mailadress",
                                                 command=lambda: self.controller.controllerfuncs.remove_sender())
        self.remove_sender_label.grid(row=6, column=0, sticky=Ctk.W, pady=5)

        self.active_login_smtp = Ctk.CTkLabel(
            self, text="Ingen mail är inloggad")
        self.active_login_smtp.grid(row=4, column=0, sticky=Ctk.W, pady=2)

        self.var_radio_smtp_to_self = Ctk.IntVar()
        self.activate_mail = Ctk.CTkRadioButton(self, text="Include mail notifications to self", variable=self.var_radio_smtp_to_self,
                                                value=1, command=lambda: self.controller.controllerfuncs.set_mail_to_self(True))
        self.activate_mail.grid(row=14, column=0, sticky=Ctk.E, pady=2, padx=5)

        self.deactivate_mail = Ctk.CTkRadioButton(
            self,
            text="Exclude mail notifications to self",
            variable=self.var_radio_smtp_to_self, value=0,
            command=lambda: self.controller.controllerfuncs.set_mail_to_self(
                False)
        )
        self.deactivate_mail.grid(
            row=15, column=0, sticky=Ctk.E, pady=2, padx=5)

        self.adress_label = Ctk.CTkButton(
            self, text="Lägg till / ändra inloggad E-mail", command=lambda: self.controller.controllerfuncs.add_user())
        self.adress_label.grid(row=1, column=0, sticky=Ctk.W, pady=1)

        self.info_textbox = Ctk.CTkTextbox(
            self, wrap=Ctk.WORD, width=500, height=370)
        self.info_textbox.grid(row=3, column=0, sticky=Ctk.W)

        label = Ctk.CTkLabel(self, text="SMTP/E-mail inställningar")
        label.grid(row=0, column=0, sticky=Ctk.W)

        if bool(self.controller.controllerfuncs.model.mail_login_verify()) is False:
            self.deactivate_logged_in()
        else:
            self.activate_logged_in()

    def deactivate_logged_in(self):
        print("No mail is logged in")
        self.remove_sender_label.configure(state="disabled")
        self.activate_mail.grid_forget()
        self.deactivate_mail.grid_forget()

    def activate_logged_in(self):
        self.adress_label.grid_forget()
        usr, pwd = self.controller.controllerfuncs.model.read_login_mail()
        self.active_login_smtp.configure(self, text=f"Inloggad som: {usr}")
        self.remove_sender_label.configure(state="enabled")

        if self.controller.controllerfuncs.model.read_to_self() is True:
            self.var_radio_smtp_to_self.set(1)
        else:
            self.var_radio_smtp_to_self.set(0)

        self.activate_mail.grid(row=14, column=0, sticky=Ctk.E, pady=2, padx=5)
        self.deactivate_mail.grid(
            row=15, column=0, sticky=Ctk.E, pady=2, padx=5)

        self.mottagare_add_label = Ctk.CTkButton(
            self, text="Lägg till mottagare", command=lambda: self.add_mottagare())
        self.mottagare_add_label.grid(row=2, column=0, sticky=Ctk.W, pady=3)

        self.mottagare_remove_label = Ctk.CTkButton(
            self, text="Ta bort mottagare", command=lambda: self.adress_recipient_remove())
        self.mottagare_remove_label.grid(row=2, column=0, pady=3)

        self.count_recievers()


# Counts the amount of recieving recipients.

    def count_recievers(self):
        self.info_textbox.delete('1.0', Ctk.END)
        nuvarande_adresser = self.controller.controllerfuncs.model.count_recievers()

        for idx, each in nuvarande_adresser.items():
            self.info_textbox.insert(
                Ctk.INSERT, f'Mottagaradress: {idx}: {each}\n')

    def set_no_login_gui(self):
        self.active_login_smtp.configure(text="Ingen mail är inloggad")
        self.controller.get_page(StartPage).var_radio.set(0)
        time.sleep(0.1)
        self.adress_label = Ctk.CTkButton(
            self, text="Lägg till / ändra inloggad E-mail", command=lambda: self.controller.controllerfuncs.add_user())
        self.adress_label.grid(row=1, column=0, sticky=Ctk.W, pady=2)
        self.mottagare_add_label.grid_forget()
        self.mottagare_remove_label.grid_forget()

        self.remove_sender_label.configure(state="disabled")

        # Testing if grid_forget works to hide buttons on specific cases
        # Example if no login active --> dont show "send notifications to self" radiobuttons
        self.activate_mail.grid_forget()
        self.deactivate_mail.grid_forget()

    def add_mottagare(self):
        ny_adress = simpledialog.askstring("Lägg till adress", "E-post adress")
        time.sleep(0.12)
        if ny_adress is None:
            return

        result = self.controller.controllerfuncs.add_address(ny_adress)
        if result == "Duplicate address":
            messagebox.showwarning(
                title="Adress info", message="Adressen som skrevs in är redan tillagd!")
        elif result == "Invalid address":
            messagebox.showwarning(
                title="Adress info", message="Du Skrev in en ogiltig adress. :-( \ Vänligen försök igen!")

        # Fallback case.
        elif result == "No address provided":
            messagebox.showwarning(
                title="No adress", message="Cancel was pressed, no address added")

        else:
            self.info_textbox.insert(Ctk.INSERT, result)

    def adress_recipient_remove(self):
        poppa_denna = simpledialog.askstring(
            "Poppa mottagare ", "Skriv in index för mottagaren du vill ta bort:")
        if poppa_denna is None or poppa_denna == "":
            return

        current_addresses_reciever, force_radio_button_to = self.controller.controllerfuncs.pop_smtp_reciever(
            poppa_denna)

        self.info_textbox.delete('1.0', Ctk.END)
        for idn, (idx, each) in enumerate(current_addresses_reciever.items(), start=1):
            self.info_textbox.insert(
                Ctk.INSERT, f'Mottagaradress: {idn}: {each}\n')

        # Ff force_radio_button_to "false" there is no addresses in list then
        if not force_radio_button_to:
            self.controller.get_page(StartPage).var_radio.set(0)


class RssUrlPage(Ctk.CTkFrame):
    def __init__(self, parent, controller: windows):
        super().__init__(parent)
        self.controller = controller

        # , font=('none 14 bold'),bg ="white",fg="black")
        label = Ctk.CTkLabel(
            self, text="Alla aktiva RSS-URL:er visas i textrutan ovan")
        label.grid(row=4, column=0, sticky=Ctk.W)

        switch_window_button = Ctk.CTkButton(
            self,
            text="Gå till huvudmeny",
            command=lambda: controller.show_frame(StartPage),
        )
        switch_window_button.grid(row=5, column=0, sticky=Ctk.W)

        self.adress_label = Ctk.CTkButton(
            self, text="Lägg till adress", command=lambda: self.controller.controllerfuncs.address_add_rss())
        self.adress_label.grid(row=1, column=0, sticky=Ctk.W, padx=2, pady=15)
        self.adress_label_remove = Ctk.CTkButton(
            self, text="Ta bort adress", command=lambda: self.adress_RSS_remove())
        self.adress_label_remove.grid(row=1, column=0,  padx=2)

        self.adress_label_info = Ctk.CTkButton(
            self, text="Tryck för info hur du tar bort adress", command=self.adress_info_func)
        self.adress_label_info.grid(row=0, column=0, sticky=Ctk.W, padx=1)

        self.output = Ctk.CTkTextbox(
            self, wrap=Ctk.WORD, width=500, height=370)
        self.output.grid(row=3, column=0, sticky=Ctk.W)

        nuvarande_adresser = self.controller.controllerfuncs.model.current_rss_urls()
        for idx, each in nuvarande_adresser.items():
            self.output.insert(Ctk.INSERT, f'Adress {idx}: {each}\n')

    def adress_info_func(self):
        self.output.delete('1.0', Ctk.END)
        self.output.insert(
            Ctk.INSERT, 'För att ta bort adress skriv in indexnumret i fritextrutan'
            'vid tryck på "ta bort adress".\nTex 3 tar bort Adress 3: X')
        self.adress_label_info.configure(
            text="Gå tillbaka", command=self.reload_page)

    def reload_page(self):
        self.output.delete('1.0', Ctk.END)
        nuvarande_adresser = self.controller.controllerfuncs.model.current_rss_urls()

        for idx, each in nuvarande_adresser.items():
            self.output.insert(Ctk.INSERT, f'Adress {idx}: {each}\n')

        self.adress_label_info.configure(
            text="Tryck för info hur du tar bort adress", command=self.adress_info_func)

    def adress_RSS_remove(self):
        poppa_denna = simpledialog.askstring(
            "Poppa RSS-adress ", "Skriv in index för RSS-adressen du vill ta bort:")
        if poppa_denna is None or poppa_denna == "":
            return

        self.output.delete('1.0', Ctk.END)

        current_addresses_rss, force_radio_button_to = self.controller.controllerfuncs.pop_feed_url(
            poppa_denna)

        for id, (idx, each) in enumerate(current_addresses_rss.items(), start=1):
            self.output.insert(Ctk.INSERT, f'Adress {id}: {each}\n')

        # If force_radio_button_to "false" there is no addresses in list then
        # Radio button should automatically go to "inactivate smtp functions"
        if force_radio_button_to is False:
            self.controller.get_page(StartPage).var_radio.set(0)

    def on_add_success(self, id_to_add: int) -> None:
        self.output.insert(Ctk.INSERT, f'Adress {id_to_add}: tillagd\n')


class UpdateTimePage(Ctk.CTkFrame):
    def __init__(self, parent, controller: windows):
        super().__init__(parent)
        self.controller = controller

        label = Ctk.CTkLabel(self, text="UPDATE TIME PAGE!!!")
        label.grid(row=1, column=0)

        # crate path to image
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, 'model_package', "time.png")

        self.img = Ctk.CTkImage(
            light_image=Image.open(image_path), size=(200, 200))
        self.label_img = Ctk.CTkLabel(self, text='', image=self.img)
        self.label_img.grid(row=2, column=0)

        switch_window_button = Ctk.CTkButton(
            self,
            text="Gå till huvudsida",
            command=lambda: controller.show_frame(StartPage),
        )
        switch_window_button.grid(row=5, column=0, pady=10)

        menub = Ctk.CTkOptionMenu(self, values=[
                                  "Meny", "1 minut", "5 minuter", "15 minuter", "30 minuter"], command=self.optionmenu_time)
        menub.grid(row=2, column=1, sticky=Ctk.E, padx=5)
        TimeValueStart = self.controller.controllerfuncs.model.convert_time()

        if TimeValueStart == "1":
            menub.set(f"{TimeValueStart} minut")
        else:
            menub.set(f"{TimeValueStart} minuter")

        self.ok_label_t = Ctk.CTkButton(
            self, text=f'Välj drop-down för refreshinst')
        self.ok_label_t.grid(row=4, column=0, sticky=Ctk.W, pady=10)

    def optionmenu_time(self, choice):
        if choice == "Meny":
            self.controller.show_frame(StartPage)

        elif choice == "1 minut":
            self.update_time(1*60)

        elif choice == "5 minuter":
            self.update_time(5*60)

        elif choice == "15 minuter":
            self.update_time(15*60)

        elif choice == "30 minuter":
            self.update_time(30*60)

    # Update time in config file and the label
    def update_time(self, text_input):
        time_string_minutes = self.controller.controllerfuncs.update_time(
            text_input)
        self.ok_label_t.configure(
            text=f'Inställd på: {time_string_minutes}-minutersintervall')


class StartPage(Ctk.CTkFrame):
    def __init__(self, parent, controller: windows):
        super().__init__(parent)
        self.controller = controller

        self.infolabel = Ctk.CTkLabel(
            self, text="Händelselogg RSS-uppdateringar!")
        self.infolabel.grid(row=4, column=0, sticky=Ctk.W)
        self.output = Ctk.CTkTextbox(
            self, wrap=Ctk.WORD, width=600, height=400, padx=10, pady=10)
        self.output.grid(row=5, column=0, sticky=Ctk.W)

        ok_label = Ctk.CTkButton(
            self, text="Rensa händelselogg", command=lambda: self.output.delete('1.0', Ctk.END))
        ok_label.grid(row=6, column=0, sticky=Ctk.W, pady=20)

        self.menub = Ctk.CTkOptionMenu(self, values=["Ställ in hur ofta kolla RSS-feed", "Ställ in RSS-URL:er", "SMTP/E-mail inställningar",
                                       "Visa RSS historik", "Radera RSS historik", "Återställ alla inställningar"], command=self.optionmenu_command)
        self.menub.grid(row=12, column=0, sticky=Ctk.E, pady=2, padx=5)
        self.menub.set("Meny")

        self.var_radio = Ctk.IntVar()

        current_marker = self.controller.controllerfuncs.model.read_marker()
        self.verify_mail = self.controller.controllerfuncs.model.mail_login_verify()

        if current_marker and self.verify_mail:
            self.set_radio_button_on()
        else:
            self.set_radio_button_off()

        self.activate_mail = Ctk.CTkRadioButton(
            self, text="Aktivera RSS till mail", variable=self.var_radio, value=1, command=lambda: self.controller.controllerfuncs.toggle_email_notifcations("true"))
        self.activate_mail.grid(row=14, column=0, sticky=Ctk.E, pady=2, padx=5)

        self.deactivate_mail = Ctk.CTkRadioButton(
            self, text="Inaktivera RSS till mail", variable=self.var_radio, value=0, command=lambda: self.controller.controllerfuncs.toggle_email_notifcations("false"))
        self.deactivate_mail.grid(
            row=15, column=0, sticky=Ctk.E, pady=2, padx=5)

        # begin checking for updates, calls on controller.
        self.update_entry_text_output()

    def set_radio_button_on(self):
        self.var_radio.set(1)

    def set_radio_button_off(self):
        self.var_radio.set(0)

    def optionmenu_command(self, choice):
        if choice == "Ställ in hur ofta kolla RSS-feed":
            print("inne i ställ in hur ofta rss")
            self.controller.show_frame(UpdateTimePage)

        elif choice == "Ställ in RSS-URL:er":
            self.controller.show_frame(RssUrlPage)

        elif choice == "SMTP/E-mail inställningar":
            self.controller.show_frame(SmtpPage)

        elif choice == "Visa RSS historik":
            self.controller.controllerfuncs.show_history()

        elif choice == "Radera RSS historik":
            self.controller.controllerfuncs.delete_history()

        elif choice == "Återställ alla inställningar":
            PromtRadera = messagebox.askyesno(
                'Radera inställningar', 'Säker på att du vill återställa inställningar?')
            if PromtRadera:
                print("SVARADE JA")
                self.controller.controllerfuncs.reset_settings()
                time.sleep(0.1)
                self.controller.get_page(SmtpPage).active_login_smtp.configure(
                    text=f"Ingen mail är inloggad")
                self.controller.get_page(SmtpPage).count_recievers()

        self.menub.set("Meny")

    def update_entry_text_output(self):
        # Updates the latest new RSS-entries and returns row number
        self.controller.controllerfuncs.update_rss_updates()
        self.after(5000, lambda: self.update_entry_text_output())

    def insert_output_in_textbox(self, insert: str) -> None:
        self.output.insert(Ctk.INSERT, (f'{insert}'))

    def output_delete_box(self):
        self.output.delete('1.0', Ctk.END)

    def show_history(self, history: str) -> None:
        self.output.insert("0.0", history)


class App(Ctk.CTk):
    def __init__(self, controller: Controller):
        super().__init__()

        self.controllerfuncs = controller

        Ctk.set_appearance_mode("Light")

        self.title("RSS-Matix ALFA 2.0")
        # self.configure(background="white")
        self.geometry("800x765")

        self.var = Ctk.StringVar()
        self.label_reader = Ctk.CTkLabel(self,  text="LÄSARE: INAKTIV!")
        self.label_reader.grid(row=1, column=0)

        dyn_lapp = Ctk.CTkLabel(self, textvariable=self.var)
        dyn_lapp.grid(row=0, column=0)

        self.start_reader_bt = Ctk.CTkButton(
            self, text="Start RSS", command=self.start_reader)
        self.start_reader_bt.grid(
            row=10, column=0, sticky=Ctk.W, pady=2, padx=4)

        self.stop_reader_bt = Ctk.CTkButton(
            self, text='Stoppa RSS', command=self.stop_reader)
        self.stop_reader_bt.grid(
            row=11, column=0, sticky=Ctk.W, pady=2, padx=4)
        self.stop_reader_bt.configure(state="disabled")

        quit_bt = Ctk.CTkButton(
            self, text='Avsluta program', command=self.click_destroy)
        quit_bt.grid(row=12, column=0, sticky=Ctk.W, pady=2, padx=4)

    def click_destroy(self):
        logger.info("Avslutade programmet, see ya next time! :-D")
        try:
            self.controllerfuncs.model.stop_reader()
            App.destroy(self)
        except Exception:
            print(
                'reser fel i click_destroy (förmodligen pga p2 / rss_reader ej startad')
            sys.exit()

    def stop_reader(self):
        self.start_reader_bt.configure(state="enabled")
        self.stop_reader_bt.configure(state="disabled")
        self.controllerfuncs.model.stop_reader()
        self.label_reader.configure(text="LÄSARE: INAKTIV!")

    def start_reader(self):
        # kontorllera maillistan innan!
        check_empty_adress_dict = self.controllerfuncs.model.current_rss_urls()

        if bool(check_empty_adress_dict):
            self.start_reader_bt.configure(state="disabled")
            self.stop_reader_bt.configure(state="enabled")
            self.controllerfuncs.model.start_reader()
            self.label_reader.configure(text="LÄSARE: AKTIV!")

        else:
            print("listan med adresser är tom, kan ej starta reader!")
            messagebox.showwarning(
                title="Inga adresser", message="Kan ej starta RSS-läsare utan några adresser. :-( \n \n Vänligen lägg till RSS-adresser och försök igen!")


if __name__ == "__main__":
    from controller import Controller
    current_dir = os.path.dirname(__file__)
    current_dir_where_run_from = os.getcwd()
    print('Get current working directory : ', os.getcwd())
    obj_view = windows()
#asdasd