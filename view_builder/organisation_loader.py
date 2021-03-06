import csv
from view_builder.model.table import Organisation, Entity
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import date


def load_organisations(path):
    engine = create_engine("sqlite+pysqlite:///{}".format(str(path)))
    with open("var/cache/organisation.csv", "r", newline="") as f, Session(
        engine
    ) as session:
        writer = csv.DictReader(f)
        counter = 1
        for row in writer:
            org = Organisation(
                entity_rel=Entity(
                    entity=counter, typology="organisation", dataset="organisation"
                ),
                organisation=row["organisation"],
                name=row["name"],
            )
            if row.get("entry-date", ""):
                org.entry_date = date.fromisoformat(row["entry-date"])
            if row.get("start-date", ""):
                org.start_date = date.fromisoformat(row["start-date"])
            if row.get("end-date", ""):
                org.end_date = date.fromisoformat(row["end-date"])
            session.add(org)
            counter = counter + 1
        session.commit()


if __name__ == "__main__":
    load_organisations(path="view_model.db")
