

from shared_kernel.domain.money import Cent, Dollar, FiveDollar, Quarter, TenCent, TwentyDollar
from common import AggregateRoot
from shared_kernel.domain.wallet import Wallet

from sqlalchemy.orm import Session, sessionmaker, declarative_base, Mapped, mapped_column
from sqlalchemy import create_engine, select


Base = declarative_base()


def SessionLocal(url="sqlite:///head_office.db"):
    engine = create_engine(
        url, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    return session()


class HeadOffice(AggregateRoot):

    def __init__(self):
        super().__init__()
        self._balance: float = 0
        self._cash: Wallet = Wallet()

    def unload_cash(self, money: Wallet):
        self._cash += money

    def load_cash_to_atm(self):
        self._cash = Wallet()

    def load_cash(self, money: Wallet):
        self._cash += money

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def cash(self) -> float:
        return self._cash.amount


class HeadOfficeOrm(Base):
    __tablename__ = 'head_office'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Cent: Mapped[int] = mapped_column(default=0)
    TenCent: Mapped[int] = mapped_column(default=0)
    Quarter: Mapped[int] = mapped_column(default=0)
    Dollar: Mapped[int] = mapped_column(default=0)
    FiveDollar: Mapped[int] = mapped_column(default=0)
    TwentyDollar: Mapped[int] = mapped_column(default=0)

    balance: Mapped[float] = mapped_column(default=0)

    def to_domain(self) -> HeadOffice:
        wallet = Wallet(
            Cent(self.Cent),
            TenCent(self.TenCent),
            Quarter(self.Quarter),
            Dollar(self.Dollar),
            FiveDollar(self.FiveDollar),
            TwentyDollar(self.TwentyDollar)
        )

        head_office = HeadOffice()
        head_office.load_cash(wallet)
        head_office._balance = self.balance
        head_office.id = self.id
        return head_office


class SqlAlchemyHeadOfficeRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(self):
        atm = HeadOfficeOrm()
        self.session.add(atm)

        self.session.commit()

    def get(self) -> HeadOffice:
        stmt = select(HeadOfficeOrm).limit(1)

        result = self.session.execute(stmt).scalars().first()
        if result is None:
            self.create()
            return self.get()

        return result.to_domain()

    def save(self, head_office: HeadOffice):

        stmt = select(HeadOfficeOrm).limit(1)
        orm = self.session.scalars(stmt).one()

        coins_and_notes = head_office._cash.count_coins_and_notes()
        for key, count in coins_and_notes.items():
            setattr(orm, key, count)

        orm.balance = head_office.balance

        self.session.commit()
