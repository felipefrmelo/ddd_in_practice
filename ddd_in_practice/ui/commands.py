
from dataclasses import dataclass, field
from ddd_in_practice.domain.money import Money, Cent, TenCent, Dollar, FiveDollar, TwentyDollar, Quarter


@dataclass(unsafe_hash=True)
class Command:
    pass


class InsertMoney(Command):
    value: Money = field(init=False)


class InsertCent(InsertMoney):
    value = Cent(1)


class InsertTenCent(InsertMoney):
    value = TenCent(1)


class InsertQuarter(InsertMoney):
    value = Quarter(1)


class InsertDollar(InsertMoney):
    value = Dollar(1)


class InsertFiveDollar(InsertMoney):
    value = FiveDollar(1)


class InsertTwentyDollar(InsertMoney):
    value = TwentyDollar(1)


@dataclass(unsafe_hash=True)
class BuySnack(Command):
    position: int


class ReturnMoney(Command):
    pass
