from snack_machine.domain.money import Dollar, TwentyDollar
from snack_machine.domain.snack import Chocolate, Gum, Soda
from snack_machine.domain.snack_pile import SnackPile
from snack_machine.domain.wallet import Wallet
from snack_machine.infra.repository import SnackMachineRepository


def test_repository_can_save_a_snack_machine(repository: SnackMachineRepository):

    repository.create()

    snack_machine = repository.find_by_id(1)
    assert snack_machine is not None
    assert snack_machine.money_inside == 0


def test_repository_can_save_a_snack_machine_with_money_inside(repository: SnackMachineRepository):

    repository.create()
    snack_machine = repository.find_by_id(1)
    assert snack_machine is not None

    snack_machine.load_money(
        Wallet(Dollar(1), Dollar(1), Dollar(1), TwentyDollar(1)))

    repository.save(snack_machine)

    snack_machine = repository.find_by_id(1)
    assert snack_machine is not None
    assert snack_machine.money_inside == 23
    assert snack_machine.money_in_transaction == 0


def test_repository_can_save_a_snack_machine_slots(repository: SnackMachineRepository):

    repository.create()
    snack_machine = repository.find_by_id(1)
    assert snack_machine is not None

    snack_machine.load_snack(1, SnackPile(Chocolate, 10, 3))
    snack_machine.load_snack(2, SnackPile(Soda, 10, 2))
    snack_machine.load_snack(3, SnackPile(Gum, 10, 1))

    repository.save(snack_machine)

    snack_machine = repository.find_by_id(1)
    assert snack_machine is not None
    assert snack_machine.get_snack_pile(1).quantity == 10
    assert snack_machine.get_snack_pile(2).quantity == 10
    assert snack_machine.get_snack_pile(3).quantity == 10


def test_repository_can_save_a_snack_machine_slots_when_buy(repository: SnackMachineRepository):

    repository.create()
    snack_machine = repository.find_by_id(1)
    assert snack_machine is not None

    snack_machine.load_snack(1, SnackPile(Chocolate, 10, 3))
    snack_machine.load_snack(2, SnackPile(Soda, 10, 2))
    snack_machine.load_snack(3, SnackPile(Gum, 10, 1))
    snack_machine.insert_money(Dollar(1))
    snack_machine.buy_snack(3)

    repository.save(snack_machine)

    snack_machine = repository.find_by_id(1)
    assert snack_machine is not None
    gum = snack_machine.get_snack_pile(3)
    assert gum.quantity == 9
    assert gum.snack.name == "Gum"
    assert snack_machine.money_inside == 1


def test_should_return_none_when_snack_machine_not_found(repository: SnackMachineRepository):

    snack_machine = repository.find_by_id(1)
    assert snack_machine is None
