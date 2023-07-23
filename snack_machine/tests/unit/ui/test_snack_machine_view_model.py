from snack_machine.domain.snack import Chocolate
from snack_machine.domain.snack_pile import SnackPile
from snack_machine.ui.snack_machine_view_model import SnackMachineViewModel
import snack_machine.ui.commands as Commands
import pytest


@pytest.fixture
def smv(repository):
    repository.create()
    snack_machine = repository.find_by_id(1)
    snack_machine.load_snack(1, SnackPile(Chocolate, 10, 1))
    snack_machine.load_snack(2, SnackPile(Chocolate, 10, 2))
    snack_machine.load_snack(3, SnackPile(Chocolate, 10, 1))

    return SnackMachineViewModel(snack_machine, repository)


@pytest.mark.parametrize("commands, expected", [
    ([Commands.InsertCent()], "$0.01"),
    ([Commands.InsertCent(), Commands.InsertCent()], "$0.02"),
    ([Commands.InsertCent(),
      Commands.InsertTenCent(),
      Commands.InsertQuarter(),
      Commands.InsertDollar(),
      Commands.InsertFiveDollar(),
      Commands.InsertTwentyDollar(),
      Commands.InsertCent()
      ], "$26.37"),
])
def test_insert_money_parametrized(commands, expected, smv: SnackMachineViewModel):
    for command in commands:
        smv.handle(command)

    assert smv.money_inserted == expected


def test_buy_snack(smv: SnackMachineViewModel):

    smv.handle(Commands.InsertDollar())

    smv.handle(Commands.BuySnack(1))

    assert smv.money_inserted == "$0.00"
    assert smv.money_inside == "$1.00"


def test_return_money(smv: SnackMachineViewModel):

    smv.handle(Commands.InsertDollar())

    smv.handle(Commands.ReturnMoney())

    assert smv.money_inserted == "$0.00"
    assert smv.money_inside == "$0.00"


def test_view_notes_and_coins(smv: SnackMachineViewModel):

    smv.handle(Commands.InsertDollar())
    smv.handle(Commands.InsertDollar())
    smv.handle(Commands.InsertFiveDollar())
    smv.handle(Commands.BuySnack(1))

    assert smv.count_coins_and_notes == {
        'Cent': 0,
        'Dollar': 1,
        'Quarter': 0,
        'TwentyDollar': 0,
        'FiveDollar': 0,
        'TenCent': 0
    }


def test_repository_save_is_Called(smv: SnackMachineViewModel):

    smv.handle(Commands.InsertDollar())

    smv.handle(Commands.BuySnack(1))

    snack_machine = smv.repository.find_by_id(1)
    assert snack_machine is not None
    assert snack_machine.money_inside == 1


def test_should_raise_if_not_enough_money_inserted(smv: SnackMachineViewModel):

    smv.handle(Commands.InsertDollar())

    with pytest.raises(ValueError):
        smv.handle(Commands.BuySnack(2))
