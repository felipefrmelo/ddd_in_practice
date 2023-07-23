import pytest
from shared_kernel.domain.money import Dollar, Cent, TenCent, Quarter, FiveDollar, TwentyDollar
from shared_kernel.domain.wallet import Wallet


def test_initial_values():
    wallet = Wallet()
    assert wallet.amount == 0


def test_add_money():
    wallet = Wallet()
    wallet.add_money(Dollar(1))
    assert wallet.amount == 1


def test_add_money_with_multiple_coins_and_notes():
    wallet = Wallet()
    wallet.add_money(Dollar(1))
    wallet.add_money(Cent(1))
    wallet.add_money(TenCent(1))
    wallet.add_money(Quarter(1))
    wallet.add_money(FiveDollar(1))
    wallet.add_money(TwentyDollar(1))

    assert wallet.amount == 26.36


def test_sum_wallets():
    wallet1 = Wallet()
    wallet1.add_money(Dollar(1))
    wallet1.add_money(Dollar(1))
    wallet1.add_money(Cent(1))

    wallet2 = Wallet()
    wallet2.add_money(Dollar(1))
    wallet2.add_money(Dollar(1))

    wallet3 = wallet1 + wallet2
    assert wallet1.amount == 2.01
    assert wallet2.amount == 2
    assert wallet3.amount == 4.01


def test_count_coins_and_notes():
    wallet = Wallet(
        TenCent(1),
        Quarter(1),
        Dollar(2),
        Cent(5),
        FiveDollar(1),
        TwentyDollar(1)
    )

    assert wallet.count_coins_and_notes() == {
        "Cent": 5,
        "TenCent": 1,
        "Quarter": 1,
        "Dollar": 2,
        "FiveDollar": 1,
        "TwentyDollar": 1,
    }


def test_can_allocate_highest_denomination_first():
    wallet = Wallet(
        Quarter(4),
        Dollar(1),
    )

    allocated = wallet.allocate(1)

    assert allocated.count_coins_and_notes() == {
        "Cent": 0,
        "TenCent": 0,
        "Quarter": 0,
        "Dollar": 1,
        "FiveDollar": 0,
        "TwentyDollar": 0,
    }


@pytest.mark.parametrize("wallet, amount, expected", [
    (Wallet(Quarter(4), Dollar(1)), 1.25, True),
    (Wallet(Quarter(4), Dollar(1)), 1.35, False),
    (Wallet(Quarter(4), Dollar(1)), 1.15, False),
    (Wallet(Cent(4), Dollar(1)), 1.04, True),
    (Wallet(Cent(400), Dollar(1)), 1.05, True),
    (Wallet(TwentyDollar(1), FiveDollar(1), Dollar(1)), 26, True),
    (Wallet(TwentyDollar(1), FiveDollar(1), Dollar(1), Cent(1)), 26.01, True),
    (Wallet(TwentyDollar(1), FiveDollar(1), Dollar(1)), 25.9, False),
    (Wallet(TwentyDollar(1), FiveDollar(1), Dollar(1)), 26.1, False),
    (Wallet(FiveDollar(1), Dollar(1)), 5.9, False),
    (Wallet(FiveDollar(1), Dollar(1)), 6, True),
])
def test_can_allocate_using_multiple_denominations(wallet, amount, expected):
    assert wallet.can_allocate(amount) == expected
