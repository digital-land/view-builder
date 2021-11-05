include makerules/makerules.mk

BUILD_TAG_FACT := digitalland/fact
BUILD_TAG_TILE := digitalland/tile
CACHE_DIR := var/cache/
VIEW_MODEL_DB := var/cache/view_model.sqlite3

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
	$(CACHE_DIR)brownfield-site.sqlite3\
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
	$(CACHE_DIR)special-area-of-conservation.sqlite3\
	$(CACHE_DIR)ramsar.sqlite3\
    	$(CACHE_DIR)site-of-special-scientific-interest.sqlite3\
	$(CACHE_DIR)open-space.sqlite3

ifeq ($(SHARED_DIR),)
SHARED_DIR=tmp/
endif

ifeq ($(SHARED_VOL),)
SHARED_VOL=$(shell pwd)/$(SHARED_DIR)
endif

all:: collect build postprocess generate-tiles

collect: $(CACHE_DIR)organisation.csv $(DATASETS)

test:
	python -m pytest tests/

lint: black-check flake8

black-check:
	black --check  . --exclude '/(src|\.venv/)'

flake8:
	flake8 .

clobber::
	rm -rf $(VIEW_MODEL_DB)
	rm -rf $(CACHE_DIR)*

docker-check:
ifeq (, $(shell which docker))
	$(error "No docker in $(PATH), consider doing apt-get install docker OR brew install --cask docker")
endif

tippecanoe-check:
ifeq (, $(shell which tippecanoe))
	git clone https://github.com/mapbox/tippecanoe.git
	cd tippecanoe
	make -j
	make install
endif


build: $(VIEW_MODEL_DB)

$(VIEW_MODEL_DB):
	@rm -f $@
	view_builder create $@
	view_builder load_organisations $@
	# this should be in shell or python ..
	for f in $(DATASETS) ; do echo $$f ; view_builder build --allow-broken-relationships $$(basename $$f .sqlite3) $$f $@ ; done


postprocess:
	@mkdir -p $(SHARED_DIR)
	cp $(VIEW_MODEL_DB) $(SHARED_DIR)
	docker build -t sqlite3-spatialite -f SqliteDockerfile .
	docker run -t --mount src=$(SHARED_VOL),target=/tmp,type=bind sqlite3-spatialite -init ./post_process.sql -bail -echo  /tmp/view_model.sqlite3
	cp $(SHARED_DIR)view_model.sqlite3 $(CACHE_DIR)

generate-tiles: tippecanoe-check
	view_builder build-tiles $(VIEW_MODEL_DB) $(CACHE_DIR)
	sed -i '1s/^/{"type":"FeatureCollection","features":[/' $(CACHE_DIR)geometry.txt
	echo ']}' >> $(CACHE_DIR)geometry.txt
	tr '\n' , < $(CACHE_DIR)geometry.txt > $(CACHE_DIR)geometry.geojson
	tippecanoe -z15 -Z4 -r1 --no-feature-limit --no-tile-size-limit -o $(CACHE_DIR)dataset_tiles.mbtiles $(CACHE_DIR)geometry.geojson

push-dataset:
	aws s3 sync $(CACHE_DIR) s3://digital-land-view-model --exclude='*' --include='view_model.sqlite3' --include='*.mbtiles'

aws-build::
	aws batch submit-job --job-name view_model-$(shell date '+%Y-%m-%d-%H-%M-%S') --job-queue dl-batch-queue --job-definition dl-batch-def --container-overrides '{"environment": [{"name":"BATCH_FILE_S3_URL","value":"s3://dl-batch-scripts/builder_run.sh"}, {"name" : "BUILDER_REPO","value" : "view-builder"}]}'

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
