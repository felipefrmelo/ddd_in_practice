from ddd_in_practice.domain.snack_machine import SnackMachine
from ddd_in_practice.infra.repository import SnackMachineRepository
from ddd_in_practice.ui.commands import InsertMoney
import ddd_in_practice.ui.commands as Commands
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class SnackMachineViewModel:

    def __init__(self, snack_machine: SnackMachine, repository: SnackMachineRepository):
        self.snack_machine = snack_machine
        self.repository = repository

    def insert_money(self, command: InsertMoney):
        self.snack_machine.insert_money(command.value)

    def buy_snack(self, command: Commands.BuySnack):
        self.snack_machine.buy_snack(command.position)
        self.repository.save(self.snack_machine)

    def return_money(self):
        self.snack_machine.return_money()

    @property
    def slots(self):
        return self.snack_machine.slots

    @property
    def count_coins_and_notes(self):
        return self.snack_machine.count_coins_and_notes()

    def handle(self, command: Commands.Command):
        command_type = type(command)
        if command_type not in self.handled_commands:
            raise Exception(f"Command {command_type} not handled")

        for handler in self.handled_commands[command_type]:
            handler(command)

    @property
    def handled_commands(self):
        return {
            Commands.BuySnack: [self.buy_snack],
            Commands.ReturnMoney: [lambda _: self.return_money()],
            Commands.InsertCent: [self.insert_money],
            Commands.InsertTenCent: [self.insert_money],
            Commands.InsertQuarter: [self.insert_money],
            Commands.InsertDollar: [self.insert_money],
            Commands.InsertFiveDollar: [self.insert_money],
            Commands.InsertTwentyDollar: [self.insert_money],
        }

    @property
    def money_inserted(self):
        return self.formatCurrency(self.snack_machine.money_in_transaction)

    @property
    def money_inside(self):
        return self.formatCurrency(self.snack_machine.money_inside)

    def formatCurrency(self, value):
        return locale.currency(value, grouping=True)
