import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from atm.domain.atm import Atm
from management.domain.head_office import HeadOffice, SessionLocal, SqlAlchemyHeadOfficeRepository
from snack_machine.domain.snack_machine import SnackMachine
from snack_machine.entrypoint import get_snack_machines, unload_cash
from atm.entrypoint import get_atms, load_cash

app = FastAPI()


dir_path = os.path.dirname(os.path.realpath(__file__))

app.mount(
    "/static", StaticFiles(directory=f"{dir_path}/static"), name="static")


templates = Jinja2Templates(directory=f"{dir_path}/templates")


def get_repo_head_office():
    session = SessionLocal()
    repo = SqlAlchemyHeadOfficeRepository(session)
    return repo


def get_head_office(repo=Depends(get_repo_head_office)):
    head_office = repo.get()
    return head_office


@app.get("/", response_class=HTMLResponse)
async def index(request: Request,
                snack_machines: list[SnackMachine] = Depends(
                    get_snack_machines),
                atms: list[Atm] = Depends(get_atms),
                head_office: HeadOffice = Depends(get_head_office),
                ):

    return templates.TemplateResponse("index.html", {"request": request, "balance": head_office.balance, "cash": head_office.cash, 'snack_machines': snack_machines, 'atms': atms})


@app.post("/snack_machine/{snack_machine_id}/unload_cash")
async def unload_cash_end(request: Request,
                          cash=Depends(unload_cash),
                          snack_machines: list[SnackMachine] = Depends(
                              get_snack_machines),
                          atms: list[Atm] = Depends(get_atms),
                          head_office: HeadOffice = Depends(get_head_office),
                          repo=Depends(get_repo_head_office)
                          ):

    print(cash)

    head_office.unload_cash(cash)
    repo.save(head_office)

    return templates.TemplateResponse("index.html", {"request": request, "balance": head_office.balance, "cash": head_office.cash, 'snack_machines': snack_machines, 'atms': atms})


@app.post("/atm/{atm_id}/load_cash")
async def load_cash_end(request: Request,
                        cash=Depends(load_cash),
                        atms: list[Atm] = Depends(get_atms),
                        snack_machines: list[SnackMachine] = Depends(
                            get_snack_machines),
                        head_office: HeadOffice = Depends(get_head_office),
                        repo=Depends(get_repo_head_office)
                        ):

    head_office.load_cash_to_atm()
    repo.save(head_office)

    return templates.TemplateResponse("index.html", {"request": request, "balance": head_office.balance, "cash": head_office.cash, 'atms': atms, 'snack_machines': snack_machines})

# how i run this
# uvicorn management.entrypoint:app --reload
