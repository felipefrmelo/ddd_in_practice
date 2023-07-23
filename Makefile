
test:
	poetry run pytest --cov-report term-missing  --cov snack_machine


run:
	poetry run python snack_machine/ui/view.py

