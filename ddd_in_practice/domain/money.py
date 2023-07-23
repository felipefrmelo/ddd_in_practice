from dataclasses import dataclass, field


@dataclass(frozen=True)
class Money:
    value: int
    _multiplier: float = field(init=False, default=1, compare=False)

    def __post_init__(self):
        assert self.value >= 0, "Money value cannot be negative"

    def get_amount(self):
        return self.value * self._multiplier

    def __add__(self, other):
        cls = type(self)
        if not isinstance(other, cls):
            raise ArithmeticError(f"Cannot sum {cls} with {type(other)}")

        return cls(self.value + other.value)

    def __sub__(self, other):
        cls = type(self)
        if not isinstance(other, cls):
            raise ArithmeticError(f"Cannot subtract {cls} with {type(other)}")

        return cls(self.value - other.value)

    @classmethod
    def from_value(cls, value):
        return cls(value)


class Cent(Money):
    _multiplier = 1/100


class TenCent(Money):
    _multiplier = 1/10


class Quarter(Money):
    _multiplier = 1/4


class Dollar(Money):
    _multiplier = 1


class FiveDollar(Dollar):
    _multiplier = 5


class TwentyDollar(Dollar):
    _multiplier = 20
