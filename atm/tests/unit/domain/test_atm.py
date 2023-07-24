import pytest
from atm.domain.atm import Atm
from shared_kernel.domain.money import Cent, TenCent, Dollar
from shared_kernel.domain.wallet import Wallet


def test_initial_values():
    atm = Atm()

    assert atm.money_inside == 0
    assert atm.money_charged == 0


def test_take_money_exchanges_money_with_commision():
    atm = Atm()

    atm.load_money(Wallet(Dollar(1)))

    atm.take_money(1)

    assert atm.money_inside == 0
    assert atm.money_charged == 1.01


def test_commision_is_at_least_one_cent():
    atm = Atm()

    atm.load_money(Wallet(Cent(1)))

    atm.take_money(0.01)

    assert atm.money_inside == 0
    assert atm.money_charged == 0.02


def test_commision_is_rounded_up_to_next_cent():
    atm = Atm()

    atm.load_money(Wallet(TenCent(1), Dollar(1)))

    atm.take_money(1.1)

    assert atm.money_inside == 0
    assert atm.money_charged == 1.12


def test_take_money_with_multiple_coins_and_notes():
    atm = Atm()

    atm.load_money(Wallet(TenCent(1), Dollar(1)))

    atm.take_money(1.1)

    assert atm.money_inside == 0
    assert atm.money_charged == 1.12


def test_take_money_w():
    atm = Atm()

    atm.load_money(Wallet(TenCent(100), Dollar(100), Cent(100)))

    atm.take_money(7)

    assert atm.money_charged == 7.07
    assert atm.money_inside == 104


@pytest.mark.parametrize("amount, expected", [
    (0,  "Invalid amount"),
    (-1, "Invalid amount"),
    (2, "Not enough money"),
    (1.01, "Not enough change"),
])
def test_take_money_with_invalid_amount(amount, expected):
    atm = Atm()

    atm.load_money(Wallet(TenCent(1), Dollar(1)))

    with pytest.raises(ValueError) as excinfo:
        atm.take_money(amount)

    assert str(excinfo.value) == expected
