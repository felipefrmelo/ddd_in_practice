import pytest
from ddd_in_practice.domain.snack_machine import SnackMachine
from ddd_in_practice.domain.money import Cent, Dollar, FiveDollar, TenCent, Quarter, TwentyDollar
from ddd_in_practice.domain.snack_pile import SnackPile
from ddd_in_practice.domain.wallet import Wallet
from ddd_in_practice.domain.snack import *


def test_initial_values():
    snack_machine = SnackMachine()
    assert snack_machine.money_inside == 0
    assert snack_machine.money_in_transaction == 0


def test_insert_money():
    snack_machine = SnackMachine()
    snack_machine.insert_money(Dollar(1))
    assert snack_machine.money_in_transaction == 1


def test_can_not_insert_more_than_one_coin_or_note_at_a_time():
    snack_machine = SnackMachine()
    two_dollars = Dollar(2)
    with pytest.raises(ValueError):
        snack_machine.insert_money(two_dollars)


def test_inserted_money_goes_to_money_in_transaction():
    snack_machine = SnackMachine()
    snack_machine.insert_money(Dollar(1))
    snack_machine.insert_money(Quarter(1))
    assert snack_machine.money_in_transaction == 1.25


def test_return_money():
    snack_machine = SnackMachine()
    snack_machine.insert_money(Dollar(1))
    snack_machine.insert_money(Quarter(1))
    snack_machine.return_money()
    assert snack_machine.money_in_transaction == 0
    assert snack_machine.money_inside == 0


def test_buy_snack():
    snack_machine = SnackMachine()
    snack_machine.insert_money(Dollar(1))
    snack_machine.insert_money(Dollar(1))
    snack_machine.load_snack(1, SnackPile(Chocolate, 10, 1))
    snack_machine.buy_snack(1)

    assert snack_machine.get_snack_pile(1).quantity == 9
    assert snack_machine.money_inside == 1
    assert snack_machine.money_in_transaction == 0


def test_buy_two_snacks():
    snack_machine = SnackMachine()

    snack_machine.load_snack(1, SnackPile(Chocolate, 10, 1))
    snack_machine.load_snack(1, SnackPile(Chocolate, 10, 1))

    snack_machine.insert_money(Dollar(1))
    snack_machine.insert_money(Dollar(1))
    snack_machine.buy_snack(1)
    assert snack_machine.money_inside == 1
    assert snack_machine.money_in_transaction == 0

    snack_machine.insert_money(Dollar(1))
    snack_machine.insert_money(Dollar(1))
    snack_machine.buy_snack(1)
    assert snack_machine.money_inside == 2
    assert snack_machine.money_in_transaction == 0


@pytest.mark.parametrize("money, quantity, expected", [
    (TenCent, 10, 1),
    (Cent, 503, 1),
    (Cent, 403, 1),
    (Cent, 4103, 1),
])
def test_buy_snack_with_more_money(money, quantity, expected):
    snack_machine = SnackMachine()
    snack_machine.load_money(Wallet(Cent(100), TenCent(10)))
    snack_machine.load_snack(1, SnackPile(Chocolate, 1, 1))
    inside_before = snack_machine.money_inside

    for _ in range(quantity):
        snack_machine.insert_money(money(1))

    snack_machine.buy_snack(1)

    assert snack_machine.money_inside == expected + inside_before
    assert snack_machine.money_in_transaction == 0


def test_not_enough_change():
    snack_machine = SnackMachine()
    snack_machine.insert_money(Dollar(1))
    snack_machine.insert_money(Dollar(1))
    snack_machine.load_snack(1, SnackPile(Chocolate, 1, 1.5))

    with pytest.raises(ValueError):
        snack_machine.buy_snack(1)

    assert snack_machine.money_in_transaction == 2


def test_can_not_buy_snack_if_not_enough_money_inserted():
    snack_machine = SnackMachine()
    snack_machine.insert_money(Dollar(1))
    snack_machine.load_snack(1, SnackPile(Chocolate, 1, 1.1))

    with pytest.raises(ValueError):
        snack_machine.buy_snack(1)

    assert snack_machine.money_in_transaction == 1


def test_can_not_buy_snack_when_there_is_no_snacks():
    snack_machine = SnackMachine()
    snack_machine.insert_money(Dollar(1))

    with pytest.raises(ValueError):
        snack_machine.buy_snack(1)

    assert snack_machine.money_in_transaction == 1


def test_count_coins_and_notes():
    snack_machine = SnackMachine()
    snack_machine.load_money(Wallet(Dollar(1), Quarter(
        1), TwentyDollar(1), FiveDollar(1), TenCent(1), TenCent(1)))

    assert snack_machine.money_inside == 26.45

    assert snack_machine.count_coins_and_notes() == {
        'Cent': 0,
        'Dollar': 1,
        'Quarter': 1,
        'TwentyDollar': 1,
        'FiveDollar': 1,
        'TenCent': 2

    }
