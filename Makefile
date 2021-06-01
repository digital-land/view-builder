include makerules/makerules.mk

CACHE_DIR := var/cache/
VIEW_MODEL_DB := view_model.db

all:: lint test

test:
	python -m pytest tests/

lint: black-check flake8

black-check:
	black --check  . --exclude '/(src|\.venv/)'

flake8:
	flake8 .

clobber::
	rm $(VIEW_MODEL_DB)

$(VIEW_MODEL_DB):
	view_builder create $(VIEW_MODEL_DB)

build: $(CACHE_DIR)organisation.csv $(VIEW_MODEL_DB)
	view_builder load_organisations $(VIEW_MODEL_DB)
	view_builder build ancient-woodland data/ancient-woodland.sqlite3 $(VIEW_MODEL_DB)
	view_builder build heritage-coast data/heritage-coast.sqlite3 $(VIEW_MODEL_DB)
	view_builder build area-of-outstanding-natural-beauty data/area-of-outstanding-natural-beauty.sqlite3 $(VIEW_MODEL_DB)
	view_builder build local-authority-district data/local-authority-district.sqlite3 $(VIEW_MODEL_DB)
	view_builder build parish data/parish.sqlite3 $(VIEW_MODEL_DB)
	view_builder build conservation-area data/conservation-area.sqlite3 $(VIEW_MODEL_DB)
	view_builder build development-policy-category data/development-policy-category.sqlite3 $(VIEW_MODEL_DB)
	view_builder build development-plan-type data/development-plan-type.sqlite3 $(VIEW_MODEL_DB)
	view_builder build ownership-status data/ownership-status.sqlite3 $(VIEW_MODEL_DB)
	view_builder build planning-permission-status data/planning-permission-status.sqlite3 $(VIEW_MODEL_DB)
	view_builder build planning-permission-type data/planning-permission-type.sqlite3 $(VIEW_MODEL_DB)
	view_builder build site-category data/site-category.sqlite3 $(VIEW_MODEL_DB)
	view_builder build document-type data/document-type.sqlite3 $(VIEW_MODEL_DB)
	view_builder build --allow-broken-relationships development-policy data/development-policy.sqlite3 $(VIEW_MODEL_DB)
	view_builder build --allow-broken-relationships development-plan-document data/development-plan-document.sqlite3 $(VIEW_MODEL_DB)
	view_builder build --allow-broken-relationships document data/document.sqlite3 $(VIEW_MODEL_DB)
	view_builder build --allow-broken-relationships brownfield-land data/brownfield-land.sqlite3 $(VIEW_MODEL_DB)

server:
	datasette -m metadata.json view_model.db

$(CACHE_DIR)organisation.csv:
	mkdir -p $(CACHE_DIR)
	curl -qs "https://raw.githubusercontent.com/digital-land/organisation-dataset/main/collection/organisation.csv" > $(CACHE_DIR)organisation.csv
