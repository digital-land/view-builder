all:
	lint test

test:
	python -m pytest tests/

init:
	pip install -r requirements.txt
	pip install -e .

lint: black-check flake8

black-check:
	black --check .

flake8:
	flake8 .
