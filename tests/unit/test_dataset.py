from view_builder.model.dataset import DatasetModel, DeveloperAgreementTypeModel, DatasetModelFactory
import datetime
import pytest


class DummyModel:
    def __init__(self, *args):
        pass


def test_dataset_model_factory_register_and_get():
    test_factory = DatasetModelFactory()
    test_factory.register_dataset_model("test_class", DummyModel)
    output = test_factory.get_dataset_model("test_class", {"check": True})

    assert(isinstance(output, DummyModel))


def test_dataset_model_factory_no_class():
    test_factory = DatasetModelFactory()
    with pytest.raises(ValueError, match="^No matching dataset model found$"):
        test_factory.get_dataset_model("test_class", {"check": True})


def test_dataset_model_no_slug():
    test_data = {
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05"
    }

    with pytest.raises(ValueError, match="^Data missing slug field$"):
        DatasetModel(test_data)


def test_dataset_model_no_entry_date():
    test_data = {
        "start-date": "2020-10-05",
        "slug": "dataset/AAA"
    }

    with pytest.raises(ValueError, match="^Entry missing entry-date$"):
        DatasetModel(test_data)


def test_dataset_model_future_entry_date():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    test_data = {
        "entry-date": tomorrow.isoformat(),
        "start-date": "2020-10-05",
        "slug": "dataset/AAA"
    }

    with pytest.raises(ValueError, match="^entry-date cannot be in the future$"):
        DatasetModel(test_data)


def test_development_agreement_type_model():
    test_data = {
        "developer-agreement-type": "AAA",
        "name": "BBB",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "slug": "developer-agreement-type/AAA",
        "extra_field": "CCC"
    }

    developer_agreement_type_orm = DeveloperAgreementTypeModel(test_data)
    orm_obj = developer_agreement_type_orm.to_orm()
    assert(orm_obj.reference == test_data["developer-agreement-type"])
    assert(orm_obj.name == test_data["name"])
    assert(orm_obj.slug.slug == test_data["slug"])
