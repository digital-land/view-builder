from datetime import date
from view_builder.model.model import Slug, Category


class DatasetORM:
    def __init__(self, data: dict):
        self.data = data

        if not data.get("slug", None):
            raise ValueError("Data missing slug field")

        if not data.get("entry-date", None):
            raise ValueError("Entry missing entry-date")

        self.data["entry_date"] = date.fromisoformat(self.data.pop("entry-date"))
        if "start-date" in self.data:
            self.data["start_date"] = date.fromisoformat(self.data.pop("start-date"))
        if "end-date" in self.data:
            self.data["end_date"] = date.fromisoformat(self.data.pop("end-date"))

        if self.data["entry_date"] > date.today():
            raise ValueError("entry-date cannot be in the future")


class DeveloperAgreementTypeORM(DatasetORM):
    def __init__(self, data: dict):
        super().__init__(data)
        self.slug = {key: data[key] for key in Slug.__table__.columns.keys() if key in data}
        self.category = {key: data[key] for key in Category.__table__.columns.keys() if key in data}
        self.category["reference"] = data["developer-agreement-type"]
        # Add check for presence of key field ?

    def to_orm(self):
        slug = Slug(**self.slug)
        category = Category(**self.category, slug=slug)
        return category



