import click
from digital_land.model.entity import Entity
from digital_land.repository.entry_repository import EntryRepository
from view_builder.builder import ViewBuilder
from view_builder.index import index_view_model
from view_builder.model.dataset import factory as dataset_model_factory

from view_builder.model.table import Base
from sqlalchemy import create_engine
from view_builder.organisation_loader import (
    load_organisations as load_organisations_from_file,
)


@click.group()
def cli():
    pass


@click.command("create", short_help="create the view model tables")
@click.argument("output_path", type=click.Path(exists=False))
def create(output_path):
    engine = create_engine("sqlite+pysqlite:///{}".format(output_path))
    builder = ViewBuilder(
        engine=engine,
        item_mapper=None,
    )
    builder.init_model(Base.metadata)


cli.add_command(create)


@click.command("build", short_help="build the view model for a single dataset")
@click.option("-d", "--debug/--no-debug", default=False)
@click.option(
    "-a", "--allow-broken-relationships/--no-broken-relationships", default=False
)
@click.argument("dataset_name", type=click.STRING)
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=False))
def build(debug, allow_broken_relationships, dataset_name, input_path, output_path):
    entry_repo = EntryRepository(input_path)
    entities = entry_repo.list_entities()
    reader = (
        Entity(entry_repo.find_by_entity(entity)).snapshot() for entity in entities
    )
    engine = create_engine("sqlite+pysqlite:///{}".format(output_path))
    builder = ViewBuilder(
        engine=engine,
        item_mapper=lambda name, session, item: dataset_model_factory.get_dataset_model(
            name, session, item
        ).to_orm(allow_broken_relationships),
        log=debug,
    )
    builder.init_model(Base.metadata)
    builder.build_model(dataset_name, reader, len(entities))


cli.add_command(build)


@click.command("index", short_help="add indexes to view model DB")
@click.argument("input_path", type=click.Path(exists=True))
def index(input_path):
    index_view_model(input_path)


cli.add_command(index)


# Temporary command to load organisations from organisation.csv
@click.command("load_organisations", short_help="load organisations into view model")
@click.argument("output_path", type=click.Path(exists=False))
def load_organisations(output_path):
    load_organisations_from_file(output_path)


cli.add_command(load_organisations)
