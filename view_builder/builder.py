import logging

from sqlalchemy.orm import Session
from tqdm import tqdm


class ViewBuilder:
    def __init__(self, engine, item_mapper, log=False):
        self._engine = engine
        self._item_mapper = item_mapper
        if log:
            logging.basicConfig()
            logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    def init_model(self, metadata):
        metadata.create_all(self._engine)

    def build_model(self, dataset_name, reader, total=None):
        with Session(self._engine) as session:
            with tqdm(total=total) as pbar:
                for item in reader:
                    orm_objects = self._item_mapper(dataset_name, session, item)
                    for obj in orm_objects:
                        session.add(obj)
                    pbar.update(1)

            session.commit()
