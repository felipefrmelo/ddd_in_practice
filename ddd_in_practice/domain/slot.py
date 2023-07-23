

from ddd_in_practice.domain.snack_pile import SnackPile


class Slot:

    id: int

    snack_pile: SnackPile

    def __init__(self, position: int):
        self.position = position
        self.snack_pile = SnackPile.empty()

    @property
    def snack_name(self):
        return self.snack_pile.snack.name

    @property
    def snack_price(self):
        return self.snack_pile.price

    def __str__(self):
        return f"[{self.position}] {self.snack_pile.snack.name} [{self.snack_pile.snack.id}]"

    def __repr__(self):
        return str(self)
