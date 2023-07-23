from dataclasses import dataclass
from snack_machine.domain.money import Money
from snack_machine.domain.slot import Slot
from snack_machine.domain.snack_pile import SnackPile
from snack_machine.domain.wallet import Wallet


class EntityID:
    value: int

    @property
    def id(self):
        return self.value

    @id.setter
    def id(self, value: int):
        self.value = value


class SnackMachine(EntityID):

    def __init__(self):
        self._money_in_transaction: float = 0
        self._money_inside: Wallet = Wallet()
        self.slots = [Slot(1), Slot(2), Slot(3)]

    def load_money(self, money: Wallet):
        self._money_inside = self._money_inside + money

    def load_snack(self, position: int, snack_pile: SnackPile):
        slot = self.get_slot(position)
        slot.snack_pile = snack_pile

    def get_slot(self, position: int):
        return next(slot for slot in self.slots if slot.position == position)

    def get_snack_pile(self, position: int):
        return self.get_slot(position).snack_pile

    def insert_money(self, money: Money):
        if money.value > 1:
            raise ValueError("Only one coin or note can be inserted at a time")

        self._money_in_transaction = self._money_in_transaction + money.get_amount()
        self._money_inside.add_money(money)

    def return_money(self):
        self._money_inside -= self._money_inside.allocate(
            self._money_in_transaction)

        self._money_in_transaction = 0

    def can_buy_snack(self, position: int):
        snack_pile = self.get_snack_pile(position)

        if self.money_in_transaction < snack_pile.price:
            raise ValueError("Not enough money")

        if snack_pile.quantity <= 0:
            raise ValueError("No snacks left")

        if not self._money_inside.can_allocate(self._money_in_transaction - snack_pile.price):
            raise ValueError("Not enough change")

    def buy_snack(self, position: int):

        self.can_buy_snack(position)

        slot = self.get_slot(position)

        slot.snack_pile = slot.snack_pile.subtract_one()

        change = self._money_inside.allocate(
            self._money_in_transaction - slot.snack_pile.price)

        self._money_inside = self._money_inside - change

        self._money_in_transaction = 0

    @ property
    def money_inside(self):
        return self._money_inside.amount

    @ property
    def money_in_transaction(self):
        return float("{:.2f}".format(self._money_in_transaction))

    def count_coins_and_notes(self):
        return self._money_inside.count_coins_and_notes()

    def __repr__(self):
        return f"Money inside: {self.money_inside}, Money in transaction: {self.money_in_transaction}"

    def __str__(self):
        return f"Money inside: {self.money_inside}, Money in transaction: {self.money_in_transaction}"
