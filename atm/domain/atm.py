from dataclasses import dataclass
from common import AggregateRoot, Event
from shared_kernel.domain.wallet import Wallet


@dataclass
class BalanceChangedEvent(Event):
    value: float


class Atm(AggregateRoot):
    commission_rate = 0.01

    def __init__(self):
        super().__init__()
        self._money_charged: float = 0
        self._money_inside: Wallet = Wallet()

    def load_money(self, money: Wallet):
        self._money_inside = self._money_inside + money

    def can_take_money(self, amount: float):

        if amount <= 0:
            raise ValueError("Invalid amount")

        if amount > self.money_inside:
            raise ValueError("Not enough money")

        if not self._money_inside.can_allocate(amount):
            raise ValueError("Not enough change")

    def take_money(self, amount: float):
        self.can_take_money(amount)

        self._money_inside -= self._money_inside.allocate(amount)
        self._money_charged += self.caluculate_amount_with_commission(amount)

        self.add_domain_event(BalanceChangedEvent(self._money_charged))

    def caluculate_amount_with_commission(self, amount):
        commission = amount * self.commission_rate
        less_than_cent = commission % 0.01

        if less_than_cent > 0.00001:
            commission = commission - less_than_cent + 0.01
        return amount + commission

    @property
    def money_inside(self):
        return self._money_inside.amount

    @property
    def money_charged(self):
        return self._money_charged

    def count_coins_and_notes(self):
        return self._money_inside.count_coins_and_notes()
