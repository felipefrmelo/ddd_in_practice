test:
	poetry run pytest --cov-report term-missing  --cov snack_machine --cov atm

run-snak-machine:
	poetry run python snack_machine/ui/view.py

run-atm:
	poetry run python atm/ui/view.py
