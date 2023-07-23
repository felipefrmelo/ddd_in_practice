

from ddd_in_practice.domain.snack import Snack


class SnackPile:
    def __init__(self, snack: Snack, quantity: int, price: float):
        self.snack = snack
        self.quantity = quantity
        self.price = price

    @staticmethod
    def empty():
        return SnackPile(Snack.empty(), 0, 0)

    def subtract_one(self):
        return SnackPile(self.snack, self.quantity - 1, self.price)
