class Snack:

    @staticmethod
    def empty():
        return Snack(0, "EMPTY")

    def __init__(self, ID: int, name: str):
        self.name = name
        self.id = ID


Chocolate = Snack(1, "Chocolate")
Soda = Snack(2, "Soda")
Gum = Snack(3, "Gum")
