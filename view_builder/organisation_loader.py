import csv
from view_builder.model.table import Organisation
from view_builder.model.table import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import date

engine = create_engine("sqlite+pysqlite:///{}".format("view_model.db"))
with open("var/cache/organisation.csv", "r", newline="") as f, Session(engine) as session:
    writer = csv.DictReader(f)
    for row in writer:
        org = Organisation(
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
    session.commit()
