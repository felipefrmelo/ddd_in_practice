from atm.infra.repository import AtmRepository
from atm.ui.atm_view_model import AtmViewModel
import atm.ui.commands as Commands
import pytest
from shared_kernel.domain.money import Cent, Dollar, FiveDollar, Quarter, TenCent, TwentyDollar

from shared_kernel.domain.wallet import Wallet


@pytest.fixture
def smv(repository: AtmRepository):
    repository.create()
    atm = repository.find_by_id(1)

    atm.load_money(Wallet(Dollar(100), Cent(100), TenCent(
        100), TwentyDollar(100), FiveDollar(100), Quarter(100)))

    return AtmViewModel(atm, repository)


def test_insert_dollar(smv: AtmViewModel):

    assert smv.money_charged == "$0.00"
    assert smv.money_inside == "$2,636.00"


def test_take_money(smv: AtmViewModel):

    smv.handle(Commands.TakeMoney(7.0))

    assert smv.money_charged == "$7.07"
    assert smv.money_inside == "$2,629.00"


def test_view_notes_and_coins(smv: AtmViewModel):

    assert smv.count_coins_and_notes == {
        'Cent': 100,
        'Dollar': 100,
        'FiveDollar': 100,
        'Quarter': 100,
        'TenCent': 100,
        'TwentyDollar': 100
    }


def test_should_raise_if_not_enough_money_inserted(smv: AtmViewModel):

    with pytest.raises(ValueError):
        smv.handle(Commands.TakeMoney(3000))
