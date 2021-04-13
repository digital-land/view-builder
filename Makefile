test:
	python -m pytest tests/

init:
	pip install -r requirements.txt
	pip install -e .
