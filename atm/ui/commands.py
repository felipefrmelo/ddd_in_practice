
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class Command:
    pass


@dataclass(unsafe_hash=True)
class TakeMoney(Command):
    value: float
