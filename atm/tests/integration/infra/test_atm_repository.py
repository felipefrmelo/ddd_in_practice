
from shared_kernel.domain.money import Dollar
from shared_kernel.domain.wallet import Wallet
from atm.infra.repository import AtmRepository


def test_repository_can_save_a_atm(repository: AtmRepository):

    repository.create()

    atm = repository.find_by_id(1)

    assert atm is not None
    assert atm.money_inside == 0


def test_repository_can_save_a_atm_with_money(repository: AtmRepository):

    repository.create()

    atm = repository.find_by_id(1)

    atm.load_money(Wallet(Dollar(1)))

    repository.save(atm)

    atm = repository.find_by_id(1)

    assert atm is not None
    assert atm.money_inside == 1
    assert atm.money_charged == 0


def test_repository_can_save_a_atm_with_money_charged(repository: AtmRepository):

    repository.create()

    atm = repository.find_by_id(1)

    atm.load_money(Wallet(Dollar(1)))

    atm.take_money(1)

    repository.save(atm)

    atm = repository.find_by_id(1)

    assert atm is not None
    assert atm.money_inside == 0
    assert atm.money_charged == 1.01
