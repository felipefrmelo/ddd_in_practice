
test:
	poetry run pytest --cov-report term-missing  --cov ddd_in_practice


run:
	poetry run python ddd_in_practice/ui/view.py

