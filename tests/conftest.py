from ddd_in_practice.domain.snack import Snack, Chocolate, Gum, Soda
from ddd_in_practice.infra.repository import SnackOrm, SqlAlchemySnackMachineRepository, SessionLocal
import pytest


@pytest.fixture
def repository():
    session = SessionLocal("sqlite:///:memory:")
    session.add_all([SnackOrm.from_domain(Chocolate),
                    SnackOrm.from_domain(Gum), SnackOrm.from_domain(Soda)])

    return SqlAlchemySnackMachineRepository(session)
