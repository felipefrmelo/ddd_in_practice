import re
import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
from shared_kernel.domain.money import *
from shared_kernel.domain.wallet import Wallet
from snack_machine.domain.snack import Chocolate, Gum, Soda
from snack_machine.domain.snack_pile import SnackPile

from snack_machine.infra.repository import SessionLocal, SnackOrm, SqlAlchemySnackMachineRepository
from snack_machine.ui.snack_machine_view_model import SnackMachineViewModel
import snack_machine.ui.commands as Commands

import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class SnackMachineApp(tk.Tk):
    def __init__(self, snack_machine_view_model: SnackMachineViewModel):

        self.snack_machine_view_model = snack_machine_view_model

        super().__init__()
        self.title("Snack Machine")

        self.layout1 = tk.Frame(self)
        self.layout2 = tk.Frame(self)

        self.layout1.grid(row=0, column=0, columnspan=1, padx=20)
        self.layout2.grid(row=0, column=2, padx=20)

        self.render_slot()
        self.render_buy_snack_button()
        self.render_return_money_button()
        self.render_money_inserted_label()
        self.render_put_money_buttons()
        self.render_money_inside_label()
        self.render_notes_labels()
        self.update_notes_labels()

    def render_slot(self):
        slots = self.snack_machine_view_model.slots
        path = "snack_machine/ui/Images/"
        self.slots_images = {
            slot: self.load_resized_image(f"{path}{slot.snack_name}.png") for slot in slots
        }

        self.slots_labels = {}
        for i, slot in enumerate(slots, 0):
            self.slots_labels[slot] = tk.Label(
                self.layout1, image=self.slots_images[
                    slot], text=self.formatSlot(slot),
                justify=tk.LEFT, compound=tk.LEFT, font="Helvetica 12 bold",
                padx=10, pady=10,
            )
            self.slots_labels[slot].grid(
                row=i, column=0, padx=10, pady=10,
            )

    def formatSlot(self, slot):
        return f"{locale.currency(slot.snack_price, grouping=True)}\nleft: {slot.snack_pile.quantity}"

    def render_buy_snack_button(self):
        for position in range(1, 4):
            def button_command(cmd=position):
                return self.buy_snack(cmd)

            button = tk.Button(
                self.layout2, text=f"Buy #{position}", command=button_command)
            button.grid(row=0, column=position - 1, pady=10)

    def render_money_inserted_label(self):
        self.money_inserted_label = tk.Label(
            self.layout2, text=f"Money Inserted: {self.snack_machine_view_model.money_inserted}")
        self.money_inserted_label.grid(row=1, column=1, pady=10)

    def render_put_money_buttons(self):
        labels = ["¢1", "¢10", "¢25", "$1", "$5", "$20"]
        commands = [Commands.InsertCent, Commands.InsertTenCent, Commands.InsertQuarter,
                    Commands.InsertDollar, Commands.InsertFiveDollar, Commands.InsertTwentyDollar]
        for i, (label, command) in enumerate(zip(labels, commands)):

            def button_command(cmd=command()):
                return self.insert_money(cmd)

            button = tk.Button(
                self.layout2, text=f'Put {label}', command=button_command,
                width=5, height=2,
                relief=tk.RAISED,
                activebackground='light blue',
                font=('Helvetica', 10, 'bold'),
            )
            button.grid(row=4 if i < 3 else 5, column=i % 3, padx=5, pady=5)

    def render_return_money_button(self):
        self.return_button = tk.Button(
            self.layout2, text="Return Money", command=self.return_money)
        self.return_button.grid(row=6, column=1, pady=10)

    def render_money_inside_label(self):
        self.money_inside_label = tk.Label(
            self, text=f"Money Inside: {self.snack_machine_view_model.money_inside}")
        self.money_inside_label.grid(row=7, column=1, pady=10)

    def render_notes_labels(self):
        self.notes_labels = {}
        notes = ['1c',  '10c',  '25c', '1d', '5d', '20d']
        path = "snack_machine/ui/Images/"
        self.notes_images = {
            k: self.load_resized_image(f"{path}{k}.png") for k in notes
        }

        for i, note in enumerate(notes):
            self.notes_labels[note] = tk.Label(
                self, image=self.notes_images[note],
                justify=tk.RIGHT, compound=tk.RIGHT

            )
            column, row = i % 3, 9 if 'c' in note else 10
            self.notes_labels[note].grid(
                row=row, column=column, padx=15, pady=5, sticky='S')

    def insert_money(self, command: Commands.Command):
        self.snack_machine_view_model.handle(command)
        self.update()

    def buy_snack(self, position):
        try:
            self.snack_machine_view_model.handle(Commands.BuySnack(position))
            self.update()
            self.money_inside_label.config(
                text=f"Money Inside: {self.snack_machine_view_model.money_inside}")
            messagebox.showinfo("Success", "Snack purchased! Enjoy!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def return_money(self):
        self.snack_machine_view_model.handle(Commands.ReturnMoney())
        self.update()

    def load_resized_image(self, image_path):
        image = Image.open(image_path)
        width = self.get_width(image_path)
        image = image.resize((width, 100), Image.DEFAULT_STRATEGY)
        return ImageTk.PhotoImage(image)

    def get_width(self, image_path):
        is_chocolate = re.search(r'Chocolate', image_path)
        if is_chocolate:
            return 150

        is_soda = re.search(r'Soda', image_path)
        if is_soda:
            return 90

        is_gum = re.search(r'Gum', image_path)
        if is_gum:
            return 100

        is_cent = re.search(r'\d+c', image_path)

        return 100 if is_cent else 200

    def update(self):
        self.update_money_inserted_label()
        self.update_notes_labels()
        self.update_slots_labels()

    def update_money_inserted_label(self):
        self.money_inserted_label.config(
            text=f"Money Inserted: {self.snack_machine_view_model.money_inserted}")

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
                text=f"{self.snack_machine_view_model.count_coins_and_notes[notes[note]]}", compound=tk.LEFT, padx=5,
            )

    def update_slots_labels(self):
        for i, slot in enumerate(self.snack_machine_view_model.slots):
            self.slots_labels[slot].config(
                text=self.formatSlot(slot))


def get_snack_machine(repository: SqlAlchemySnackMachineRepository):
    if repository.find_by_id(1) is None:
        repository.create()

    snack_machine = repository.find_by_id(1)
    assert snack_machine is not None
    return snack_machine


def init_snacks():
    session = SessionLocal()
    try:
        session.add_all([SnackOrm.from_domain(Chocolate),
                         SnackOrm.from_domain(Soda), SnackOrm.from_domain(Gum)])
        session.commit()
    except Exception:
        pass

    session.close()


if __name__ == "__main__":
    init_snacks()

    session = SessionLocal()
    repository = SqlAlchemySnackMachineRepository(session)

    snack_machine = get_snack_machine(repository)
    snack_machine.load_snack(1, SnackPile(Chocolate, 10, 3))
    snack_machine.load_snack(2, SnackPile(Soda, 10, 2))
    snack_machine.load_snack(3, SnackPile(Gum, 10, 1))

    snack_machine.load_money(Wallet(Dollar(100), Cent(100), Quarter(
        100), TenCent(100), FiveDollar(100), TwentyDollar(100)))
    repository.save(snack_machine)

    snack_machine_view_model = SnackMachineViewModel(snack_machine, repository)
    app = SnackMachineApp(snack_machine_view_model)
    app.mainloop()
