from datetime import date
from view_builder.model.table import Slug, Category


class DatasetModelFactory:
    def __init__(self):
        self._dataset_models = {}

    def register_dataset_model(self, model_class):
        self._dataset_models[model_class.dataset_name] = model_class

    def get_dataset_model(self, name, data: dict):
        model_class = self._dataset_models.get(name)
        if not model_class:
            raise ValueError("No matching dataset model found")
        return model_class(data)


factory = DatasetModelFactory()


class DatasetModel:
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


class DeveloperAgreementTypeModel(DatasetModel):

    dataset_name = "developer-agreement-type"

    def __init__(self, data: dict):
        DatasetModel.__init__(self, data)
        self.slug = {
            key: data[key] for key in Slug.__table__.columns.keys() if key in data
        }
        self.category = {
            key: data[key] for key in Category.__table__.columns.keys() if key in data
        }
        if "reference" not in self.category and "developer-agreement-type" in data:
            self.category["reference"] = data["developer-agreement-type"]
        # Add check for presence of key field ?

    def to_orm(self):
        slug = Slug(**self.slug)
        category = Category(**self.category, slug=slug)
        return [category]


factory.register_dataset_model(DeveloperAgreementTypeModel)
