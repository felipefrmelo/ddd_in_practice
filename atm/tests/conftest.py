from atm.infra.repository import SqlAlchemyAtmRepository, SessionLocal
import pytest


@pytest.fixture
def repository():
    session = SessionLocal("sqlite:///:memory:")

    return SqlAlchemyAtmRepository(session)
