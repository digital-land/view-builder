import logging

from sqlalchemy.orm import Session


class ViewBuilder:
    def __init__(self, engine, item_mapper, log=False):
        self._engine = engine
        self._item_mapper = item_mapper
        if log:
            logging.basicConfig()
            logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    def init_model(self, metadata):
        metadata.create_all(self._engine)

    def build_model(self, dataset_name, reader):
        with Session(self._engine) as session:
            for item in reader:
                orm_objects = self._item_mapper(dataset_name, item)
                for obj in orm_objects:
                    session.add(obj)

            session.commit()
