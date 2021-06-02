include makerules/makerules.mk

CACHE_DIR := var/cache/
VIEW_MODEL_DB := view_model.db

all:: build

DATASETS=\
	$(CACHE_DIR)document-type.sqlite3\
	$(CACHE_DIR)development-plan-type.sqlite3\
	$(CACHE_DIR)development-policy-category.sqlite3\
	$(CACHE_DIR)planning-permission-status.sqlite3\
	$(CACHE_DIR)planning-permission-type.sqlite3\
	$(CACHE_DIR)ownership-status.sqlite3\
	$(CACHE_DIR)site-category.sqlite3\
	\
	$(CACHE_DIR)local-authority-district.sqlite3\
	$(CACHE_DIR)parish.sqlite3\
	\
	$(CACHE_DIR)ancient-woodland.sqlite3\
	$(CACHE_DIR)area-of-outstanding-natural-beauty.sqlite3\
	$(CACHE_DIR)brownfield-land.sqlite3\
	$(CACHE_DIR)conservation-area.sqlite3\
	$(CACHE_DIR)development-policy.sqlite3\
	$(CACHE_DIR)development-plan-document.sqlite3\
	$(CACHE_DIR)document.sqlite3\
	$(CACHE_DIR)green-belt.sqlite3\
	$(CACHE_DIR)heritage-coast.sqlite3\
	$(CACHE_DIR)historic-england/battlefield.sqlite3\
	$(CACHE_DIR)historic-england/building-preservation-notice.sqlite3\
	$(CACHE_DIR)historic-england/certificate-of-immunity.sqlite3\
	$(CACHE_DIR)historic-england/heritage-at-risk.sqlite3\
	$(CACHE_DIR)historic-england/listed-building.sqlite3\
	$(CACHE_DIR)historic-england/park-and-garden.sqlite3\
	$(CACHE_DIR)historic-england/protected-wreck-site.sqlite3\
	$(CACHE_DIR)historic-england/scheduled-monument.sqlite3\
	$(CACHE_DIR)historic-england/world-heritage-site.sqlite3\
	$(CACHE_DIR)special-area-of-conservation.sqlite3

test:
	python -m pytest tests/

lint: black-check flake8

black-check:
	black --check  . --exclude '/(src|\.venv/)'

flake8:
	flake8 .

clobber::
	rm $(VIEW_MODEL_DB)

build:: $(VIEW_MODEL_DB)

$(VIEW_MODEL_DB): $(CACHE_DIR)organisation.csv $(DATASETS)
	@rm -f $@
	view_builder create $@
	view_builder load_organisations $@
	# this should be in shell or python ..
	for f in $(DATASETS) ; do echo $$f ; view_builder build --allow-broken-relationships $$(basename $$f .sqlite3) $$f $@ ; done

server:
	datasette -m metadata.json view_model.db

$(CACHE_DIR)organisation.csv:
	@mkdir -p $(CACHE_DIR)
	curl -qfsL "$(SOURCE_URL)organisation-dataset/main/collection/organisation.csv" > $(CACHE_DIR)organisation.csv

#
#  download cached copy of dataset
#
$(CACHE_DIR)%.sqlite3:
	@mkdir -p $(CACHE_DIR)
	curl -qfsL $(call dataset_url,$(basename $(notdir $@)),$(basename $(notdir $@))) > $@

#  the collection should come from the specification ..
$(CACHE_DIR)historic-england/%.sqlite3:
	@mkdir -p $(CACHE_DIR)/historic-england
	curl -qfsL $(call dataset_url,$(basename $(notdir $@)),historic-england) > $@
