test:
	poetry run pytest --cov-report term-missing  --cov snack_machine --cov atm

run-snak-machine:
	poetry run python snack_machine/ui/view.py

run-atm:
	poetry run python atm/ui/view.py

run-rabbitmq:
	docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
