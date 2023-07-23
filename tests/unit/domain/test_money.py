from snack_machine.domain.money import Cent, TenCent, Quarter, Dollar, FiveDollar, TwentyDollar
import pytest


@pytest.mark.parametrize("value, amount, money_type", [
    (1, 0.01, Cent),
    (1, 0.1, TenCent),
    (1, 0.25, Quarter),
    (1, 1, Dollar),
    (1, 5, FiveDollar),
    (1, 20, TwentyDollar),
    (5, 0.05, Cent),
    (5, 0.5, TenCent),
    (4, 1, Quarter),
    (5, 5, Dollar),
    (2, 10, FiveDollar),
])
def test_money(value, amount, money_type):
    assert money_type(value).get_amount() == amount
    assert money_type(value) == money_type(value)


def test_sum_money():
    assert Dollar(1) + Dollar(1) == Dollar(2)
    assert FiveDollar(1) + FiveDollar(1) == FiveDollar(2)


def test_should_not_compare_different_money():
    assert Dollar(1) != FiveDollar(1)
    assert Dollar(1) != Cent(1)


def test_should_not_sum_different_money():
    with pytest.raises(ArithmeticError):
        assert Dollar(1) + Cent(1)


def test_should_not_init_money_with_negative_value():
    with pytest.raises(AssertionError):
        assert Dollar(-1)
