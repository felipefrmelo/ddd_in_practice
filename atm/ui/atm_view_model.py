from atm.domain.atm import Atm
from atm.infra.repository import AtmRepository
import atm.ui.commands as Commands
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class AtmViewModel:

    def __init__(self, atm: Atm, repository: AtmRepository):
        self.atm = atm
        self.repository = repository

    def take_money(self, command: Commands.TakeMoney):
        self.atm.take_money(command.value)
        self.repository.save(self.atm)

    @property
    def count_coins_and_notes(self):
        return self.atm.count_coins_and_notes()

    def handle(self, command: Commands.Command):
        command_type = type(command)
        if command_type not in self.handled_commands:
            raise Exception(f"Command {command_type} not handled")

        for handler in self.handled_commands[command_type]:
            handler(command)

    @property
    def handled_commands(self) -> dict:
        return {
            Commands.TakeMoney: [self.take_money],
        }

    @property
    def money_charged(self):
        return self.formatCurrency(self.atm.money_charged)

    @property
    def money_inside(self):
        return self.formatCurrency(self.atm.money_inside)

    def formatCurrency(self, value):
        return locale.currency(value, grouping=True)
