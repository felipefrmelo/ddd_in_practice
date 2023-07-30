from atm.domain.atm import Atm
from common import Publisher
from shared_kernel.domain.wallet import Wallet
from abc import ABC, abstractmethod
from shared_kernel.domain.money import Cent, Dollar, FiveDollar, Money, Quarter, TenCent, TwentyDollar

from sqlalchemy.orm import Session, sessionmaker, declarative_base, Mapped, mapped_column
from sqlalchemy import create_engine, select


class AtmRepository(ABC):

    def __init__(self, pub: Publisher):
        self.pub = pub

    @abstractmethod
    def create(self):
        ...

    @abstractmethod
    def find_by_id(self, id) -> Atm:
        ...

    def save(self, atm: Atm):
        self._save(atm)
        while atm.domain_events:
            event = atm.domain_events.pop()
            self.pub.publish(event.name, event)

    @abstractmethod
    def _save(self, atm: Atm):
        raise NotImplementedError


Base = declarative_base()


def SessionLocal(url):
    engine = create_engine(
        url, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    return session()


class AtmOrm(Base):
    __tablename__ = 'atm'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Cent: Mapped[int] = mapped_column(default=0)
    TenCent: Mapped[int] = mapped_column(default=0)
    Quarter: Mapped[int] = mapped_column(default=0)
    Dollar: Mapped[int] = mapped_column(default=0)
    FiveDollar: Mapped[int] = mapped_column(default=0)
    TwentyDollar: Mapped[int] = mapped_column(default=0)
    MoneyCharged: Mapped[float] = mapped_column(default=0)

    @property
    def money_inside(self) -> list[Money]:
        return [
            Cent(self.Cent),
            TenCent(self.TenCent),
            Quarter(self.Quarter),
            Dollar(self.Dollar),
            FiveDollar(self.FiveDollar),
            TwentyDollar(self.TwentyDollar)
        ]

    def to_domain(self) -> Atm:
        wallet = Wallet(*self.money_inside)

        atm = Atm()
        atm.load_money(wallet)
        atm._money_charged = self.MoneyCharged
        atm.id = self.id
        return atm


class SqlAlchemyAtmRepository(AtmRepository):

    def __init__(self, session: Session, pub: Publisher):
        super().__init__(pub)
        self.session = session

    def create(self):
        atm = AtmOrm()
        self.session.add(atm)

        self.session.commit()

    def find_by_id(self, id):
        atms = self.session.query(
            AtmOrm).filter_by(id=id).all()

        return next((s.to_domain() for s in atms), None)

    def _save(self, atm: Atm):
        stmt = select(AtmOrm).where(
            AtmOrm.id == atm.id)
        atm_orm = self.session.scalars(stmt).one()

        coins_and_notes = atm.count_coins_and_notes()
        for key, count in coins_and_notes.items():
            setattr(atm_orm, key, count)

        atm_orm.MoneyCharged = atm._money_charged

        self.session.commit()
