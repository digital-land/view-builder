include makerules/makerules.mk

CACHE_DIR := var/cache/
VIEW_MODEL_DB := view_model.db

all:: lint test

test:
	python -m pytest tests/

# init:
# 	pip install -r requirements.txt
# 	pip install -e .

lint: black-check flake8

black-check:
	black --check .

flake8:
	flake8 .

clobber::
	rm $(VIEW_MODEL_DB)

$(VIEW_MODEL_DB):
	view_builder create $(VIEW_MODEL_DB)

build: $(CACHE_DIR)organisation.csv $(VIEW_MODEL_DB)
	python view_builder/organisation_loader.py
	view_builder build local-authority-district ../datasette-builder/data/local-authority-district.sqlite3 $(VIEW_MODEL_DB)
	view_builder build development-policy-category ../datasette-builder/data/development-policy-category.sqlite3 $(VIEW_MODEL_DB)
	view_builder build development-plan-type ../datasette-builder/data/development-plan-type.sqlite3 $(VIEW_MODEL_DB)
	view_builder build --allow-broken-relationships development-policy ../datasette-builder/data/development-policy.sqlite3 $(VIEW_MODEL_DB)
	view_builder build --allow-broken-relationships development-plan-document ../datasette-builder/data/development-plan-document.sqlite3 $(VIEW_MODEL_DB)

server:
	datasette -m metadata.json view_model.db

$(CACHE_DIR)organisation.csv:
	curl -qs "https://raw.githubusercontent.com/digital-land/organisation-dataset/main/collection/organisation.csv" > $(CACHE_DIR)organisation.csv
