from collections import defaultdict
from atm.infra.repository import SqlAlchemyAtmRepository, SessionLocal
import pytest

from common import Event


class MockPublisher:

    def __init__(self):
        self.events = defaultdict(list)

    def publish(self, queue: str, event: Event):
        self.events[queue].append(event)

    def subscribe(self, queue: str, callback):
        ...


@pytest.fixture
def pub():
    return MockPublisher()


@pytest.fixture
def repository(pub):
    session = SessionLocal("sqlite:///:memory:")

    return SqlAlchemyAtmRepository(session, pub)
