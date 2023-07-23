from snack_machine.domain.money import *


class Wallet:

    def __init__(self, *args: Money):
        self._money: dict[str, Money] = {}
        for money_type in (Cent, TenCent, Quarter, Dollar, FiveDollar, TwentyDollar):
            self._money[money_type.__name__] = money_type.from_value(0)

        for money in args:
            self.add_money(money)

    def add_money(self, money: Money):
        money_name = type(money).__name__
        self._money[money_name] += money

    @property
    def amount(self):
        return sum([money.get_amount() for money in self._money.values()])

    def __add__(self, other):

        if not isinstance(other, Wallet):
            raise TypeError(
                f"Cannot sum {type(self)} with {type(other)}")

        values = [s1 + s2 for s1,
                  s2 in zip(self._money.values(), other._money.values())]

        wallet = Wallet(*values)
        return wallet

    def __sub__(self, other):

        if not isinstance(other, Wallet):
            raise TypeError(
                f"Cannot subtract {type(self)} with {type(other)}")

        values = [s1 - s2 for s1,
                  s2 in zip(self._money.values(), other._money.values())]

        wallet = Wallet(*values)
        return wallet

    def count_coins_and_notes(self):
        return {
            money_name: money.value
            for money_name, money in self._money.items()
        }

    def can_allocate(self, amount: float):
        allocated = self.allocate(amount)

        return float(f"{allocated.amount:.2f}") == float(f"{amount:.2f}")

    def allocate(self, amount: float):

        moneys = sorted(self._money.values(),
                        key=lambda x: x._multiplier, reverse=True)

        w = []
        for money in moneys:
            moneyCount = self.countMoney(amount, money)
            amount = self.subtractAmount(amount, moneyCount, money)
            w.append(money.from_value(moneyCount))

        return Wallet(
            *w,
        )

    def subtractAmount(self, amount, moneyCount, money):
        return amount - moneyCount * money._multiplier

    def countMoney(self, amount, money):
        return min(
            int(round((round(amount, 2) / money._multiplier), 2)), money.value)
