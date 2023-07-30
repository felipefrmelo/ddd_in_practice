# type: ignore
from fastapi.testclient import TestClient
from atm.domain.atm import Atm
from management.entrypoint import app, get_head_office, get_repo_head_office
from management.domain.head_office import HeadOffice
from shared_kernel.domain.money import Dollar
from shared_kernel.domain.wallet import Wallet
from snack_machine.domain.snack_machine import SnackMachine
from snack_machine.entrypoint import get_snack_machines, unload_cash
from atm.entrypoint import load_cash, WalletRequest, get_atms

client = TestClient(app)


snack_machine = SnackMachine()
snack_machine.load_money(Wallet(Dollar(10)))
snack_machine.id = 1

atm = Atm()
atm.id = 1


def override_get_atms():
    return [atm]


def override_load_cash(atm_id: int, wallet: WalletRequest):

    domain_wallet = wallet.to_domain()
    atm.load_money(domain_wallet)
    return domain_wallet


def override_get_snack_machines():
    return [snack_machine]


def override_unload_cash(snack_machine_id: int):
    return snack_machine.unload_cash()


def override_get_head_office():
    return HeadOffice()


class FakeRepo:
    def get(self):
        return HeadOffice()

    def save(self, head_office):
        pass


def override_get_repo_head_office():
    return FakeRepo()


app.dependency_overrides[get_repo_head_office] = override_get_repo_head_office
app.dependency_overrides[get_head_office] = override_get_head_office
app.dependency_overrides[get_snack_machines] = override_get_snack_machines
app.dependency_overrides[unload_cash] = override_unload_cash
app.dependency_overrides[get_atms] = override_get_atms
app.dependency_overrides[load_cash] = override_load_cash


def test_management_page():
    response = client.get("/")

    assert response.status_code == 200
    assert response.template.name == 'index.html'
    assert "request" in response.context


def test_should_view_head_office():
    response = client.get("/")

    assert "balance" in response.context
    assert "cash" in response.context


def test_should_list_snack_machines():
    response = client.get("/")

    assert len(response.context["snack_machines"]) == 1

    sm = response.context["snack_machines"][0]
    assert sm.id == 1
    assert sm.money_inside == 10


def test_should_unload_cash_from_snack_machine():
    response = client.post("/snack_machine/1/unload_cash")

    assert response.status_code == 200
    assert response.context["cash"] == 10
    assert response.context["balance"] == 0
    sm = response.context["snack_machines"][0]
    assert sm.money_inside == 0


def test_should_load_cash_to_atm():
    response = client.post("/atm/1/load_cash", json={"one_dollar_count": 10})

    assert response.status_code == 200
    assert response.context["cash"] == 0
    assert response.context["balance"] == 0
    atm = response.context["atms"][0]

    assert atm.money_inside == 10
