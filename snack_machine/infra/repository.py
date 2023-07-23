from snack_machine.domain.slot import Slot
from snack_machine.domain.snack import Snack
from snack_machine.domain.snack_pile import SnackPile
from snack_machine.domain.wallet import Wallet
from abc import ABC, abstractmethod
from snack_machine.domain.money import Cent, Dollar, FiveDollar, Money, Quarter, TenCent, TwentyDollar

from snack_machine.domain.snack_machine import SnackMachine

from sqlalchemy.orm import Session, sessionmaker, declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, create_engine, select


class SnackMachineRepository(ABC):

    @abstractmethod
    def create(self):
        ...

    @abstractmethod
    def find_by_id(self, id) -> SnackMachine:
        ...

    @abstractmethod
    def save(self, snack_machine: SnackMachine):
        ...


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


class SnackOrm(Base):
    __tablename__ = 'snacks'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    def to_domain(self) -> Snack:
        return Snack(self.id, self.name)

    @staticmethod
    def from_domain(snack: Snack):
        return SnackOrm(id=snack.id, name=snack.name)


class SlotOrm(Base):
    __tablename__ = 'slots'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    position: Mapped[int] = mapped_column()
    snack_id: Mapped[int] = mapped_column(
        ForeignKey('snacks.id'), nullable=True)
    snack: Mapped[SnackOrm] = relationship('SnackOrm')
    quantity: Mapped[int] = mapped_column(default=0)
    price: Mapped[float] = mapped_column(default=0.0)
    snack_machine_id: Mapped[int] = mapped_column(
        ForeignKey('snack_machines.id'))

    def to_domain(self) -> Slot:
        slot = Slot(self.position)
        slot.snack_pile = SnackPile(
            self.snack.to_domain() if self.snack else Snack.empty(), self.quantity, self.price)
        slot.id = self.id
        return slot


class SnackMachineOrm(Base):
    __tablename__ = 'snack_machines'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Cent: Mapped[int] = mapped_column(default=0)
    TenCent: Mapped[int] = mapped_column(default=0)
    Quarter: Mapped[int] = mapped_column(default=0)
    Dollar: Mapped[int] = mapped_column(default=0)
    FiveDollar: Mapped[int] = mapped_column(default=0)
    TwentyDollar: Mapped[int] = mapped_column(default=0)
    slots: Mapped[list[SlotOrm]] = relationship(
        'SlotOrm', cascade='all, delete-orphan')

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

    def to_domain(self) -> SnackMachine:
        wallet = Wallet(*self.money_inside)

        snack_machine = SnackMachine()
        snack_machine.load_money(wallet)
        snack_machine.id = self.id
        snack_machine.slots = [slot.to_domain() for slot in self.slots]
        return snack_machine


class SqlAlchemySnackMachineRepository(SnackMachineRepository):

    def __init__(self, session: Session):
        self.session = session

    def create(self):
        snack_machine = SnackMachineOrm()
        self.session.add(snack_machine)

        snack_machine.slots = [
            SlotOrm(position=1, snack_machine_id=snack_machine.id),
            SlotOrm(position=2, snack_machine_id=snack_machine.id),
            SlotOrm(position=3, snack_machine_id=snack_machine.id),
        ]
        self.session.commit()

    def find_by_id(self, id):
        snack_machines = self.session.query(
            SnackMachineOrm).filter_by(id=id).all()

        return next((s.to_domain() for s in snack_machines), None)

    def save(self, snack_machine: SnackMachine):
        stmt = select(SnackMachineOrm).where(
            SnackMachineOrm.id == snack_machine.id)
        snack_machine_orm = self.session.scalars(stmt).one()

        coins_and_notes = snack_machine.count_coins_and_notes()
        for key, count in coins_and_notes.items():
            setattr(snack_machine_orm, key, count)

        snack_machine_orm.slots = [
            SlotOrm(
                id=slot.id,
                position=slot.position,
                snack_id=slot.snack_pile.snack.id,
                quantity=slot.snack_pile.quantity,
                price=slot.snack_pile.price,
                snack_machine_id=snack_machine_orm.id,
            )
            for slot in snack_machine.slots
        ]

        self.session.commit()
