from pydantic import BaseModel
from common import RabbitMQPublisher
from shared_kernel.domain.money import Dollar

from shared_kernel.domain.wallet import Wallet
from atm.infra.repository import SqlAlchemyAtmRepository, SessionLocal

session = SessionLocal()

pub = RabbitMQPublisher()

repo = SqlAlchemyAtmRepository(session, pub)


class WalletRequest(BaseModel):
    one_dollar_count: int = 0

    def to_domain(self) -> Wallet:
        return Wallet(Dollar(self.one_dollar_count))


def load_cash(atm_id: int, wallet_request: WalletRequest) -> Wallet:

    return Wallet()


def get_atms():
    return repo.get_all()
