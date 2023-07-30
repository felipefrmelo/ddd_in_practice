

from shared_kernel.domain.wallet import Wallet
from snack_machine.infra.repository import SqlAlchemySnackMachineRepository, SessionLocal

session = SessionLocal()

repo = SqlAlchemySnackMachineRepository(session)


def get_snack_machines():
    return repo.get_all()


def unload_cash(snack_machine_id: int) -> Wallet:
    snack_machine = repo.find_by_id(snack_machine_id)
    if not snack_machine:
        raise Exception("Snack machine not found")
    cash = snack_machine.unload_cash()
    repo.save(snack_machine)

    return cash
