import re
import tkinter as tk
from tkinter import NUMERIC, StringVar, messagebox
from PIL import ImageTk, Image

from atm.infra.repository import SessionLocal, SqlAlchemyAtmRepository
from atm.ui.atm_view_model import AtmViewModel
import atm.ui.commands as Commands

import locale
from common import RabbitMQPublisher
from shared_kernel.domain.money import *

from shared_kernel.domain.wallet import Wallet

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class AtmApp(tk.Tk):
    def __init__(self, atm_view_model: AtmViewModel):

        self.atm_view_model = atm_view_model

        super().__init__()
        self.title("ATM Machine")

        self.render_money_inserted_label()
        self.render_money_inside_label()
        self.render_notes_labels()
        self.render_input_money()
        self.update_notes_labels()

    def render_money_inserted_label(self):
        self.money_inserted_label = tk.Label(
            self, text=f"Money Charged: {self.atm_view_model.money_charged}", font="Helvetica 12 bold")
        self.money_inserted_label.grid(row=1, column=1, pady=10)

    def render_money_inside_label(self):
        self.money_inside_label = tk.Label(
            self, text=f"Money Inside: {self.atm_view_model.money_inside}", font="Helvetica 12 bold")
        self.money_inside_label.grid(row=2, column=1, pady=10)

    def render_notes_labels(self):
        self.notes_labels = {}
        notes = ['1c',  '10c',  '25c', '1d', '5d', '20d']
        path = "atm/ui/Images/"
        self.notes_images = {
            k: self.load_resized_image(f"{path}{k}.png") for k in notes
        }

        for i, note in enumerate(notes):
            self.notes_labels[note] = tk.Label(
                self, image=self.notes_images[note],
                justify=tk.RIGHT, compound=tk.RIGHT

            )
            column, row = i % 3, 3 if 'c' in note else 4
            self.notes_labels[note].grid(
                row=row, column=column, padx=15, pady=5, sticky='S')

    def render_input_money(self):
        self.take_money_i = StringVar()
        self.input_money = tk.Entry(
            self, textvariable=self.take_money_i, width=10, justify=tk.RIGHT)
        self.input_money.grid(row=5, column=1, pady=10)
        self.input_money.focus_set()

        self.input_money_button = tk.Button(
            self, text="Take money", command=lambda: self.take_money(float(self.input_money.get())))
        self.input_money_button.grid(row=6, column=1, pady=10)

    def take_money(self, amount: float):
        try:
            self.atm_view_model.handle(Commands.TakeMoney(amount))
            self.update()
            messagebox.showinfo(
                "Success", f"You have taken {locale.currency(amount, grouping=True)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_resized_image(self, image_path):
        image = Image.open(image_path)
        width = self.get_width(image_path)
        image = image.resize((width, 100), Image.DEFAULT_STRATEGY)
        return ImageTk.PhotoImage(image)

    def get_width(self, image_path):

        is_cent = re.search(r'\d+c', image_path)

        return 100 if is_cent else 200

    def update(self):
        self.update_money_charged_label()
        self.update_notes_labels()

    def update_money_charged_label(self):
        self.money_inserted_label.config(
            text=f"Money Charged: {self.atm_view_model.money_charged}")

    def update_money_inside_label(self):
        self.money_inside_label.config(
            text=f"Money Inside: {self.atm_view_model.money_inside}")

    def update_notes_labels(self):
        notes = {
            "1c": 'Cent',
            "1d": 'Dollar',
            "5d": 'FiveDollar',
            "10c": 'TenCent',
            "20d": 'TwentyDollar',
            "25c": 'Quarter',
        }

        for note in notes:
            self.notes_labels[note].config(
                text=f"{self.atm_view_model.count_coins_and_notes[notes[note]]}", compound=tk.LEFT, padx=5,
            )


def get_atm(repository: SqlAlchemyAtmRepository):
    if repository.find_by_id(1) is None:
        repository.create()
        atm = repository.find_by_id(1)
        if atm:
            atm.load_money(Wallet(Dollar(100), Cent(100), Quarter(
                100), TenCent(100), FiveDollar(100), TwentyDollar(100)))
            repository.save(atm)

    atm = repository.find_by_id(1)
    assert atm is not None
    return atm


db_url = "sqlite:///atm.db"


if __name__ == "__main__":

    pub = RabbitMQPublisher("localhost")

    session = SessionLocal(db_url)
    repository = SqlAlchemyAtmRepository(session, pub)

    atm = get_atm(repository)

    atm_view_model = AtmViewModel(atm, repository)
    app = AtmApp(atm_view_model)
    app.mainloop()
