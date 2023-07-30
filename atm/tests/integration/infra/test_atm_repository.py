
from atm.domain.atm import BalanceChangedEvent
from common import Event
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


def test_repository_should_raise_an_event_when_save_a_atm_with_money_charged(repository: AtmRepository):

    repository.create()

    atm = repository.find_by_id(1)

    atm.load_money(Wallet(Dollar(1)))

    atm.take_money(1)

    events = []

    q = None

    def publish_mock(queue: str, event: Event):
        events.append(event)
        nonlocal q
        q = queue

    repository.pub.publish = publish_mock

    repository.save(atm)

    assert len(events) == 1
    assert isinstance(events[0], BalanceChangedEvent)
    assert q == "BalanceChangedEvent"
    assert atm.domain_events == []
